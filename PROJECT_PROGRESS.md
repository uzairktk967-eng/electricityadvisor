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
| 6 | Streamlit professional UI | **Implemented; runtime verification deferred until deployment** |
| 7 | Knowledge-base management | Next |
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

- Added `consultation/session.py` and package exports.
- Added a single-consultation workflow coordinating NLP candidates, explicit user review, the fact store and inference engine.
- Extracted candidates remain outside the fact store until a user confirms or rejects them. Each reviewed candidate records its source and review note; duplicate review is blocked.
- Added validated structured fact entry, evidence summaries and backward-chaining prompts for missing facts.
- Added a response assembler returning derived conclusions, fired rules, explanations, limitations, rule-linked recommendations, unresolved conflicts and safety notices.
- Added eight consultation unit tests and `docs/CONSULTATION.md`.

## Phase 6 — Streamlit user interface

### Deliverables
- Added root entry point `app.py` and pinned the Streamlit dependency in `requirements.txt`.
- Added a Streamlit theme configuration in `.streamlit/config.toml`.
- Added a natural-language description form and explicit candidate review controls. Negated candidates are labelled to make their review semantics clear.
- Added a structured fact-entry form generated from the existing fact catalogue, including numeric, string, boolean and enumerated values.
- Added missing-information prompts for monthly energy, variable cost and standby estimates.
- Added result presentation for rule-supported findings, caveats, evidence status, conflicts, explanations, limitations, recommendations and safety notices.
- Added clear disclosures that cost is a variable estimate rather than the complete bill, savings are not guaranteed, and the app does not diagnose electrical faults.
- Kept the reasoning and consultation logic in the existing independent packages; the UI is a presentation layer.
- Updated the README and added `docs/STREAMLIT_UI.md` with local run and Community Cloud deployment guidance.

### Verification status
- Phase 6 source and documentation files were committed and fetched back from GitHub for review.
- The app has not been launched and no automated tests have been run, in accordance with the developer's plan to test after deployment.
- Phases 3–5 still contain 26 authored tests; their execution remains deferred. No test-pass claim is made.
- Consultation state remains session-only and is not stored in a database.

## Current next phase

**Phase 7 — Knowledge-base management.** Add safe, validated workflows for reviewing and maintaining the JSON knowledge base. Do not begin Phase 8 until Phase 7 is completed and documented.
