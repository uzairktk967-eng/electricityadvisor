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
9. NLP proposes candidate facts only; it must not infer conclusions or silently confirm ambiguous evidence.

## 3. Logical components

| Component | Responsibility |
|---|---|
| `knowledge_base/` | JSON facts, rules, conclusions, categories and recommendations |
| `expert_system/` | Fact model, rule matcher, forward chaining, backward chaining and conflict handling |
| `nlp/` | Text normalization, tokenization, controlled phrase mapping, negation and uncertainty handling |
| `consultation/` | Dialogue state, evidence confirmation, missing-information questions and response assembly |
| `app.py` | Streamlit presentation and user interaction |
| `tests/` | Unit, integration, scenario and regression tests |
| `docs/` | Architecture, knowledge-base, developer, UI, testing and user documentation |

Future components for validation, explainability, reporting and storage may be introduced in their designated phases.

## 4. Consultation data flow

1. The user describes an appliance or electricity-use concern and provides appliance and usage details.
2. NLP extracts candidate facts with confidence/ambiguity metadata; it does not decide conclusions.
3. The UI displays candidates and requires explicit confirmation or rejection.
4. The consultation layer records reviewed evidence with provenance. Structured facts are validated against the fact catalogue.
5. Backward chaining identifies evidence needed for a requested target conclusion.
6. The inference engine matches validated rules and derives conclusions using forward chaining.
7. Conflict handling reports unresolved contradictions rather than silently choosing one value.
8. The consultation service returns conclusions, fired rules, explanations, limitations, rule-linked recommendations, evidence status and safety notices.
9. Streamlit presents these results; it does not contain a second implementation of the reasoning rules.

## 5. Core data concepts

- **Fact:** A named proposition/value with evidence status and source.
- **Rule:** An identifier, conditions, conclusion, category, priority, explanation and recommended actions.
- **Conclusion:** A defined proposition that rules may derive.
- **Evidence status:** At minimum confirmed, rejected, uncertain and missing.
- **Reasoning trace:** Ordered record of evaluated rules, matched conditions, derived facts and conflicts.
- **Recommendation:** A domain action linked to a rule and supported conclusion.
- **Fact candidate:** A proposed fact extracted from natural language, including source text, matched phrase, status and confidence indicator; it requires user review.

## 6. Inference design

- **Forward chaining:** Start from confirmed facts, repeatedly fire applicable rules until no new facts are derived or a documented stopping condition is reached.
- **Backward chaining:** Start from a target conclusion and recursively identify evidence needed to establish it.
- **Rule matching:** Evaluate conditions against explicit facts; missing or uncertain evidence must not be treated as true.
- **Conflict resolution:** Use explicit priority and a deterministic tie policy; retain an audit trace of competing rules.
- **Multiple conclusions:** Permit multiple independently supported conclusions in one consultation.
- **Contradictions:** Preserve conflicting evidence and surface it for clarification; do not silently choose one value.

## 7. Consultation and UI design

- NLP candidates remain separate from the fact store until the user explicitly reviews them.
- Direct structured inputs pass through the fact catalogue's type and range validation.
- The Streamlit structured input control is generated from the fact definitions rather than duplicating the catalogue in UI code.
- Backward-chaining prompts map missing fact IDs to focused questions.
- The response assembler exposes only conclusions and recommendations emitted by fired knowledge-base rules.
- Streamlit session state holds one in-memory consultation for the active browser session. It is not durable history; a reload or ended session may clear it.
- No database, user account, durable history or report export is implemented in this phase.

## 8. Technology choices

- Python for application and reasoning logic.
- Streamlit for the user interface.
- JSON for the initial knowledge base and controlled NLP phrase catalogue.
- Python standard library and free/open-source packages where needed.
- SQLite only if later requirements justify durable structured history.
- Streamlit Community Cloud as the intended free deployment target, subject to deployment verification.

No paid API or hosted service is required for core reasoning.

## 9. Quality and safety boundaries

Electricity estimates depend on appliance wattage, operating time, quantity and tariff assumptions. The system must distinguish user-provided measurements from estimates and disclose assumptions. Cost is a variable estimate based on the entered rate, not a complete utility bill; fixed charges, taxes, slabs, duties and adjustments may be excluded. Estimated savings are not guaranteed.

Electrical installation, wiring faults and hazardous repair advice are outside the scope of ordinary energy-saving recommendations; users should be directed to a qualified electrician for such issues.

The NLP package uses a limited deterministic vocabulary and explicit patterns. It may miss paraphrases or ambiguous wording. It must return candidates for user confirmation and must not present its confidence indicator as a calibrated probability.

## 10. Phase boundaries and verification

- **Phase 1:** Audit and architecture — complete.
- **Phase 2:** Engineer and structurally validate the JSON knowledge base — complete.
- **Phase 3:** Implement the independent symbolic inference engine — implemented; runtime verification deferred until deployment.
- **Phase 4:** Implement constrained, explainable lightweight NLP — implemented; runtime verification deferred until deployment.
- **Phase 5:** Implement consultation orchestration and response assembly — implemented; runtime verification deferred until deployment.
- **Phase 6:** Implement Streamlit presentation, candidate review, structured inputs, missing-information prompts and results — implemented; runtime verification deferred until deployment.
- **Phase 7 onward:** Knowledge-base management, validation, history, reports and final deployment readiness remain future work.

A component is implemented only when its source code and documentation exist. Test execution status must be reported separately; authored tests must never be described as passing until they have actually run.
