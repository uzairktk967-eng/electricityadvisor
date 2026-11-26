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
| 8 | Explainability, validation and automated testing | **Implemented; runtime verification deferred until deployment** |
| 9 | History, reports and exports | **Implemented; runtime verification deferred until deployment** |
| 10 | Final audit, documentation and deployment readiness | **Source audit complete; deployment/runtime verification pending** |
| 11 | Post-deployment bug fixing: NLP robustness and input validation | **In progress; multi-appliance workflow and full regression verification pending** |

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
- Tests are authored but not executed; runtime verification is deferred until deployment.

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

- Added `knowledge_base/manager.py` and package exports for loading and validating the five editable knowledge-base documents.
- Added JSON Schema Draft 2020-12 validation using the `jsonschema` dependency.
- Added cross-file checks for duplicate IDs, category/fact/conclusion/recommendation references, operator and fact-type compatibility, enum values, numeric thresholds, recommendation linkage and prerequisite dependency cycles.
- Added an explicit formula allow-list. Formula metadata is compared against known supported formula strings and is never executed.
- Added a Streamlit Knowledge-Base Management section. Users can edit JSON or upload a replacement into a session-only draft, validate the complete set and download a ZIP bundle only when validation succeeds.
- The management UI does not overwrite active knowledge-base files or commit changes to GitHub. Repository changes must be reviewed and committed through the normal Git workflow.
- Added six knowledge-base validation tests and `docs/KNOWLEDGE_BASE_MANAGEMENT.md`.

## Phase 8 — Explainability, validation and automated testing

- Added `docs/EXPLAINABILITY.md` defining the user-facing evidence states, trace fields, explanation contract, calculation disclosures and safety boundaries.
- Added ten end-to-end consultation scenarios in `tests/test_end_to_end.py`, covering energy/cost calculations, missing tariff, explicit candidate review, conflicting and uncertain evidence, standby-specific power, safety referral, flexible schedules, energy labels and provenance.
- Added `docs/TESTING.md` with test commands, acceptance criteria and regression/safety review guidance.
- The complete authored test suite now contains 51 tests: inference (9), NLP (9), consultation (8), knowledge-base validation (6), end-to-end scenarios (10) and history/report exports (9).
- Tests have not been executed. Runtime verification remains deferred until Streamlit deployment, as requested; no test-pass claim is made.
- Existing inference traces and consultation responses were retained as the explanation source; the UI is not permitted to invent independent conclusions or recommendations.

## Phase 9 — History, reports and exports

- Added `consultation/history.py` to create immutable JSON-safe snapshots of completed assessments with unique IDs, UTC timestamps, evidence values, status and provenance, plus full rule-supported results.
- Added a session-scoped history panel in Streamlit. It retains the latest 25 assessments, supports viewing a previous assessment, deleting one entry and clearing the session history.
- Added individual JSON and CSV exports plus a self-contained printable HTML report. Users can print the HTML report or save it as PDF from their browser. Added a JSON export of the full active-session history.
- Reports include conclusions, caveats, evidence, fired-rule explanations, limitations, recommendations, conflicts and safety notices. Raw natural-language paragraphs are not copied into report snapshots.
- Hardened dynamic HTML output with HTML escaping and CSV exports against spreadsheet formula injection. Added eight history/export regression tests.
- Added `docs/HISTORY_AND_REPORTS.md` describing the lifecycle, privacy, export formats and limitations.
- Deliberately did not add SQLite or local-file persistence: Streamlit Community Cloud does not guarantee local filesystem persistence. Durable multi-session history requires a separately configured persistent storage service and an explicit privacy/retention design.
- History and exports are generated in memory. No reports are stored on the app server; downloaded files are under the user's control.
- Tests are authored but not executed, consistent with the agreed post-deployment verification plan.

## Phase 10 — Final audit and deployment readiness

- Reviewed source integration across the Streamlit entry point, consultation service, inference engine, fact store, knowledge-base loader/validator, history/report exports and test modules.
- Fixed a structured-input type mismatch: integer facts such as appliance quantity now use integer-valued Streamlit number controls rather than passing floats to strict integer validation.
- Strengthened CSV formula-injection mitigation to detect formula prefixes after leading whitespace and added a regression test.
- Updated the Streamlit UI guide to reflect Phase 9 history/report functionality, integer input handling and the separate test-execution requirement.
- Updated architecture component descriptions and added `docs/FINAL_AUDIT.md` with deployment configuration, Community Cloud instructions, resolved findings and runtime acceptance checklist.
- Confirmed deployment configuration: root `app.py`, `main` branch, root `requirements.txt`, `.streamlit/config.toml`; recommended Community Cloud Python 3.12 selection. No secrets or external services are required by the current app.
- Community Cloud does not run the repository's unit tests automatically. Full automated test execution remains deferred until deployment/runtime access, as agreed.
- **Phase 10 source audit is complete; the app is prepared for deployment but not deployment-verified.** No app startup, browser interaction or test suite execution is claimed.

## Phase 11 — Post-deployment bug fixing (in progress)

- Investigated the live-use report where a natural-language appliance description produced no extracted facts.
- Expanded deterministic numeric phrase patterns to recognize common single-appliance wording: “rated at 80 W”, “runs 10 hours daily”, “operates for 4.5 hours a day”, simple number-word quantities, days-per-month wording and Pakistani rupee tariff phrasing.
- Added three NLP regression tests covering common paraphrases, word quantities and daily/monthly usage wording. The authored test count is now 56; tests have not yet been executed.
- Corrected the knowledge-base type for appliance quantity from a general number to an integer, so fractional appliance counts are rejected and the Streamlit integer input path is used; added a regression test.
- Fixed phrase matching at punctuation boundaries and added flexible-schedule paraphrases, addressing a pre-existing mismatch between the NLP test expectation and the phrase catalogue.
- Added a visible UI limitation notice: the current fact model safely supports one appliance profile at a time. Multiple different appliances cannot yet be represented as independent rows; combining them in one paragraph could incorrectly associate wattage/runtime values.
- Updated NLP documentation to state the expanded phrase coverage and the single-appliance boundary.
- Remaining work: implement a properly separated multi-appliance workflow, audit other input/engine/UI/report edge cases, execute regression tests, fix failures, and repeat the live acceptance checks.

## Verification status

- Phase 7 management code, UI and documentation were fetched back from GitHub during its implementation.
- Phase 8 test and documentation files were committed to the default branch.
- No application runtime, browser interaction or automated test execution has been performed in this workflow.
- Knowledge-base drafts remain session-only and require manual review and a Git commit to change active repository data.

## Current next phase

**Phase 11 — Post-deployment bug fixing.** Single-appliance NLP coverage and quantity typing have been improved. Multi-appliance support, full regression execution and deployed runtime verification remain outstanding.
