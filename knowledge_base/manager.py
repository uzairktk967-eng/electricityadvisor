"""Safe loading and validation helpers for knowledge-base draft documents."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

from jsonschema import Draft202012Validator


KNOWLEDGE_FILES = {
    "facts.json": "facts",
    "categories.json": "categories",
    "conclusions.json": "conclusions",
    "recommendations.json": "recommendations",
    "rules.json": "rules",
}

# Formula metadata is declarative. Only formulas explicitly implemented by the
# inference engine may be accepted for these rule identifiers.
APPROVED_FORMULAS = {
    "R-ENERGY-001": "rated_power_w * quantity * hours_per_day * days_per_month / 1000",
    "R-COST-001": "monthly_kwh_estimate * tariff_price_per_kwh",
    "R-STANDBY-001": "standby_power_w * quantity * standby_hours_per_day * days_per_month / 1000",
}


@dataclass(frozen=True)
class ValidationReport:
    errors: tuple[str, ...]
    warnings: tuple[str, ...]

    @property
    def is_valid(self) -> bool:
        return not self.errors


def load_documents(directory: str | Path) -> dict[str, dict[str, Any]]:
    """Load the five editable JSON knowledge-base documents."""
    root = Path(directory)
    documents: dict[str, dict[str, Any]] = {}
    for filename in KNOWLEDGE_FILES:
        path = root / filename
        try:
            with path.open("r", encoding="utf-8") as handle:
                documents[filename] = json.load(handle)
        except FileNotFoundError as exc:
            raise ValueError(f"Required knowledge-base file is missing: {filename}") from exc
        except json.JSONDecodeError as exc:
            raise ValueError(f"Invalid JSON in {filename}: {exc}") from exc
    return documents


def validate_documents(
    documents: Mapping[str, Any],
    schema: Mapping[str, Any],
) -> ValidationReport:
    """Validate document structure and cross-file semantic references."""
    errors: list[str] = []
    warnings: list[str] = []

    missing = sorted(set(KNOWLEDGE_FILES) - set(documents))
    if missing:
        errors.extend(f"Missing required document: {name}" for name in missing)
        return ValidationReport(tuple(errors), tuple(warnings))

    try:
        Draft202012Validator.check_schema(dict(schema))
    except Exception as exc:
        return ValidationReport((f"Knowledge-base schema is invalid: {exc}",), ())

    validator = Draft202012Validator(dict(schema))
    for filename in KNOWLEDGE_FILES:
        document = documents[filename]
        if not isinstance(document, dict):
            errors.append(f"{filename}: document root must be a JSON object")
            continue
        for issue in sorted(validator.iter_errors(document), key=lambda item: list(map(str, item.absolute_path))):
            location = ".".join(str(part) for part in issue.absolute_path) or "root"
            errors.append(f"{filename} [{location}]: {issue.message}")

    if errors:
        return ValidationReport(tuple(errors), tuple(warnings))

    collections = {
        filename: documents[filename][collection]
        for filename, collection in KNOWLEDGE_FILES.items()
    }

    id_sets: dict[str, set[str]] = {}
    for filename, items in collections.items():
        seen: set[str] = set()
        for index, item in enumerate(items):
            item_id = item["id"]
            if item_id in seen:
                errors.append(f"{filename}: duplicate ID '{item_id}' at item {index + 1}")
            seen.add(item_id)
        id_sets[filename] = seen

    facts = {item["id"]: item for item in collections["facts.json"]}
    categories = id_sets["categories.json"]
    conclusions = {item["id"]: item for item in collections["conclusions.json"]}
    recommendations = {item["id"]: item for item in collections["recommendations.json"]}
    rules = collections["rules.json"]

    for fact_id, fact in facts.items():
        minimum, maximum = fact.get("minimum"), fact.get("maximum")
        if minimum is not None and maximum is not None and minimum > maximum:
            errors.append(f"facts.json: '{fact_id}' has minimum greater than maximum")
        allowed = fact.get("allowed_values")
        if allowed is not None and len(allowed) != len(set(map(repr, allowed))):
            errors.append(f"facts.json: '{fact_id}' has duplicate allowed_values")
        if fact["type"] == "enum" and not allowed:
            errors.append(f"facts.json: enum fact '{fact_id}' must define allowed_values")

    for conclusion in conclusions.values():
        if conclusion["category"] not in categories:
            errors.append(
                f"conclusions.json: '{conclusion['id']}' references unknown category "
                f"'{conclusion['category']}'"
            )

    for recommendation in recommendations.values():
        if recommendation["category"] not in categories:
            errors.append(
                f"recommendations.json: '{recommendation['id']}' references unknown category "
                f"'{recommendation['category']}'"
            )
        if not recommendation["linked_conclusions"]:
            errors.append(f"recommendations.json: '{recommendation['id']}' has no linked conclusions")
        for conclusion_id in recommendation["linked_conclusions"]:
            if conclusion_id not in conclusions:
                errors.append(
                    f"recommendations.json: '{recommendation['id']}' references unknown conclusion "
                    f"'{conclusion_id}'"
                )

    rule_ids: set[str] = set()
    used_recommendations: set[str] = set()
    dependency_graph: dict[str, set[str]] = {}
    for rule in rules:
        rule_id = rule["id"]
        rule_ids.add(rule_id)
        if rule["category"] not in categories:
            errors.append(f"rules.json: '{rule_id}' references unknown category '{rule['category']}'")
        conclusion_id = rule["conclusion"]
        if conclusion_id not in conclusions:
            errors.append(f"rules.json: '{rule_id}' references unknown conclusion '{conclusion_id}'")
        prerequisite = rule.get("requires_conclusion")
        if prerequisite:
            if prerequisite not in conclusions:
                errors.append(f"rules.json: '{rule_id}' references unknown prerequisite '{prerequisite}'")
            else:
                dependency_graph.setdefault(conclusion_id, set()).add(prerequisite)

        for condition in rule["conditions"]:
            fact_id = condition["fact"]
            if fact_id not in facts:
                errors.append(f"rules.json: '{rule_id}' references unknown fact '{fact_id}'")
                continue
            fact = facts[fact_id]
            operator = condition["operator"]
            value = condition["value"]
            if operator in {"gt", "gte", "lt", "lte"} and fact["type"] not in {"number", "integer"}:
                errors.append(f"rules.json: '{rule_id}' uses numeric operator '{operator}' on non-numeric fact '{fact_id}'")
            if operator == "in" and not isinstance(value, list):
                errors.append(f"rules.json: '{rule_id}' operator 'in' requires a list for '{fact_id}'")
            if operator in {"eq", "neq"}:
                expected_type = fact["type"]
                if expected_type == "enum":
                    if value not in fact.get("allowed_values", []):
                        errors.append(f"rules.json: '{rule_id}' uses a value outside '{fact_id}' allowed_values")
                elif expected_type == "number" and (not isinstance(value, (int, float)) or isinstance(value, bool)):
                    errors.append(f"rules.json: '{rule_id}' expects a numeric comparison value for '{fact_id}'")
                elif expected_type == "integer" and (not isinstance(value, int) or isinstance(value, bool)):
                    errors.append(f"rules.json: '{rule_id}' expects an integer comparison value for '{fact_id}'")
                elif expected_type == "boolean" and not isinstance(value, bool):
                    errors.append(f"rules.json: '{rule_id}' expects a boolean comparison value for '{fact_id}'")
                elif expected_type == "string" and not isinstance(value, str):
                    errors.append(f"rules.json: '{rule_id}' expects a string comparison value for '{fact_id}'")
            if operator == "in" and isinstance(value, list) and fact["type"] == "enum":
                invalid = [entry for entry in value if entry not in fact.get("allowed_values", [])]
                if invalid:
                    errors.append(f"rules.json: '{rule_id}' has invalid enum members for '{fact_id}': {invalid}")

        for recommendation_id in rule["recommendations"]:
            used_recommendations.add(recommendation_id)
            if recommendation_id not in recommendations:
                errors.append(
                    f"rules.json: '{rule_id}' references unknown recommendation '{recommendation_id}'"
                )
            elif conclusion_id not in recommendations[recommendation_id]["linked_conclusions"]:
                errors.append(
                    f"rules.json: '{rule_id}' recommendation '{recommendation_id}' "
                    f"is not linked to conclusion '{conclusion_id}'"
                )

        formula = rule.get("formula")
        if formula is not None:
            approved = APPROVED_FORMULAS.get(rule_id)
            if approved is None or formula != approved:
                errors.append(
                    f"rules.json: '{rule_id}' uses a formula not explicitly allow-listed by the inference engine"
                )

    for recommendation_id in recommendations:
        if recommendation_id not in used_recommendations:
            warnings.append(f"Recommendation '{recommendation_id}' is not referenced by any rule")

    # Detect cycles in conclusion prerequisites before the engine's backward chaining runs.
    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(node: str, trail: list[str]) -> None:
        if node in visiting:
            cycle = " -> ".join(trail + [node])
            errors.append(f"rules.json: prerequisite dependency cycle detected: {cycle}")
            return
        if node in visited:
            return
        visiting.add(node)
        for dependency in dependency_graph.get(node, set()):
            visit(dependency, trail + [node])
        visiting.remove(node)
        visited.add(node)

    for conclusion_id in dependency_graph:
        visit(conclusion_id, [])

    return ValidationReport(tuple(errors), tuple(warnings))
