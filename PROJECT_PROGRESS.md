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
| 11 | Post-deployment bug fixing: NLP robustness and input validation | **Implemented; automated verification pending** |
| 12 | Multi-appliance household assessment | **Implemented in source; prior CI run passed; latest revision verification pending** |
| 13 | Natural-language conversational answers | **Implemented in source; latest CI and live verification pending** |

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

## Phase 12 — Multi-appliance household assessment (implemented; verification pending)

- Added `consultation/multi_appliance.py`. Each distinct appliance is evaluated in a separate `ConsultationSession`, preventing one appliance's wattage, quantity or runtime from being mixed with another's.
- Added household aggregation for monthly kWh, optional variable tariff cost, and identification of the highest-consuming appliance.
- Reuses the existing rule engine for each appliance's energy and cost conclusions; no new formula strings or arbitrary formula evaluation were introduced.
- Added input validation for names, finite non-negative power and tariff values, integer quantities, daily runtime from 0–24 hours, and monthly usage from 0–31 days.
- Added Streamlit inputs for multiple appliances, household result table, aggregate totals, and a household electrical-symptom safety referral.
- Multi-appliance assessments are added to session history with appliance-specific input labels. Their history snapshot is isolated from any separate single-appliance consultation facts.
- Added eight focused tests in `tests/test_multi_appliance.py`, bringing the authored suite to 64 tests. Tests have not yet been executed; the GitHub Actions workflow was added to run the suite on pushes and pull requests.
- Acceptance example: 3 × 80 W fans at 10 h/day, 5 × 20 W bulbs at 6 h/day, and 1 × 1,000 W heater at 3 h/day, each for 30 days, should total 180 kWh/month; at Rs. 55/kWh, the estimated variable cost is Rs. 9,900, and the heater is the largest consumer.

## Phase 13 — Natural-language conversational answers (implemented; verification pending)

- Added `consultation/natural_response.py`, a deterministic, evidence-grounded response helper that converts supported assessment results into conversational English.
- Added a Streamlit question field labelled “Ask a question in your own words” so users can ask about consumption, cost, the highest-consuming appliance, and practical usage review.
- For multi-appliance results, the helper can explain the household total, itemized appliance consumption, variable cost and highest-consuming appliance.
- For single-appliance results, it explains estimated monthly kWh, the calculation inputs and limitations, and requests the missing tariff before estimating cost.
- If no assessment exists, it asks the user to enter and confirm required inputs first. If evidence is insufficient or the question is outside the supported scope, it says so rather than inventing an answer.
- Safety-related questions receive a conservative qualified-electrician referral. The helper does not diagnose electrical faults or give repair instructions.
- The implementation uses deterministic local templates and no external AI/API. It is a limited-domain conversational helper, not an unrestricted chatbot. It currently generates English responses; multilingual responses are not implemented.
- Added six tests in `tests/test_natural_response.py`. The authored suite now contains 70 tests. A previous 64-test revision passed in GitHub Actions; the latest revision with natural-language response tests still needs its own completed successful workflow run and live Streamlit check.


## Phase 18 — Broader knowledge-base question answering (implemented; verification pending)

- Reworked consultation/natural_response.py from a small set of keyword branches into a broader deterministic question router for the advisor's documented scope.
- Added direct answers for kWh/unit meaning, the monthly consumption formula, required inputs, standby-power rules, variable-cost versus complete-bill limitations, actual-versus-estimated consumption, efficiency-label comparisons, and safe usage-review guidance.
- Added assessment-aware answers for confirmed input values, single-appliance consumption and cost, household totals, highest-consuming appliance, missing confirmed facts, and evidence conflicts.
- Added explicit unknown-topic responses stating that unsupported subjects are not covered by the current knowledge base; the assistant must not guess.
- Electrical warning symptoms retain a high-priority qualified-electrician referral.
- Added nine regression tests for the new FAQ categories, confirmed-input reporting and unknown-topic refusal. The authored test suite count is now 79; tests have not been run and the deployed Streamlit app has not yet been verified.
- The response helper remains deterministic and local. It does not use an external LLM/API and is not an unrestricted chatbot. New topics must be added to the knowledge base and covered by tests before being advertised as supported.

## Verification status

