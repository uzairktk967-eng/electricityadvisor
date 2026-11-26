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

## Supported phrasing and boundaries

Numeric extraction recognizes common alternatives for rated power (for example, “rated at 80 W”), runtime (for example, “runs 10 hours daily” and “operates for 4.5 hours a day”), quantities including simple number words, days per month, and tariff wording such as “Rs. 55 per kWh”. Values remain candidates and require explicit user review.

The current fact catalogue represents one appliance profile per consultation. Do not submit multiple different appliances with different wattages or runtimes as one paragraph: the existing single-value evidence model cannot safely associate each value with its appliance. Assess each appliance separately until a dedicated multi-appliance workflow is implemented.

This remains a small deterministic vocabulary, not a general conversational model. It may miss unlisted paraphrases, ambiguous sentence structures, or negation outside its local context window. Candidate review is mandatory. Expand the phrase catalogue and tests only with documented domain examples.
```
