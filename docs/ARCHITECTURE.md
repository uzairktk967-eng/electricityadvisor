# System Architecture — Smart Home Electricity Advisor

## 1. Project identity

- **Name:** Smart Home Electricity Advisor
- **Developer:** M Uzair Khan
- **Academic program:** BS Artificial Intelligence
- **Institution:** CUSIT
- **Domain:** Energy Management / Electrical Engineering
- **Primary purpose:** Help households reason about appliance electricity use and identify evidence-supported opportunities to reduce avoidable consumption.

Project identity should be stored centrally in a configuration module during implementation rather than duplicated across UI and service modules.

## 2. Architecture principles

1. Keep symbolic reasoning independent of Streamlit.
2. Keep domain knowledge in version-controlled JSON data.
3. Make every conclusion traceable to matched rules and supplied facts.
4. Treat missing, uncertain, rejected and contradictory evidence distinctly.
5. Never create a recommendation unless a knowledge-base rule supports it.
6. Keep the core application free of paid APIs and external AI dependencies.
7. Validate knowledge-base changes before accepting them.
8. Use lightweight storage and document persistence limits clearly.

## 3. Proposed logical components

The following is a target design, not a claim that these modules already exist.

| Component | Responsibility |
|---|---|
| `config/` | Central project identity and application settings |
| `knowledge_base/` | JSON facts, rules, conclusions, categories and recommendations |
| `expert_system/` | Fact model, rule matcher, forward chaining, backward chaining and conflict resolution |
| `nlp/` | Text normalization, tokenization, synonym/phrase mapping, negation and uncertainty handling |
| `consultation/` | Dialogue state, evidence confirmation, missing-information questions and response assembly |
| `explainability/` | Rule evaluation log, inference trace and human-readable explanations |
| `validation/` | Knowledge-base schema, reference, duplicate and consistency checks |
| `reports/` | Consultation/test report generation and export helpers |
| `storage/` | Session/history persistence adapter, with a documented lightweight backend |
| `ui/` | Streamlit pages and reusable presentation components |
| `tests/` | Unit, integration, scenario and regression tests |
| `docs/` | Architecture, user, developer, testing and academic documentation |

## 4. Intended consultation data flow

1. The user describes an electricity-use concern and provides appliance and usage details.
2. The NLP layer extracts candidate facts with confidence/ambiguity metadata; it does not decide conclusions.
3. The consultation layer asks focused questions for missing or ambiguous evidence.
4. Confirmed and rejected evidence is stored as explicit facts with provenance.
5. The inference engine matches validated rules and derives conclusions using forward chaining; backward chaining can identify evidence needed for a requested hypothesis.
6. Conflict handling applies documented priorities and reports unresolved conflicts rather than hiding them.
7. The explanation layer reports the evidence, rules evaluated, rules fired and resulting conclusions.
8. The response layer formats only those conclusions and recommendations returned by the inference engine.
9. The UI presents the consultation and trace; optional history/report services store or export it.

## 5. Core data concepts

- **Fact:** A named proposition/value with evidence status and source.
- **Rule:** An identifier, conditions, conclusion, category, priority, explanation and recommended actions.
- **Conclusion:** A defined proposition that rules may derive.
- **Evidence status:** At minimum confirmed, rejected, uncertain and missing.
- **Reasoning trace:** Ordered record of evaluated rules, matched conditions, derived facts and conflicts.
- **Recommendation:** A domain action linked to a rule and supported conclusion.

Exact JSON schemas and the first domain rule set belong to Phase 2, not Phase 1.

## 6. Inference design

- **Forward chaining:** Start from confirmed facts, repeatedly fire applicable rules until no new facts are derived or a documented stopping condition is reached.
- **Backward chaining:** Start from a target conclusion and recursively identify rules and prerequisite facts that could establish it.
- **Rule matching:** Evaluate conditions against explicit facts; missing or uncertain evidence must not be treated as true.
- **Conflict resolution:** Use explicit priority and a deterministic tie policy; retain an audit trace of competing rules.
- **Multiple conclusions:** Permit multiple independently supported conclusions in one consultation.
- **Contradictions:** Preserve conflicting evidence and surface it for clarification; do not silently choose one value.

## 7. Initial technology choices

- Python for application and reasoning logic.
- Streamlit for the user interface.
- JSON for the initial knowledge base.
- Python standard library and free/open-source packages where needed.
- SQLite only if later requirements justify durable structured history.
- Streamlit Community Cloud as the intended free deployment target, subject to deployment verification.

No paid API or hosted service is required for core reasoning.

## 8. Quality and safety boundaries

Electricity estimates depend on appliance wattage, operating time, quantity and applicable tariff assumptions. The system must distinguish user-provided measurements from estimates and disclose assumptions. It should avoid presenting estimated savings as guaranteed bill reductions. Electrical installation, wiring faults and hazardous repair advice are outside the scope of ordinary energy-saving recommendations; users should be directed to a qualified electrician for such issues.

## 9. Phase boundaries

- **Phase 1:** Audit and architecture only — complete.
- **Phase 2:** Engineer and validate the JSON knowledge base.
- **Phase 3:** Implement the independent symbolic inference engine — committed; runtime test execution pending.
- **Phase 4:** Implement constrained, explainable lightweight NLP after Phase 3 tests pass.
- **Phase 5 onward:** Build consultation, UI, management, testing, reporting and deployment capabilities in sequence.

This document describes the intended design. A component is implemented only when its source code and verification evidence exist in the repository.
