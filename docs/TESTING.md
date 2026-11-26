# Testing and Verification Plan

## Current status

Automated tests are authored but have not been executed in this development workflow. The developer requested runtime testing after Streamlit deployment. Do not describe the suite as passing until it has actually been run and its output reviewed.

The current authored suite contains:

| Test module | Coverage | Tests |
|---|---|---:|
| `tests/test_inference_engine.py` | Forward/backward chaining, calculations, evidence states, conflicts and type validation | 9 |
| `tests/test_nlp.py` | Normalization, extraction, numeric parsing, uncertainty and negation | 9 |
| `tests/test_consultation.py` | Candidate review, structured facts, missing questions and response assembly | 8 |
| `tests/test_knowledge_base.py` | JSON Schema and cross-file validation | 6 |
| `tests/test_end_to_end.py` | Complete consultation scenarios and explanation contract | 10 |
| `tests/test_history.py` | Session snapshots, provenance, JSON/CSV/HTML exports and output safety | 8 |
| **Total** | | **51** |

## Run locally or after deployment

From the repository root:

```bash
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
```

The app can be started locally with:

```bash
streamlit run app.py
```

Streamlit Community Cloud deployment does not itself execute the repository's unit tests. Run the test command in a Python environment with the repository checked out.

## End-to-end acceptance checklist

- [ ] Application starts and imports all packages.
- [ ] Empty natural-language input is handled without an exception.
- [ ] Extracted candidates remain unused until an explicit review decision.
- [ ] Confirmed facts retain provenance; uncertain/rejected/conflicting facts do not satisfy rules.
- [ ] Energy and variable-cost calculations match hand-calculated examples.
- [ ] Standby calculations require standby-specific power.
- [ ] Missing-information questions identify prerequisites for energy and cost estimates.
- [ ] Electrical warning symptoms produce a professional referral.
- [ ] Findings show their rule explanations, limitations and evidence status.
- [ ] Recommendations appear only when their supporting rule fires.
- [ ] Invalid knowledge-base drafts cannot be exported.
- [ ] Valid knowledge-base drafts export without modifying active repository files.
- [ ] Session reset clears the consultation and its displayed result.
- [ ] No user data is represented as durably saved.
- [ ] Each completed assessment creates one immutable history snapshot with a unique ID and UTC timestamp.
- [ ] Session history is capped at 25 items; deleting one or all entries updates the visible history.
- [ ] JSON, CSV and printable HTML reports contain the expected facts, findings and disclosures.
- [ ] HTML report values are escaped and CSV formula-like text is neutralized.
- [ ] Exporting reports does not cause an unintended assessment rerun or duplicate history entry.
- [ ] Integer structured facts are submitted as integers and accepted by fact validation.
- [ ] CSV formula-like text remains neutralized when whitespace precedes the formula marker.

## Regression and safety review

For each change to a rule, fact definition, formula or extractor pattern:

1. Add a focused test for the intended behavior.
2. Add or update an end-to-end scenario when the user-visible result changes.
3. Check both positive and negative evidence cases.
4. Verify that explanations and limitations remain connected to the firing rule.
5. Check that no formula metadata is executed as code.
6. Revisit the safety referral and bill-estimate caveats.

Record the command, environment, date and complete test summary when tests are eventually executed. Distinguish failures, skipped tests and tests not run.
