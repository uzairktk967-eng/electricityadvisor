"""Deterministic, evidence-grounded conversational answers for user questions.

This module deliberately uses no external AI service. It translates supported
assessment results into readable prose and clearly states when evidence is
insufficient or a question is outside the advisor's scope.
"""

from __future__ import annotations

import re
from typing import Any


def _number(value: Any) -> str:
    return f"{float(value):,.2f}".rstrip("0").rstrip(".")


def generate_natural_language_answer(
    question: str,
    result: dict[str, Any] | None,
    *,
    appliance_name: str | None = None,
) -> str:
    """Answer common energy-advice questions using supplied result data only."""
    prompt = (question or "").strip()
    if not prompt:
        return "Please type a question about your appliance, electricity use, estimated cost, or assessment."

    lowered = prompt.casefold()
    safety_terms = (
        "spark", "burning smell", "electric shock", "shock", "hot wire",
        "hot outlet", "breaker trip", "breaker keeps", "smoke",
    )
    if any(term in lowered for term in safety_terms):
        return (
            "Electrical warning signs can indicate a hazardous fault. If it is safe to do so, "
            "stop using the affected appliance or outlet, keep people away, and contact a qualified "
            "electrician. Do not open equipment, touch exposed wiring, or attempt repairs. "
            "This advisor cannot diagnose the fault."
        )

    if result is None:
        return (
            "I can help with appliance energy use and estimated variable electricity cost. "
            "First enter and confirm the appliance's rated power, quantity, daily operating hours "
            "and monthly usage days, then run an assessment. You can then ask me about the results."
        )

    if result.get("safety_notice"):
        safety_prefix = (
            "Safety first: the assessment includes an electrical warning. Stop using the affected "
            "appliance or outlet if safe, keep others away, and contact a qualified electrician. "
            "Do not attempt repairs. "
        )
    else:
        safety_prefix = ""

    appliances = result.get("appliances")
    is_multi = isinstance(appliances, list)
    conclusions = result.get("conclusions", {})
    energy = conclusions.get("energy.monthly_kwh_estimate_available")
    cost = conclusions.get("cost.monthly_variable_estimate_available")

    asks_highest = any(term in lowered for term in (
        "which appliance", "highest", "most electricity", "biggest consumer",
        "consume the most", "uses the most",
    ))
    asks_cost = any(term in lowered for term in (
        "cost", "bill", "rupees", "rs.", "price", "pay",
    ))
    asks_reduce = any(term in lowered for term in (
        "reduce", "save", "saving", "lower", "decrease", "cut down",
    ))
    asks_why = any(term in lowered for term in (
        "why", "explain", "how come", "what does",
    ))
    asks_total = any(term in lowered for term in (
        "how much", "consumption", "energy", "units", "kwh", "electricity use",
    ))

    if is_multi:
        total = result.get("total_monthly_kwh")
        total_cost = result.get("total_monthly_variable_cost")
        highest = result.get("highest_consumption_appliance")
        if total is None:
            return safety_prefix + "The household assessment does not contain a monthly energy total yet. Please check the appliance inputs and run it again."
        if asks_highest:
            row = next((item for item in appliances if item.get("name") == highest), None)
            if row:
                return (
                    safety_prefix + f"{highest} is currently the largest electricity consumer in this household estimate, "
                    f"at {_number(row['monthly_kwh'])} kWh per month. Across all listed appliances, "
                    f"the estimated total is {_number(total)} kWh per month."
                )
        if asks_cost and total_cost is not None:
            return (
                safety_prefix + f"Based on the tariff you entered, the estimated variable energy cost for "
                f"all listed appliances is Rs. {_number(total_cost)} per month. This is an estimate, "
                "not your complete electricity bill; taxes, fixed charges, tariff slabs and adjustments may be excluded."
            )
        if asks_reduce:
            if highest:
                return (
                    safety_prefix + f"Start by reviewing the operating time of {highest}, which has the highest "
                    "estimated monthly consumption among the appliances you entered. Reduce runtime only where "
                    "it is practical and does not affect essential needs or safety. The estimate does not guarantee bill savings."
                )
            return safety_prefix + "I cannot identify a priority without a complete household appliance breakdown."
        if asks_total or asks_why:
            parts = [
                f"{item['name']}: {_number(item['monthly_kwh'])} kWh/month"
                for item in appliances
            ]
            return (
                safety_prefix + "Based on the power ratings, quantities and usage times you entered, "
                + "; ".join(parts)
                + f". Together, these appliances use an estimated {_number(total)} kWh per month."
            )
        return (
            safety_prefix + "I can explain your household total, estimated variable cost, the appliance "
            "using the most electricity, or practical ways to review usage. Please ask about one of those results."
        )

    if energy is None:
        return (
            safety_prefix + "I don't have enough confirmed information to calculate monthly consumption yet. "
            "Please provide rated power, quantity, hours used per day and days used per month, then run the assessment."
        )

    kwh = energy.get("value")
    if asks_highest:
        return (
            safety_prefix + "This assessment covers one appliance profile, so I cannot compare it with other "
            "appliances in your home. Add the other appliances in the household assessment to identify the largest consumer."
        )
    if asks_cost:
        if cost is None:
            return (
                safety_prefix + f"The estimated monthly energy use is {_number(kwh)} kWh, but I cannot estimate its "
                "variable cost until you enter your price per kWh."
            )
        return (
            safety_prefix + f"The estimated variable energy cost is {_number(cost.get('value'))} per month, "
            "using the tariff you entered. This is not a complete bill and may exclude fixed charges, taxes, "
            "tariff slabs and adjustments."
        )
    if asks_reduce:
        if result.get("recommendations"):
            advice = " ".join(item.get("text", "") for item in result["recommendations"] if item.get("text"))
            if advice:
                return safety_prefix + advice + " These suggestions are not a guarantee of savings."
        return (
            safety_prefix + "I don't have enough rule-supported information to recommend a specific change. "
            "Check the appliance's actual power use and whether its operating time can be reduced without affecting essential use."
        )
    if asks_total or asks_why:
        return (
            safety_prefix + f"Based on the inputs you confirmed, this appliance is estimated to use "
            f"{_number(kwh)} kWh per month. The estimate is calculated from rated power × quantity × "
            "hours per day × days per month ÷ 1,000. Appliances with cycling or variable power demand "
            "may use a different amount in practice."
        )

    if result.get("conflicts"):
        return safety_prefix + "Some of the information you entered conflicts. Please review the evidence section and correct the inputs before relying on the estimate."
    return (
        safety_prefix + "I have your assessment results. You can ask how much energy the appliance uses, "
        "what its estimated variable cost is, or how to review its usage. I will base the answer on the information you entered."
    )
