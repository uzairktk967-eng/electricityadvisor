# Core Inference Engine

## Scope

This phase adds a Python symbolic reasoning engine that reads the Phase 2 JSON knowledge base. It does not include the Streamlit UI, natural-language processing, consultation flow or deployment.

## Modules

- `expert_system/fact_store.py`: typed facts, evidence statuses, provenance and contradictory-evidence detection.
- `expert_system/engine.py`: knowledge-base loading, rule matching, forward chaining, backward chaining and trace generation.
- `expert_system/models.py`: result data structures.
- `tests/test_inference_engine.py`: unit tests for representative reasoning scenarios.

## Evidence behavior

Only a single, non-conflicting confirmed value can satisfy a rule condition. Uncertain, rejected, missing and contradictory evidence do not match. Contradictory confirmed values are retained and reported as conflicts instead of silently selecting one.

## Forward chaining

The engine evaluates rules in descending priority order, then rule-ID order for deterministic behavior. Conditions in each rule use AND logic. A rule with a prerequisite conclusion waits until that conclusion has been derived. It continues until no new rule fires or the configured iteration limit is reached.

All valid conclusions are retained. Priority is recorded for traceability and does not suppress independent conclusions.

## Backward chaining

For a target conclusion, the engine examines rules that can derive it, recursively checks prerequisite conclusions and identifies missing/uncertain/rejected facts or conditions that currently block each route. Multiple rules are represented as alternative derivation paths.

## Calculation safety

Formula metadata is never passed to Python `eval`. Only explicitly registered rule IDs have calculation implementations. The initial calculations are monthly energy, variable energy cost and standby energy. Unknown formula-bearing rules fail closed with a knowledge-base error.

## Run tests

From the repository root:

```bash
python -m unittest discover -s tests -v
```

The tests use Python's standard library and require no third-party package.

## Known limitations

- The initial calculation registry is intentionally small and tied to the current starter rule set.
- Backward chaining is a goal-directed evidence planner, not a general Prolog implementation.
- The engine is a library; there is no user interface or natural-language interface yet.
- Schema validation and broad knowledge-base consistency testing will be expanded in the dedicated validation/testing phase.
