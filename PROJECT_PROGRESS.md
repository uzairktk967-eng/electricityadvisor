# Project Progress — Smart Home Electricity Advisor

**Developer:** M Uzair Khan  
**Program:** BS Artificial Intelligence  
**Institution:** CUSIT  
**Domain:** Energy Management / Electrical Engineering  
**Repository:** https://github.com/uzairktk967-eng/electricityadvisor  
**Default branch:** `main`

## Development roadmap

| Phase | Scope | Status |
|---|---|---|
| 1 | Repository audit and architecture | **Complete** |
| 2 | Knowledge-base engineering | **Complete** |
| 3 | Core inference engine | **Implemented; runtime verification deferred until deployment** |
| 4 | Lightweight natural-language processing | **Implemented; runtime verification deferred until deployment** |
| 5 | Consultation and response engine | **Implemented; runtime verification deferred until deployment** |
| 6 | Streamlit professional UI | Next |
| 7 | Knowledge-base management | Not started |
| 8 | Explainability, validation and automated testing | Not started |
| 9 | History, reports and exports | Not started |
| 10 | Final audit, documentation and deployment readiness | Not started |

## Phase 1 — Repository audit and architecture

- Confirmed repository identity, visibility, default branch and initial commit.
- Inspected the original README and searched for application and progress files.
- Established that development should begin from an initial repository state.
- Defined the modular architecture in `docs/ARCHITECTURE.md`.
- Preserved the original README; no existing project files were deleted or replaced.

## Phase 2 — Knowledge-base engineering

- Added versioned JSON catalogues for 13 facts, 6 categories, 6 conclusions, 6 recommendations and 6 IF–THEN rules.
- Added a Draft 2020-12 JSON Schema describing the knowledge-base file structures.
- Added `docs/KNOWLEDGE_BASE.md` documenting evidence semantics, calculation conventions, rule semantics, safety boundaries and validation requirements.
- Added standby-specific power so standby estimates cannot use ordinary rated operating power by implication.
- All six JSON files were fetched back from GitHub and parsed successfully.
- Cross-file semantic references and duplicate-ID checks passed. This was not execution of a formal JSON Schema validator or application tests.

## Phase 3 — Core inference engine

- Added typed facts, evidence statuses, provenance, contradictory confirmed-value detection, forward chaining, backward chaining, deterministic rule matching and inference traces.
- Added allow-listed calculations for monthly energy, variable energy cost and standby energy. Formula metadata is never evaluated using Python `eval`.
- Added nine standard-library unit tests and `docs/INFERENCE_ENGINE.md`.
- Tests are authored but not executed; runtime verification is deferred until Streamlit deployment at the developer's request.

## Phase 4 — Lightweight natural-language processing

- Added text normalization, tokenization, controlled phrase mapping and a versioned phrase catalogue.
- Added extraction for appliance names, explicit numeric power/usage/tariff values, energy-label availability, flexible schedules and electrical warning symptoms.
- Candidates retain source text, matched text, evidence status, confidence indicator and notes.
- Uncertainty and local negation are handled conservatively. Extraction does not write facts or run inference.
- Added nine NLP tests and `docs/NLP.md`.
- Tests are authored but not executed; runtime verification is deferred until Streamlit deployment.

## Phase 5 — Consultation and response engine

### Deliverables
- Added `consultation/session.py` and package exports.
- Added a single-consultation workflow that coordinates NLP candidates, explicit user review, the fact store and inference engine.
- Extracted candidates remain outside the fact store until a user confirms or rejects them. Each reviewed candidate records its source and review note; duplicate review is blocked.
- Added validated structured fact entry for direct user input.
- Added evidence summaries and backward-chaining prompts for missing facts, including energy, cost and standby inputs.
- Added a response assembler that returns only derived conclusions, fired rules, explanations, limitations, rule-linked recommendations and unresolved conflicts.
- Added a conservative safety notice when the electrical-symptom rule fires.
- Added eight consultation unit tests and `docs/CONSULTATION.md`.

### Verification status
- The Phase 3, 4 and 5 test suites contain 26 authored tests in total (9 inference, 9 NLP, 8 consultation).
- None have been executed in this environment. Runtime verification is deferred until Streamlit deployment, as agreed. No test pass is claimed.
- Consultation state is currently in memory and is lost when the process ends. Persistence/history is outside this phase.

## Current next phase

**Phase 6 — Streamlit user interface.** Build a user-facing consultation flow with candidate confirmation, structured inputs, missing-information prompts, results, explanations and safety messaging. Keep reasoning logic in the existing independent packages. Do not begin Phase 7 until Phase 6 is completed and documented.
