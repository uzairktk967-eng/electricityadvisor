"""Deterministic, knowledge-base-grounded conversational answers.

Answers are generated only from the advisor's documented scope and the
current assessment evidence. Unknown topics are explicitly declined.
"""
from __future__ import annotations

import re
from typing import Any


def _number(value: Any) -> str:
    return f"{float(value):,.2f}".rstrip("0").rstrip(".")


def _has(text: str, *patterns: str) -> bool:
    return any(re.search(pattern, text) for pattern in patterns)


def _safety_answer() -> str:
    return (
        "Electrical warning signs can indicate a hazardous fault. If safe, stop using "
        "the affected appliance or outlet, keep people away, and contact a qualified "
        "electrician. Do not touch exposed wiring, open equipment, or attempt repairs. "
        "This advisor cannot diagnose the fault."
    )


def _general_knowledge_answer(text: str) -> str | None:
    """Answer stable FAQs that are explicitly covered by the knowledge base."""
    if _has(text, r"\b(kwh|kilowatt.?hours?|units?)\b.*\b(mean|meaning|what is|define)",
            r"\bwhat does\b.*\b(kwh|unit)\b"):
        return (
            "A kilowatt-hour (kWh), commonly called one electricity unit, is the energy "
            "used by a 1,000-watt load operating for one hour. For example, 100 W used "
            "for 10 hours consumes 1 kWh."
        )
    if _has(text, r"\bhow\b.*\b(calculat|work out|estimate)\b.*\b(consumption|energy|units?)\b",
            r"\bformula\b.*\b(kwh|electricity|energy)\b"):
        return (
            "The advisor estimates monthly energy with this formula: rated power in watts "
            "× quantity × operating hours per day × days used per month ÷ 1,000. "
            "The result is kWh (electricity units) per month. It assumes the entered "
            "power is representative while the appliance is operating."
        )
    if _has(text, r"\b(what information|which details|what details|what do you need)\b",
            r"\b(required|need to provide)\b.*\b(calculat|estimate)\b"):
        return (
            "To estimate monthly consumption, provide the appliance's rated input power "
            "(W), number of equivalent appliances, average operating hours per day, and "
            "days used in the month. To estimate variable cost as well, provide your "
            "applicable tariff per kWh. Standby estimates need a separate standby-power value."
        )
    if _has(text, r"\b(standby|sleep mode|待機)\b"):
        return (
            "Standby consumption is calculated separately. The advisor needs power "
            "specifically measured or documented in standby mode, the number of devices, "
            "standby hours per day and days per month. Rated operating power must not be "
            "assumed to equal standby power."
        )
    if _has(text, r"\b(full|total|actual)\b.*\b(electricity )?bill\b",
            r"\bdoes this include\b.*\b(tax|fixed charge|bill|slab)\b"):
        return (
            "No. This advisor estimates variable energy cost from kWh × the tariff you "
            "enter. It does not calculate a complete utility bill; fixed charges, taxes, "
            "duties, tariff slabs and adjustments may be excluded."
        )
    if _has(text, r"\b(actual|real)\b.*\b(consumption|usage)\b",
            r"\bwhy\b.*\b(estimate|actual|different|vary)\b",
            r"\b(cycl|compressor|thermostat|variable load)\b"):
        return (
            "The estimate assumes the entered rated power is representative throughout "
            "the stated operating hours. Appliances that cycle on and off or vary their "
            "power demand (for example, compressor-based appliances) may use a different "
            "amount. A suitable energy meter's measured kWh is preferable for actual use."
        )
    if _has(text, r"\b(efficient|efficiency|energy.?star|star rating|compare.*appliance)\b"):
        return (
            "The advisor supports comparing verified energy labels or manufacturer "
            "consumption specifications for appliances providing the same service. It "
            "cannot rank efficiency from brand, age or rated wattage alone; comparable "
            "capacity and test conditions are needed."
        )
    if _has(text, r"\b(save|saving|reduce|lower|cut)\b.*\b(electricity|energy|consumption|usage)\b",
            r"\bhow can i\b.*\b(save|reduce)\b"):
        return (
            "The knowledge base supports reviewing operating hours where the schedule is "
            "flexible, checking the appliance's documented input power, and comparing "
            "verified energy labels. Do not reduce essential refrigeration, medical, "
            "safety-critical or other necessary use. These steps do not guarantee savings."
        )
    return None


