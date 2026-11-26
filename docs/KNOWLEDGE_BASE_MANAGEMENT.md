# Knowledge-Base Management

## Scope

The management workflow provides a reviewable draft of the JSON knowledge base. It does not silently rewrite the active files or commit changes to GitHub.

Editable documents:
- `facts.json`
- `categories.json`
- `conclusions.json`
- `recommendations.json`
- `rules.json`

The JSON Schema (`schema.json`) remains a controlled structural contract and is not editable through the ordinary management screen.

## Validation

`knowledge_base/manager.py` performs:
1. JSON Schema Draft 2020-12 validation for each document.
2. Unique-ID checks within each collection.
3. Cross-file category, fact, conclusion and recommendation reference checks.
4. Operator/fact-type compatibility checks.
5. Numeric bound and enum consistency checks.
6. Recommendation-to-rule linkage and orphan recommendation warnings.
7. Prerequisite dependency cycle detection.
8. Exact allow-list checks for calculation formula metadata. Formula strings are never executed.

A draft is exportable only when the full five-file set passes validation. Warnings are shown separately and do not silently change data.

## Streamlit workflow

Open the Knowledge-Base Management section in the app:
1. Select a JSON document.
2. Edit its JSON text or upload a replacement for that document.
3. Validate the complete draft set.
4. Download a ZIP bundle only if validation succeeds.

The active knowledge-base files are not modified by the browser editor. This prevents an unauthenticated public app visitor from changing the live rules. To apply changes, review the downloaded files and submit them through the repository's normal Git workflow, retaining version history and code review.

## Deployment and persistence

Streamlit Community Cloud's application filesystem should not be treated as a durable administrative database. Drafts are held in the active Streamlit session and may be lost when the session ends. The app does not write knowledge-base changes to disk or automatically commit to GitHub.

## Limitations

- The validator checks consistency against the current schema and inference-engine formula allow-list; it does not prove that domain rules are scientifically correct.
- Adding a new formula requires a deliberate implementation in the inference engine and a matching validator allow-list entry. Arbitrary expressions are rejected.
- The workflow is not a multi-user approval system. Repository review remains the change-control mechanism.
