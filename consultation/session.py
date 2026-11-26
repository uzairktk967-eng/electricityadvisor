"""Consultation orchestration between NLP candidates and symbolic inference."""

from pathlib import Path
from typing import Any

from expert_system import InferenceEngine
from nlp import FactCandidate, extract_facts


class ConsultationSession:
    """A single in-memory consultation; no candidate is trusted automatically."""

    def __init__(self, knowledge_base_dir: str | Path, phrase_map_path: str | Path | None = None):
        self.engine = InferenceEngine(knowledge_base_dir)
        self.store = self.engine.new_fact_store()
        self.phrase_map_path = phrase_map_path
        self.candidates: list[FactCandidate] = []
        self.reviewed: dict[int, str] = {}

    def submit_text(self, text: str) -> list[dict[str, Any]]:
        """Extract candidates and retain them for explicit user review."""
        new_candidates = extract_facts(text, self.phrase_map_path)
        self.candidates.extend(new_candidates)
        start = len(self.candidates) - len(new_candidates)
        return [
            {"index": start + offset, **candidate.to_dict(), "reviewed": False}
            for offset, candidate in enumerate(new_candidates)
        ]

    def review_candidate(self, index: int, *, confirm: bool) -> dict[str, Any]:
        """Record the user's decision; confirmation is explicit and auditable."""
        if index < 0 or index >= len(self.candidates):
            raise IndexError(f"Unknown candidate index: {index}")
        if index in self.reviewed:
            raise ValueError(f"Candidate {index} has already been reviewed")
        candidate = self.candidates[index]
        status = "confirmed" if confirm else "rejected"
        note = candidate.note
        if candidate.status == "rejected" and confirm:
            status = "rejected"
            note = (note + " " if note else "") + "User confirmed the negated statement."
        elif not confirm:
            note = (note + " " if note else "") + "User did not confirm this extracted candidate."
        record = self.store.add(
            candidate.fact_id, candidate.value, status=status,
            source="natural_language_user_review", note=note,
        )
        self.reviewed[index] = status
        return {
            "index": index, "fact_id": record.fact_id, "value": record.value,
            "status": record.status, "source": record.source, "note": record.note,
        }

    def add_fact(self, fact_id: str, value: Any, *, source: str = "direct_user_input", note: str = "") -> dict[str, Any]:
        """Add a directly supplied, user-confirmed fact."""
        record = self.store.add(fact_id, value, status="confirmed", source=source, note=note)
        return {"fact_id": record.fact_id, "value": record.value, "status": record.status, "source": record.source}

    def evidence_summary(self) -> dict[str, dict[str, Any]]:
        """Return evidence status for every fact in the knowledge base."""
        summary = {}
        for fact_id, definition in self.engine.fact_definitions.items():
            evidence = self.store.evidence(fact_id)
            summary[fact_id] = {
                "label": definition.get("description", fact_id),
                "status": evidence["status"],
                "value": evidence["value"],
                "record_count": len(evidence["records"]),
            }
        return summary

    def missing_questions(self, target_conclusion: str) -> list[dict[str, str]]:
        """Turn backward-chaining missing facts into focused user questions."""
        plan = self.engine.backward_chain(target_conclusion, self.store)
        missing_ids: list[str] = []
        for alternative in plan.alternatives:
            if alternative["status"] in {"needs_information", "blocked"}:
                for fact_id in alternative.get("missing_facts", []):
                    if fact_id not in missing_ids:
                        missing_ids.append(fact_id)
        return [
            {
                "fact_id": fact_id,
                "question": self._question_for(fact_id, self.engine.fact_definitions[fact_id]),
                "unit": self.engine.fact_definitions[fact_id].get("unit") or "",
            }
            for fact_id in missing_ids
        ]

    @staticmethod
    def _question_for(fact_id: str, definition: dict[str, Any]) -> str:
        prompts = {
            "appliance.rated_power_w": "What is the appliance's rated input power shown on its label or manufacturer specification?",
            "appliance.quantity": "How many equivalent appliances are being considered?",
            "usage.hours_per_day": "Approximately how many hours per day is the appliance operating?",
            "usage.days_per_month": "How many days in the month is it used?",
            "tariff.price_per_kwh": "What marginal price do you pay per kWh (or per unit), according to your current tariff?",
            "appliance.standby_power_w": "What is the power measured or documented specifically in standby mode?",
            "usage.standby_hours_per_day": "For how many hours per day does it remain in standby mode?",
            "usage.schedule_flexible": "Can the operating schedule be shifted without affecting essential use or safety?",
            "appliance.has_energy_label": "Do you have an energy label or manufacturer specification for this appliance?",
            "supply.has_electrical_symptom": "Are there sparks, a burning smell, electric shocks, hot outlets/wiring, or repeated breaker trips?",
        }
        return prompts.get(fact_id, f"Please provide: {definition.get('description', fact_id)}")

    def run(self) -> dict[str, Any]:
        """Run forward chaining and assemble only rule-supported explanations."""
        result = self.engine.forward_chain(self.store)
        recommendations: list[dict[str, Any]] = []
        explanations: list[dict[str, Any]] = []
        for trace_item in result.trace:
            if trace_item.get("status") != "fired":
                continue
            explanations.append({
                "rule_id": trace_item["rule_id"],
                "conclusion": trace_item["conclusion"],
                "explanation": trace_item.get("explanation", ""),
                "limitations": trace_item.get("limitations", []),
            })
            for recommendation in trace_item.get("recommendations", []):
                if recommendation["id"] not in {item["id"] for item in recommendations}:
                    recommendations.append(recommendation)
        safety_required = "safety.professional_inspection_required" in result.conclusions
        return {
            "conclusions": {key: value.to_dict() for key, value in result.conclusions.items()},
            "fired_rules": list(result.fired_rules),
            "explanations": explanations,
            "recommendations": recommendations,
            "conflicts": result.conflicts,
            "evidence": self.evidence_summary(),
            "safety_notice": (
                "Electrical warning symptoms were reported. Stop using the affected appliance or outlet if safe, "
                "keep others away, and contact a qualified electrician. Do not attempt repairs."
                if safety_required else None
            ),
        }