def generate_natural_language_answer(
    question: str,
    result: dict[str, Any] | None,
    *,
    appliance_name: str | None = None,
) -> str:
    """Answer supported questions using only the active assessment and KB scope."""
    prompt = (question or "").strip()
    if not prompt:
        return "Please type a question about electricity consumption, cost, appliance usage, efficiency or electrical safety."

    text = prompt.casefold()
    if _has(text, r"\bspark", r"\bburning smell\b", r"\belectric shock\b",
            r"\bhot (?:wire|wiring|outlet|socket)\b", r"\bbreaker\b.*\btrip",
            r"\bsmoke\b"):
        return _safety_answer()

    general = _general_knowledge_answer(text)
    if general:
        return general

    if result is None:
        if _has(text, r"\b(hello|hi|hey)\b", r"\bwho are you\b", r"\bwhat can you do\b"):
            return (
                "I am a Smart Home Electricity Advisor. I can estimate appliance kWh and "
                "variable energy cost, explain the calculation, discuss standby use and "
                "verified efficiency information, and give conservative electrical-safety guidance."
            )
        return (
            "I can answer this using the electricity advisor's knowledge base, but I do not "
            "have an assessment to refer to yet. Enter and confirm the appliance power, "
            "quantity, hours per day and days per month, then run an assessment. If your "
            "question is outside appliance energy use, cost, standby use, efficiency or "
            "electrical safety, it is not covered by this knowledge base."
        )

    safety_prefix = ""
    if result.get("safety_notice"):
        safety_prefix = (
            "Safety notice: stop using the affected appliance or outlet if safe, keep "
            "others away and contact a qualified electrician. Do not attempt repairs. "
        )

    evidence = result.get("evidence") or {}
    facts = {
        key: item.get("value")
        for key, item in evidence.items()
        if isinstance(item, dict) and item.get("status") == "confirmed"
    }
    conclusions = result.get("conclusions") or {}
    energy = conclusions.get("energy.monthly_kwh_estimate_available")
    cost = conclusions.get("cost.monthly_variable_estimate_available")
    appliances = result.get("appliances")
    is_multi = isinstance(appliances, list)

    if _has(text, r"\b(what (?:are|were) )?(my )?(input|inputs|details|assumptions)\b",
            r"\bwhat information did i give\b", r"\bshow.*\b(power|hours|quantity|tariff)\b"):
        if is_multi:
            rows = [
                f"{item.get('name', 'Appliance')}: {item.get('quantity')} unit(s), "
                f"{_number(item.get('rated_power_w', 0))} W each, "
                f"{_number(item.get('hours_per_day', 0))} h/day, "
                f"{_number(item.get('days_per_month', 0))} days/month"
                for item in appliances
            ]
            return safety_prefix + "Your confirmed household inputs are: " + "; ".join(rows) + "."
        labels = [
            ("Rated power", "appliance.rated_power_w", " W"),
            ("Quantity", "appliance.quantity", ""),
            ("Daily operating time", "usage.hours_per_day", " hours/day"),
            ("Days used per month", "usage.days_per_month", " days/month"),
            ("Tariff", "tariff.price_per_kwh", " Rs./kWh"),
        ]
        available = [
            f"{label}: {_number(facts[key])}{unit}"
            for label, key, unit in labels if key in facts and facts[key] is not None
        ]
        return safety_prefix + (
            "Confirmed inputs: " + "; ".join(available) + "."
            if available else "No confirmed input facts are available in this assessment yet."
        )

    if is_multi:
        total = result.get("total_monthly_kwh")
        total_cost = result.get("total_monthly_variable_cost")
        highest = result.get("highest_consumption_appliance")
        asks_highest = _has(text, r"\b(which|what)\b.*\b(appliance|device)\b.*\b(most|highest|largest)\b",
                            r"\bhighest\b", r"\bbiggest consumer\b", r"\buses the most\b")
        asks_cost = _has(text, r"\bcost\b", r"\bhow much\b.*\b(pay|rupees|rs\.?)\b",
                         r"\bprice\b", r"\bexpensive\b")
        asks_total = _has(text, r"\b(total|together|combined|overall)\b",
                          r"\b(consumption|energy|units|kwh)\b", r"\bhow much electricity\b")
        if asks_highest and highest:
            row = next((item for item in appliances if item.get("name") == highest), None)
            if row:
                return safety_prefix + (
                    f"{highest} is the highest-consuming listed appliance at "
                    f"{_number(row['monthly_kwh'])} kWh/month. The household total is "
                    f"{_number(total)} kWh/month."
                )
        if asks_cost:
            if total_cost is None:
                return safety_prefix + "The household energy estimate is available, but no tariff was supplied, so I cannot calculate variable cost. Provide your applicable price per kWh."
            return safety_prefix + (
                f"The estimated variable energy cost for the listed appliances is "
                f"Rs. {_number(total_cost)} per month. This is not the complete electricity bill."
            )
        if asks_total and total is not None:
            breakdown = "; ".join(
                f"{item.get('name', 'Appliance')}: {_number(item.get('monthly_kwh', 0))} kWh/month"
                for item in appliances
            )
            return safety_prefix + f"Monthly breakdown: {breakdown}. Combined use: {_number(total)} kWh/month."
        if _has(text, r"\b(recommend|suggest|advice|reduce|save|improve)\b"):
            return safety_prefix + (
                "The knowledge base recommends reviewing operating hours only where use is "
                "flexible, checking verified power specifications and comparing like-for-like "
                "energy labels. Do not compromise essential use. No saving is guaranteed."
            )

    else:
        if energy is None:
            missing = [
                label for key, label in [
                    ("appliance.rated_power_w", "rated power (W)"),
                    ("appliance.quantity", "quantity"),
                    ("usage.hours_per_day", "hours per day"),
                    ("usage.days_per_month", "days per month"),
                ] if key not in facts
            ]
            return safety_prefix + (
                "I cannot calculate monthly consumption yet. Missing confirmed information: "
                + (", ".join(missing) if missing else "the assessment has no valid energy conclusion")
                + ". Add or confirm these inputs and run the assessment again."
            )
        kwh = energy.get("value")
        if _has(text, r"\b(cost|bill|rupees|rs\.?|pay|tariff|price)\b"):
            if cost is None:
                return safety_prefix + (
                    f"Your estimated monthly consumption is {_number(kwh)} kWh, but the "
                    "tariff is not confirmed. Provide your applicable price per kWh to "
                    "estimate variable energy cost. This will not be the complete bill."
                )
            return safety_prefix + (
                f"Your estimated monthly variable energy cost is Rs. "
                f"{_number(cost.get('value'))}, based on the tariff you supplied. "
                "Fixed charges, taxes, slabs and adjustments may be excluded."
            )
        if _has(text, r"\b(consumption|electricity|energy|units?|kwh)\b",
                r"\bhow much\b", r"\bcalculate\b", r"\bestimate\b"):
            details = []
            for key, label, unit in [
                ("appliance.rated_power_w", "rated power", " W"),
                ("appliance.quantity", "quantity", ""),
                ("usage.hours_per_day", "operating time", " h/day"),
                ("usage.days_per_month", "usage period", " days/month"),
            ]:
                if key in facts:
                    details.append(f"{label} {_number(facts[key])}{unit}")
            return safety_prefix + (
                f"Based on your confirmed inputs ({', '.join(details)}), the estimated "
                f"monthly consumption is {_number(kwh)} kWh (units). Formula: rated power "
                "× quantity × hours/day × days/month ÷ 1,000. Actual use may differ if "
                "the appliance cycles or varies its power demand."
            )
        if _has(text, r"\b(recommend|suggest|advice|reduce|save|improve)\b"):
            advice = " ".join(
                item.get("text", "") for item in result.get("recommendations", [])
                if item.get("text")
            )
            if advice:
                return safety_prefix + advice + " These suggestions do not guarantee savings."
            return safety_prefix + (
                "The supported advice is to verify the appliance's input power from its "
                "label or manufacturer documentation. Review runtime only if it can be "
                "reduced without affecting essential use."
            )

    if result.get("conflicts"):
        if _has(text, r"\b(conflict|different values|contradict|wrong input)\b"):
            return safety_prefix + (
                "The assessment contains conflicting evidence. Review the evidence section "
                "and resolve the conflicting values before relying on the estimate."
            )

    if _has(text, r"\b(compare|comparison|versus|\bvs\b)\b"):
        return (
            "The knowledge base can compare appliance consumption only when separate "
            "appliance inputs are supplied in the household assessment. This single-appliance "
            "assessment cannot compare devices."
        )

    return (
        "I can't find a supported answer to that question in my current knowledge base. "
        "This advisor currently covers appliance electricity consumption estimates, "
        "user-entered tariff-based variable cost, required inputs and calculation method, "
        "standby consumption, verified energy-label comparisons, usage-schedule review and "
        "basic electrical-safety referral. I won't guess beyond that scope."
    )