- Phase 7 management code, UI and documentation were fetched back from GitHub during its implementation.
- Phase 8 test and documentation files were committed to the default branch.
- No application runtime, browser interaction or automated test execution has been performed in this workflow.
- Knowledge-base drafts remain session-only and require manual review and a Git commit to change active repository data.

## Current next phase

**Phase 11 — Post-deployment bug fixing.** Single-appliance NLP coverage, punctuation matching, quantity typing and CI test automation have been improved. Automated test execution and deployed runtime verification remain outstanding.

**Phase 12 — Multi-appliance household assessment.** The source implementation calculates each appliance independently and aggregates household totals, variable cost and highest consumption. A previous 64-test revision passed in GitHub Actions; latest source revision and live Streamlit acceptance remain outstanding.

**Phase 13 — Natural-language conversational answers.** Users can ask common questions in their own words and receive evidence-grounded conversational English answers. The current helper is deterministic and limited to supported question types; current-revision CI and live verification remain outstanding.


## Phase 14 — Automatic assessment after fact review (implemented; runtime verification pending)

- Fixed a confusing review workflow: confirming or rejecting the final extracted candidate now automatically runs the single-appliance rule-based assessment.
- The resulting assessment is stored in session state and added to session history, then an evidence-grounded natural-language summary is shown automatically.
- If not all extracted candidates have been reviewed, the system waits rather than assessing partially reviewed evidence.
- If the assessment cannot run, the UI displays an explanatory message instead of silently leaving the user without a response.
- The existing manual assessment button remains available for structured inputs and repeat assessments.
- Updated app.py was fetched back from GitHub and checked for the automatic review-to-assessment flow. Automated tests and deployed Streamlit interaction have not yet been run; live verification remains pending.


## Phase 15 — Always show an answer after fact review (implemented; runtime verification pending)

- The completed fact-review workflow now constructs a clear answer containing monthly kWh/units and, when a confirmed tariff exists, estimated variable cost.
- If the inference engine does not emit an energy conclusion despite complete confirmed inputs, the app uses the same transparent dimensional formula with those confirmed values as a guarded arithmetic fallback.
- If required inputs are genuinely missing or not confirmed, the app now states exactly which values are needed rather than silently showing only extracted facts.
- The answer is rendered immediately below the fact-review section so users do not need to search further down the page.
- Latest app.py change was fetched back from GitHub and verified for the answer-generation and display paths. Automated tests and live Streamlit deployment interaction have not yet been run; runtime verification remains pending.


## Phase 16 — Natural-language appliance quantity and runtime extraction (implemented; verification pending)

- Fixed a real-world extraction gap reported during live user testing: quantity phrases such as “two electric fans” are recognized even when the user does not write “I have”. A singular named appliance in a single-appliance description is represented as one unit, with an explicit confirmation note.
- Expanded daily-runtime extraction to accept approximate wording such as “approximately 8 hours per day” and “around 8 hours daily”. Approximate values remain marked uncertain for explicit user review; they are not silently treated as verified measurements. Per-unit tariff extraction also accepts direct wording such as “at Rs. 55 per kWh”.
- Added two focused regression cases matching the exact fan and refrigerator questions used during acceptance testing, including the singular refrigerator wording that omits an explicit “one”.
- Updated extractor numeric-group handling to safely read the captured value from either supported quantity phrasing.
- Source changes and regression tests were committed. Tests have not been executed, and the deployed Streamlit app has not yet been re-tested; runtime verification remains pending.


## Phase 17 — Complete-question extraction hardening (implemented; verification pending)

- Addressed a second gap exposed by the exact acceptance prompts: users wrote “for 30 days” rather than “30 days per month”. The extractor now interprets that duration as the monthly assessment period when the same question explicitly asks for monthly electricity consumption.
- Added conservative fallback patterns for explicit appliance counts (e.g. “two electric fans”) and operating schedules (e.g. “run for 12 hours daily” and “operates for approximately 8 hours per day”) when the primary patterns do not match.
- Added exact-prompt regression cases for both reported questions, asserting that quantity, rated power, daily runtime, monthly days and tariff are all extracted.
- Changes are committed to the main repository branch. Automated tests have not been run and deployment behaviour is not yet verified.
