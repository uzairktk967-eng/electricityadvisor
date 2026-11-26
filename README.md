# Smart Home Electricity Advisor

A rule-based, explainable application for estimating household appliance energy use and presenting evidence-supported guidance.

## Features

- Describe an appliance or concern in natural language.
- Review and explicitly confirm or reject extracted fact candidates.
- Add validated facts through structured inputs.
- Identify missing information for energy, variable-cost and standby estimates.
- View rule-supported findings, evidence status, conflicts, explanations and recommendations.
- Receive a safety referral when electrical warning symptoms are reported.
- Prepare knowledge-base JSON drafts, validate schema and cross-file references, and export a validated bundle.
- Review the latest 25 completed assessments within the active browser session.
- Export individual assessment reports as JSON, CSV or printable HTML; export session history as JSON.

## Run locally

Python 3.10+ is recommended.

```bash
python -m venv .venv
# Windows:
.venv\\Scripts\\activate
# macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt
streamlit run app.py
```

## Deploy

The Streamlit entry point is `app.py`. For Streamlit Community Cloud, select this repository, branch `main`, and main file path `app.py`. Dependencies are declared in the root `requirements.txt`.

See [Streamlit UI and deployment notes](docs/STREAMLIT_UI.md), [Knowledge-Base Management](docs/KNOWLEDGE_BASE_MANAGEMENT.md), [History and Reports](docs/HISTORY_AND_REPORTS.md), and [Testing Plan](docs/TESTING.md), and [Final Audit and Deployment Guide](docs/FINAL_AUDIT.md).

## Architecture

- `knowledge_base/`: JSON facts, rules, conclusions, recommendations, schema and draft validation.
- `expert_system/`: evidence-aware forward and backward chaining.
- `nlp/`: constrained natural-language fact candidate extraction.
- `consultation/`: review workflow, response assembly, session history snapshots and report exports.
- `app.py`: Streamlit consultation and knowledge-base management interface.
- `tests/`: authored unit, integration, end-to-end and report-export regression tests (51 total; execution pending deployment).

The UI calls the consultation service; it does not implement its own reasoning rules.

## Important limitations

- Energy and cost values are estimates based on user-supplied information.
- Cost is a variable energy-cost estimate, not a complete electricity bill.
- Savings are not guaranteed.
- Electrical faults are not diagnosed. Warning symptoms should be referred to a qualified electrician.
- Consultation data and knowledge-base drafts are held in session state only; they are not saved to a project database.
- The knowledge-base editor does not modify active repository files or commit to GitHub. Exported changes must be reviewed and committed through the normal Git workflow.
- Automated tests have been authored but are intentionally deferred until deployment testing. No test-pass claim is made.

See `PROJECT_PROGRESS.md` for the phase-by-phase development status.
