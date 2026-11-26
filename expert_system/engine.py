"""Forward and backward chaining over the versioned JSON knowledge base."""

import json
from pathlib import Path
from typing import Any

from .fact_store import FactStore
from .models import BackwardQueryResult, ConclusionResult, InferenceResult


class KnowledgeBaseError(ValueError):
    """Raised when the knowledge base is incomplete or inconsistent."""


class InferenceEngine:
    def __init__(self, knowledge_base_dir: str | Path):
        root = Path(knowledge_base_dir)
        self.facts = self._load(root / "facts.json")
        self.rules_data = self._load(root / "rules.json")
        self.conclusions_data = self._load(root / "conclusions.json")
        self.recommendations_data = self._load(root / "recommendations.json")
        self.categories_data = self._load(root / "categories.json")
        self.fact_definitions = {item["id"]: item for item in self.facts["facts"]}
        self.conclusion_definitions = {item["id"]: item for item in self.conclusions_data["conclusions"]}
        self.recommendation_definitions = {item["id"]: item for item in self.recommendations_data["recommendations"]}
        self.category_ids = {item["id"] for item in self.categories_data["categories"]}
        self.rules = sorted(self.rules_data["rules"], key=lambda item: (-item["priority"], item["id"]))
        self._validate_references()

    @staticmethod
    def _load(path: Path) -> dict[str, Any]:
        try:
            with path.open("r", encoding="utf-8") as handle:
                return json.load(handle)
        except FileNotFoundError as exc:
            raise KnowledgeBaseError(f"Knowledge-base file not found: {path}") from exc
        except json.JSONDecodeError as exc:
            raise KnowledgeBaseError(f"Invalid JSON in {path}: {exc}") from exc

    def new_fact_store(self) -> FactStore:
        return FactStore(self.facts)

    def _validate_references(self) -> None:
        for rule in self.rules:
            if rule["category"] not in self.category_ids:
                raise KnowledgeBaseError(f"Unknown category in {rule['id']}: {rule['category']}")
            if rule["conclusion"] not in self.conclusion_definitions:
                raise KnowledgeBaseError(f"Unknown conclusion in {rule['id']}: {rule['conclusion']}")
            if rule.get("requires_conclusion") and rule["requires_conclusion"] not in self.conclusion_definitions:
                raise KnowledgeBaseError(f"Unknown prerequisite conclusion in {rule['id']}")
            for condition in rule["conditions"]:
                if condition["fact"] not in self.fact_definitions:
                    raise KnowledgeBaseError(f"Unknown fact in {rule['id']}: {condition['fact']}")
                self._validate_operator_type(rule["id"], condition)
            for recommendation_id in rule.get("recommendations", []):
                if recommendation_id not in self.recommendation_definitions:
                    raise KnowledgeBaseError(f"Unknown recommendation in {rule['id']}: {recommendation_id}")

    def _validate_operator_type(self, rule_id: str, condition: dict[str, Any]) -> None:
        fact_type = self.fact_definitions[condition["fact"]]["type"]
        operator = condition["operator"]
        numeric_ops = {"gt", "gte", "lt", "lte"}
        if operator in numeric_ops and fact_type not in {"number", "integer"}:
            raise KnowledgeBaseError(f"{rule_id}: {operator} requires a numeric fact")
        if operator == "in" and not isinstance(condition["value"], list):
            raise KnowledgeBaseError(f"{rule_id}: 'in' requires a list value")

    def _evaluate_condition(self, condition: dict[str, Any], store: FactStore) -> dict[str, Any]:
        fact_id = condition["fact"]
        evidence = store.evidence(fact_id)
        status = evidence["status"]
        if status != "confirmed":
            return {
                "fact": fact_id,
                "status": status,
                "matched": False,
                "expected": {"operator": condition["operator"], "value": condition["value"]},
                "observed": None,
            }
        actual = evidence["value"]
        expected = condition["value"]
        operator = condition["operator"]
        try:
            matched = {
                "eq": lambda: actual == expected,
                "neq": lambda: actual != expected,
                "gt": lambda: actual > expected,
                "gte": lambda: actual >= expected,
                "lt": lambda: actual < expected,
                "lte": lambda: actual <= expected,
                "in": lambda: actual in expected,
            }[operator]()
        except (TypeError, KeyError) as exc:
            raise KnowledgeBaseError(f"Invalid comparison for {fact_id}: {operator}") from exc
        return {
            "fact": fact_id,
            "status": "confirmed",
            "matched": bool(matched),
            "expected": {"operator": operator, "value": expected},
            "observed": actual,
        }

    def _calculate(self, rule: dict[str, Any], store: FactStore, conclusions: dict[str, ConclusionResult]) -> Any:
        formula = rule.get("formula")
        if not formula:
            return True
        rule_id = rule["id"]
        if rule_id == "R-ENERGY-001":
            power = store.evidence("appliance.rated_power_w")["value"]
            quantity = store.evidence("appliance.quantity")["value"]
            hours = store.evidence("usage.hours_per_day")["value"]
            days = store.evidence("usage.days_per_month")["value"]
            return power * quantity * hours * days / 1000.0
        if rule_id == "R-COST-001":
            energy = conclusions.get("energy.monthly_kwh_estimate_available")
            if energy is None:
                raise KnowledgeBaseError("Cost rule fired without a monthly energy estimate")
            rate = store.evidence("tariff.price_per_kwh")["value"]
            return energy.value * rate
        if rule_id == "R-STANDBY-001":
            power = store.evidence("appliance.standby_power_w")["value"]
            quantity = store.evidence("appliance.quantity")["value"]
            hours = store.evidence("usage.standby_hours_per_day")["value"]
            days = store.evidence("usage.days_per_month")["value"]
            return power * quantity * hours * days / 1000.0
        raise KnowledgeBaseError(f"No allow-listed calculation is registered for {rule_id}")

    def _recommendations(self, rule: dict[str, Any]) -> list[dict[str, Any]]:
        return [self.recommendation_definitions[item] for item in rule.get("recommendations", [])]

    def forward_chain(self, store: FactStore, *, max_iterations: int = 100) -> InferenceResult:
        conclusions: dict[str, ConclusionResult] = {}
        fired_rules: list[str] = []
        trace: list[dict[str, Any]] = []
        conflicts: list[dict[str, Any]] = []
        if max_iterations < 1:
            raise ValueError("max_iterations must be at least 1")

        for iteration in range(1, max_iterations + 1):
            newly_fired = False
            for rule in self.rules:
                if rule["id"] in fired_rules:
                    continue
                condition_results = [self._evaluate_condition(item, store) for item in rule["conditions"]]
                fact_conflicts = [item for item in condition_results if item["status"] == "conflict"]
                if fact_conflicts:
                    conflict = {"rule_id": rule["id"], "type": "contradictory_fact_evidence", "facts": fact_conflicts}
                    conflicts.append(conflict)
                    trace.append({"rule_id": rule["id"], "iteration": iteration, "status": "conflict", "conditions": condition_results})
                    continue
                if not all(item["matched"] for item in condition_results):
                    trace.append({"rule_id": rule["id"], "iteration": iteration, "status": "not_matched", "conditions": condition_results})
                    continue
                prerequisite = rule.get("requires_conclusion")
                if prerequisite and prerequisite not in conclusions:
                    trace.append({"rule_id": rule["id"], "iteration": iteration, "status": "waiting_for_prerequisite", "requires_conclusion": prerequisite, "conditions": condition_results})
                    continue

                value = self._calculate(rule, store, conclusions)
                conclusion_id = rule["conclusion"]
                definition = self.conclusion_definitions[conclusion_id]
                if conclusion_id in conclusions and conclusions[conclusion_id].value != value:
                    conflicts.append({
                        "type": "conflicting_derived_conclusions",
                        "conclusion": conclusion_id,
                        "existing_value": conclusions[conclusion_id].value,
                        "new_value": value,
                        "existing_rules": conclusions[conclusion_id].rule_ids,
                        "new_rule": rule["id"],
                    })
                    trace.append({"rule_id": rule["id"], "iteration": iteration, "status": "derived_conflict", "conclusion": conclusion_id})
                    fired_rules.append(rule["id"])
                    newly_fired = True
                    continue
                if conclusion_id in conclusions:
                    conclusions[conclusion_id].rule_ids.append(rule["id"])
                    conclusions[conclusion_id].priority = max(conclusions[conclusion_id].priority, rule["priority"])
                else:
                    conclusions[conclusion_id] = ConclusionResult(
                        conclusion_id=conclusion_id,
                        value=value,
                        unit=definition.get("unit"),
                        rule_ids=[rule["id"]],
                        priority=rule["priority"],
                        caveat=definition.get("caveat", ""),
                    )
                fired_rules.append(rule["id"])
                newly_fired = True
                trace.append({
                    "rule_id": rule["id"],
                    "iteration": iteration,
                    "status": "fired",
                    "conclusion": conclusion_id,
                    "value": value,
                    "priority": rule["priority"],
                    "explanation": rule["explanation"],
                    "limitations": rule.get("limitations", []),
                    "recommendations": self._recommendations(rule),
                })
            if not newly_fired:
                return InferenceResult(conclusions, fired_rules, trace, conflicts, iteration)
        trace.append({"status": "stopped", "reason": "max_iterations_reached", "max_iterations": max_iterations})
        return InferenceResult(conclusions, fired_rules, trace, conflicts, max_iterations)

    def backward_chain(self, target: str, store: FactStore) -> BackwardQueryResult:
        if target not in self.conclusion_definitions:
            raise KnowledgeBaseError(f"Unknown target conclusion: {target}")
        trace: list[dict[str, Any]] = []
        visiting: set[str] = set()

        def solve(conclusion_id: str) -> list[dict[str, Any]]:
            if conclusion_id in visiting:
                return [{"status": "dependency_cycle", "conclusion": conclusion_id, "missing_facts": [], "blockers": []}]
            visiting.add(conclusion_id)
            alternatives = []
            candidate_rules = [rule for rule in self.rules if rule["conclusion"] == conclusion_id]
            for rule in candidate_rules:
                missing, blockers, dependencies = [], [], []
                prerequisite = rule.get("requires_conclusion")
                if prerequisite:
                    if prerequisite == conclusion_id:
                        blockers.append({"type": "self_dependency", "conclusion": prerequisite})
                    else:
                        dependencies = solve(prerequisite)
                        if not any(item["status"] == "ready" for item in dependencies):
                            for item in dependencies:
                                missing.extend(item.get("missing_facts", []))
                                blockers.extend(item.get("blockers", []))
                condition_details = []
                for condition in rule["conditions"]:
                    result = self._evaluate_condition(condition, store)
                    condition_details.append(result)
                    if result["status"] == "missing" or result["status"] == "uncertain" or result["status"] == "rejected":
                        missing.append(condition["fact"])
                    elif result["status"] == "conflict":
                        blockers.append({"type": "conflicting_evidence", "fact": condition["fact"]})
                    elif not result["matched"]:
                        blockers.append({"type": "condition_not_satisfied", "fact": condition["fact"], "observed": result["observed"], "expected": result["expected"]})
                missing = list(dict.fromkeys(missing))
                status = "ready" if not missing and not blockers else ("needs_information" if missing and not blockers else "blocked")
                alternative = {
                    "rule_id": rule["id"],
                    "status": status,
                    "missing_facts": missing,
                    "blockers": blockers,
                    "prerequisite_alternatives": dependencies,
                    "conditions": condition_details,
                    "priority": rule["priority"],
                }
                alternatives.append(alternative)
                trace.append({"target": conclusion_id, **alternative})
            visiting.remove(conclusion_id)
            return alternatives

        alternatives = solve(target)
        return BackwardQueryResult(target, alternatives, trace)
