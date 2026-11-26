# Streamlit User Interface

## Run locally

From the repository root:

```bash
python -m venv .venv
# Windows:
.venv\\Scripts\\activate
# macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt
streamlit run app.py
```

The app entry point is `app.py`. The knowledge base remains in `knowledge_base/`; the UI calls the existing `ConsultationSession` service and does not implement inference rules itself.

## Consultation flow

1. A user describes an appliance or electricity concern.
2. NLP-extracted candidates are displayed with matched text, extractor status and a confidence indicator.
3. Each candidate requires an explicit confirm or reject action. A negated candidate is labelled so that confirming the statement does not mistakenly confirm the underlying proposition.
4. The structured input form reads the fact catalogue and supports string, numeric, boolean and enumerated facts.
5. Backward-chaining prompts can identify missing information for energy, variable-cost and standby estimates.
6. The user runs forward chaining and sees derived findings, evidence status, conflicts, fired-rule explanations, limitations, recommendations and any safety referral.

## State and privacy

A `ConsultationSession` is held in Streamlit session state for the active browser session. There is no database, durable history, user account or report export in this phase. Session state is not persistent storage; a reload or disconnected session can clear the consultation.

## Estimate and safety disclosures

- Monthly energy is an estimate based on entered power, quantity and usage.
- Cost is a variable energy-cost estimate based on the user-entered rate. It is not the complete electricity bill and may exclude fixed charges, taxes, slabs, duties and adjustments.
- No savings are guaranteed.
- Electrical warning symptoms trigger referral to a qualified electrician. The app does not diagnose wiring faults or provide repair instructions.
- Extractor confidence is an indicator, not a calibrated probability. Candidates are not used until explicitly reviewed.

## Deployment entry point

For Streamlit Community Cloud, select repository `uzairktk967-eng/electricityadvisor`, branch `main`, and main file path `app.py`. The root `requirements.txt` declares the Python dependency. Follow the current Streamlit deployment instructions and review deployment logs after launch.
