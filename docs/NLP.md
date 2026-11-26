# Lightweight Natural-Language Processing

## Scope

The NLP package converts a limited set of explicit household-electricity phrases into reviewable fact candidates. It does not diagnose faults, calculate conclusions, or call the inference engine. The caller must ask the user to confirm candidates before adding them to the fact store.

## Modules

- `nlp/normalizer.py`: Unicode/case normalization, whitespace cleanup and tokenization.
- `nlp/phrase_map.py`: controlled phrase catalogue matching.
- `nlp/extractor.py`: explicit numeric patterns, phrase extraction, local negation/uncertainty checks and candidate metadata.
- `nlp/domain_phrases.json`: versioned phrase-to-fact vocabulary.
- `tests/test_nlp.py`: standard-library tests for representative extraction behavior.

## API

```python
from nlp import extract_facts

candidates = extract_facts(
    "My refrigerator has rated power 150 W and runs for 8 hours per day."
)
for candidate in candidates:
    print(candidate.to_dict())
```

A candidate includes the fact ID, proposed value, evidence status, original input, matched text, confidence and a note. Confidence is a deterministic rule-based indicator, not a calibrated probability.

## Evidence safeguards

- Numeric values are extracted only when paired with a recognized label and unit.
- Approximation/uncertainty wording produces an `uncertain` candidate.
- Negated boolean phrases produce `rejected` candidates.
- Unrecognized text produces no candidate rather than a guessed fact.
- Extraction never writes to `FactStore` and never fires inference rules.
- Electrical warning phrases are flagged for professional referral; the NLP layer provides no repair instructions.

## Limitations

This is a small deterministic vocabulary, not a general conversational model. It may miss paraphrases, ambiguous sentence structures, multiple appliances in one sentence, or negation outside its local context window. Candidate review is mandatory. Expand the phrase catalogue and tests only with documented domain examples.
```
