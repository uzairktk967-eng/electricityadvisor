# Smart Home Electricity Advisor

A rule-based, explainable application for estimating household appliance energy use and presenting evidence-supported guidance.

## Features

- Describe an appliance or concern in natural language.
- Review and explicitly confirm or reject extracted fact candidates.
- Add validated facts through structured inputs.
- Identify missing information for energy, variable-cost and standby estimates.
- View rule-supported findings, evidence status, conflicts, explanations and recommendations.
- Receive a safety referral when electrical warning symptoms are reported.

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

The Streamlit entry point is `app.py`. For Streamlit Community Cloud, select this repository, branch `main`, and main file path `app.py`. The dependency is declared in the root `requirements.txt`.

See [Streamlit UI and deployment notes](docs/STREAMLIT_UI.md).

## Architecture

- `knowledge_base/`: versioned JSON facts, rules, conclusions and recommendations.
- `expert_system/`: evidence-aware forward and backward chaining.
- `nlp/`: constrained natural-language fact candidate extraction.
- `consultation/`: review workflow and response assembly.
- `app.py`: Streamlit presentation layer.
- `tests/`: unit tests authored for the reasoning and consultation components.

The UI calls the consultation service; it does not implement its own reasoning rules.

## Important limitations

- Energy and cost values are estimates based on user-supplied information.
- Cost is a variable energy-cost estimate, not a complete electricity bill.
- Savings are not guaranteed.
- Electrical faults are not diagnosed. Warning symptoms should be referred to a qualified electrician.
- Consultation data is held in session state only; durable history and database storage are not implemented.
- Automated tests have been authored but are intentionally deferred until deployment testing. No test-pass claim is made.

See `PROJECT_PROGRESS.md` for the phase-by-phase development status.
