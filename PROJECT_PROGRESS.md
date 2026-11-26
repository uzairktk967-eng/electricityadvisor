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
| 7 | Knowledge-base management | **Implemented; runtime verification deferred until deployment** |
| 8 | Explainability, validation and automated testing | Next |
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

- Added root entry point `app.py`, Streamlit dependency, theme configuration and `docs/STREAMLIT_UI.md`.
- Added natural-language input, explicit candidate review, structured fact entry, missing-information prompts and assessment results.
- Added findings, evidence status, conflicts, fired-rule explanations, limitations, recommendations and safety notices.
- Disclosed variable-cost estimate limitations, lack of guaranteed savings and electrical safety boundaries.
- Kept reasoning and consultation logic in independent packages.

## Phase 7 — Knowledge-base management

### Deliverables
- Added `knowledge_base/manager.py` and package exports for loading and validating the five editable knowledge-base documents.
- Added JSON Schema Draft 2020-12 validation using the `jsonschema` dependency.
- Added cross-file checks for duplicate IDs, category/fact/conclusion/recommendation references, operator and fact-type compatibility, enum values, numeric thresholds, recommendation linkage and prerequisite dependency cycles.
- Added an explicit formula allow-list. Formula metadata is compared against known supported formula strings and is never executed.
- Added a Streamlit Knowledge-Base Management section. Users can edit JSON or upload a replacement into a session-only draft, validate the complete set and download a ZIP bundle only when validation succeeds.
- The management UI does not overwrite active knowledge-base files or commit changes to GitHub. Repository changes must be reviewed and committed through the normal Git workflow.
- Added six knowledge-base validation tests and `docs/KNOWLEDGE_BASE_MANAGEMENT.md`.

### Verification status
- Phase 7 source, UI, requirements and documentation files were fetched back from GitHub for review.
- The Streamlit app and automated test suites have not been executed. Testing remains deferred until deployment, as requested; no test-pass claim is made.
- The repository now contains 32 authored tests across inference (9), NLP (9), consultation (8) and knowledge-base validation (6). None have been run in this environment.
- Draft management is session-only; exported changes require manual review and a Git commit.

## Current next phase

**Phase 8 — Explainability, validation and automated testing.** Improve end-to-end validation, test coverage and user-facing explanations. Do not begin Phase 9 until Phase 8 is completed and documented.
