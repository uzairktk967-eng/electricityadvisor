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
| 3 | Core inference engine (forward/backward chaining, matching, conflict handling) | **Implemented; runtime verification deferred until deployment** |
| 4 | Lightweight natural-language processing | **Implemented; runtime verification pending** |
| 5 | Consultation and response engine | Next |
| 6 | Streamlit professional UI | Not started |
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

### Deliverables
- Added `expert_system/fact_store.py` for typed fact validation, provenance, evidence states and contradictory confirmed-value detection.
- Added `expert_system/engine.py` for JSON knowledge-base loading, typed rule matching, forward chaining, backward chaining, allow-listed calculations, priority ordering and inference traces.
- Added `expert_system/models.py` and package exports.
- Added nine standard-library unit tests covering energy/cost calculation, uncertain and rejected evidence, safety referral, standby-specific measurement, contradictory evidence, backward chaining and type validation.
- Added `docs/INFERENCE_ENGINE.md`.
- Formula metadata is never evaluated using Python `eval`; only explicitly registered rule IDs are calculated.

### Verification status
- The nine tests are authored but have not been executed.
- A local clone/test attempt was blocked because the execution environment could not resolve `github.com`.
- Per the developer's chosen workflow, runtime verification of Phases 3 and 4 will be performed after the Streamlit application is deployed. Until then, no test pass is claimed.

## Phase 4 — Lightweight natural-language processing

### Deliverables
- Added `nlp/normalizer.py` for Unicode/case normalization, whitespace cleanup and tokenization.
- Added `nlp/phrase_map.py` and versioned `nlp/domain_phrases.json` for controlled domain vocabulary.
- Added `nlp/extractor.py` to extract explicit appliance, numeric, usage, tariff, schedule, label and electrical-symptom fact candidates.
- Added local negation and uncertainty handling. Extracted facts retain source text, matched text, status, confidence indicator and note.
- Extraction returns candidates only; it does not write to the fact store, infer conclusions or diagnose faults. User confirmation is required before candidates are used by the inference engine.
- Added `tests/test_nlp.py` and `docs/NLP.md`.
- Numeric parsing preserves grouped thousands (for example, 1,500 W) rather than interpreting it as a decimal.

### Verification status
- Nine NLP unit tests are authored but have not been executed.
- Runtime verification is deferred until Streamlit deployment, as agreed with the developer.

## Current next phase

**Phase 5 — Consultation and response engine.** It will connect reviewed NLP candidates to the fact store and inference engine, ask for missing or ambiguous inputs, and assemble evidence-based explanations. Do not start Phase 6 until Phase 5 is completed and documented.
