# Consultation and Response Engine

## Scope

The consultation package coordinates the constrained NLP extractor, user evidence review, fact store and symbolic inference engine. It is independent of Streamlit and keeps one consultation in memory. It does not persist user data.

## Basic usage

```python
from consultation import ConsultationSession

session = ConsultationSession("knowledge_base")
candidates = session.submit_text(
    "My refrigerator has rated power 150 W and runs for 8 hours per day."
)

# Present each candidate to the user and ask for confirmation.
for candidate in candidates:
    print(candidate)

# After an explicit user decision:
session.review_candidate(candidates[0]["index"], confirm=True)

# Direct structured input is also supported:
session.add_fact("appliance.quantity", 1)
session.add_fact("usage.days_per_month", 30)

# Identify missing facts for a target calculation:
questions = session.missing_questions("energy.monthly_kwh_estimate_available")

# Run inference after collecting and reviewing evidence:
response = session.run()
```

## Workflow

1. Natural-language input is passed to the NLP extractor.
2. Candidates remain separate from the fact store until reviewed.
3. review_candidate records the user's decision and provenance. A candidate cannot be reviewed twice.
4. Structured inputs can be added using add_fact, which validates values against the fact catalogue.
5. missing_questions uses backward chaining to identify missing facts for a requested conclusion and maps them to concise prompts.
6. run invokes forward chaining and returns conclusions, fired rules, explanations, linked recommendations, conflicts, evidence status and a safety notice when applicable.

## Response safeguards

- Only conclusions derived by the inference engine are returned.
- Recommendations are collected only from rules that actually fired and are deduplicated by recommendation ID.
- Conflicting confirmed values remain conflicts; the consultation does not select a preferred value.
- Safety referral is surfaced when the safety rule fires. No electrical repair procedure is generated.
- Energy cost is explicitly a variable estimate based on the user's entered rate, not a complete utility bill.

## Limitations

- A session is in-memory and is lost when the process ends; persistent history is outside this phase.
- Questions are generated from a small, explicit fact-to-question mapping.
- Candidate extraction remains constrained by the phrase map and numeric patterns.
- The caller/UI must present candidates and collect explicit confirmation; the package itself does not render controls.
