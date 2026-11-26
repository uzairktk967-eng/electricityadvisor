"""Rule-based assessment for several distinct appliances in one household.

Each appliance is evaluated in its own consultation so facts from different
appliances can never be mixed. Household totals are aggregated only after
each appliance has a rule-supported energy result.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Iterable

from .session import ConsultationSession


def assess_multiple_appliances(
    knowledge_base_dir: str | Path,
    appliances: Iterable[dict[str, Any]],
    *,
    tariff_per_kwh: float | None = None,
    electrical_symptom: bool = False,
) -> dict[str, Any]:
    """Assess separate appliance profiles and return transparent totals."""
    items = list(appliances)
    if not items:
        raise ValueError("Add at least one appliance before running an assessment.")

    results = []
    total_kwh = 0.0
    highest = None

    for position, item in enumerate(items, start=1):
        name = str(item.get("name", "")).strip()
        if not name:
            raise ValueError(f"Appliance {position}: enter an appliance name.")

        power = item.get("rated_power_w")
        quantity = item.get("quantity")
        hours = item.get("hours_per_day")
        days = item.get("days_per_month")

        if isinstance(power, bool) or not isinstance(power, (int, float)) or power < 0:
            raise ValueError(f"{name}: rated power must be a non-negative number.")
        if isinstance(quantity, bool) or not isinstance(quantity, int) or quantity < 1:
            raise ValueError(f"{name}: quantity must be a whole number of at least 1.")
        if isinstance(hours, bool) or not isinstance(hours, (int, float)) or not 0 <= hours <= 24:
            raise ValueError(f"{name}: daily operating hours must be between 0 and 24.")
        if isinstance(days, bool) or not isinstance(days, (int, float)) or not 0 <= days <= 31:
            raise ValueError(f"{name}: monthly usage days must be between 0 and 31.")

        session = ConsultationSession(knowledge_base_dir)
        session.add_fact("appliance.name", name)
        session.add_fact("appliance.rated_power_w", float(power))
        session.add_fact("appliance.quantity", quantity)
        session.add_fact("usage.hours_per_day", float(hours))
        session.add_fact("usage.days_per_month", float(days))
        if tariff_per_kwh is not None:
            if isinstance(tariff_per_kwh, bool) or not isinstance(tariff_per_kwh, (int, float)) or tariff_per_kwh < 0:
                raise ValueError("Tariff must be a non-negative amount per kWh.")
            session.add_fact("tariff.price_per_kwh", float(tariff_per_kwh))
        if electrical_symptom:
            session.add_fact("supply.has_electrical_symptom", True)

        result = session.run()
        energy = result["conclusions"].get("energy.monthly_kwh_estimate_available")
        if energy is None:
            raise ValueError(f"{name}: the rule engine did not produce a monthly energy estimate.")

        kwh = float(energy["value"])
        cost = kwh * float(tariff_per_kwh) if tariff_per_kwh is not None else None
        row = {
            "name": name,
            "rated_power_w": float(power),
            "quantity": quantity,
            "hours_per_day": float(hours),
            "days_per_month": float(days),
            "monthly_kwh": kwh,
            "monthly_variable_cost": cost,
            "result": result,
        }
        results.append(row)
        total_kwh += kwh
        if highest is None or kwh > highest["monthly_kwh"]:
            highest = row

    explanations = []
    recommendations = []
    fired_rules = []
    conflicts = []
    for row in results:
        row_result = row["result"]
        explanations.extend(row_result.get("explanations", []))
        conflicts.extend(row_result.get("conflicts", []))
        for rule_id in row_result.get("fired_rules", []):
            if rule_id not in fired_rules:
                fired_rules.append(rule_id)
        for recommendation in row_result.get("recommendations", []):
            if recommendation["id"] not in {item["id"] for item in recommendations}:
                recommendations.append(recommendation)

    conclusions = {
        "energy.monthly_kwh_estimate_available": {
            "value": total_kwh, "unit": "kWh/month",
            "caveat": "Household total is the sum of independently assessed appliance estimates.",
            "rule_ids": ["R-ENERGY-001"],
        }
    }
    if tariff_per_kwh is not None:
        conclusions["cost.monthly_variable_estimate_available"] = {
            "value": total_kwh * float(tariff_per_kwh), "unit": "currency/month",
            "caveat": "Variable energy estimate only; not a complete utility bill.",
            "rule_ids": ["R-COST-001"],
        }

    return {
        "appliances": results,
        "conclusions": conclusions,
        "explanations": explanations,
        "recommendations": recommendations,
        "conflicts": conflicts,
        "fired_rules": fired_rules,
        "total_monthly_kwh": total_kwh,
        "tariff_per_kwh": float(tariff_per_kwh) if tariff_per_kwh is not None else None,
        "total_monthly_variable_cost": (
            total_kwh * float(tariff_per_kwh) if tariff_per_kwh is not None else None
        ),
        "highest_consumption_appliance": highest["name"] if highest else None,
        "safety_notice": (
            "Electrical warning symptoms were reported. Stop using the affected appliance or outlet if safe, "
            "keep others away, and contact a qualified electrician. Do not attempt repairs."
            if electrical_symptom else None
        ),
        "disclosure": (
            "Estimates use the supplied rated power, quantity, daily operating hours and usage days. "
            "The variable cost excludes any bill components not represented by the entered rate."
        ),
    }
