# Explainability and Evidence Traces

## User-facing explanation contract

Every displayed finding must be derived by the inference engine. The consultation response exposes:

- conclusion ID, value, unit, contributing rule IDs and caveat;
- fired rule IDs and the ordered inference trace;
- each fired rule's explanation, limitations and linked recommendations;
- evidence status and record count for every known fact;
- unresolved evidence conflicts; and
- a professional-referral notice when the electrical safety rule fires.

The Streamlit layer may format these records, but it must not create a conclusion or recommendation independently.

## Evidence states

| State | Meaning | Can satisfy a rule? |
|---|---|---|
| confirmed | Explicitly confirmed or directly entered evidence | Yes, if non-conflicting |
| uncertain | Evidence is ambiguous or not confirmed | No |
| rejected | The proposition was explicitly rejected | No |
| missing | No evidence record is available | No |
| conflict | Multiple confirmed records disagree | No |

A natural-language candidate is not evidence for inference until the user reviews it. Confirming a negated statement preserves the rejected status of the proposition represented by the candidate.

## Trace interpretation

Each rule evaluation is recorded with its rule ID, iteration, status and condition details. A fired rule additionally records its derived conclusion, value, priority, explanation, limitations and linked recommendations. Other trace states include not matched, waiting for prerequisite, conflict, derived conflict and iteration-limit stop.

Rule priority provides deterministic ordering; it does not suppress independent valid conclusions. Conflicting evidence is surfaced instead of silently selecting a value.

## Calculation transparency

- Monthly energy: rated input power × quantity × hours/day × days/month ÷ 1,000.
- Variable energy cost: estimated kWh × user-entered price per kWh.
- Standby energy: standby-specific power × quantity × standby hours/day × days/month ÷ 1,000.

Formula strings in JSON are metadata only. The engine uses explicit, allow-listed calculation implementations; it never evaluates arbitrary expressions from the knowledge base.

## Safety and limitations

A reported electrical warning symptom produces a professional-referral notice. The advisor does not diagnose faults or instruct users to repair wiring or electrical equipment.

Energy values depend on user-supplied inputs and assumptions. Variable cost is not a complete utility bill and may exclude fixed charges, taxes, tariff slabs and adjustments. Savings are not guaranteed. NLP confidence indicators are not calibrated probabilities.
