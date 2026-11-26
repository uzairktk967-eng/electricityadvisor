"""Streamlit interface for the Smart Home Electricity Advisor."""

from pathlib import Path
import io
import json
import zipfile

import streamlit as st

from consultation import ConsultationSession
from consultation.history import build_history_entry, export_csv, export_html, export_json
from knowledge_base import KNOWLEDGE_FILES, load_documents, validate_documents

ROOT = Path(__file__).resolve().parent
KNOWLEDGE_BASE = ROOT / "knowledge_base"
MAX_HISTORY_ITEMS = 25

st.set_page_config(
    page_title="Smart Home Electricity Advisor",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)


def new_consultation() -> ConsultationSession:
    return ConsultationSession(KNOWLEDGE_BASE)


if "consultation" not in st.session_state:
    st.session_state.consultation = new_consultation()
if "last_result" not in st.session_state:
    st.session_state.last_result = None
if "consultation_history" not in st.session_state:
    st.session_state.consultation_history = []

session: ConsultationSession = st.session_state.consultation


def clear_result() -> None:
    st.session_state.last_result = None


def render_value(value, unit: str | None = None) -> str:
    if isinstance(value, bool):
        rendered = "Yes" if value else "No"
    elif isinstance(value, (int, float)):
        rendered = f"{value:,.2f}"
    else:
        rendered = str(value)
    return f"{rendered} {unit}".strip() if unit else rendered


st.title("⚡ Smart Home Electricity Advisor")
st.write(
    "Understand appliance energy use with transparent calculations, "
    "reviewable evidence and practical, safety-aware guidance."
)

with st.sidebar:
    st.header("Consultation")
    st.caption("One consultation is held in this browser session only.")
    if st.button("Start a new consultation", use_container_width=True):
        st.session_state.consultation = new_consultation()
        st.session_state.last_result = None
        st.rerun()
    st.divider()
    st.markdown("**How it works**")
    st.markdown(
        "1. Describe your appliance or concern.\n"
        "2. Review every extracted fact.\n"
        "3. Add missing details.\n"
        "4. Run the rule-based assessment."
    )
    st.caption(
        "This tool estimates energy use; it does not inspect electrical systems "
        "or guarantee bill savings."
    )

st.subheader("1. Describe your appliance or concern")
with st.form("description_form", clear_on_submit=True):
    description = st.text_area(
        "Describe the appliance, its power rating, usage and any concern",
        placeholder=(
            "Example: My refrigerator has rated power 150 W, "
            "I use it for 8 hours per day, and I have one."
        ),
        height=110,
    )
    submitted_description = st.form_submit_button("Extract details", type="primary")

if submitted_description:
    if not description.strip():
        st.warning("Enter a description before extracting details.")
    else:
        extracted = session.submit_text(description.strip())
        clear_result()
        if extracted:
            st.success(f"Found {len(extracted)} candidate fact(s). Review them below.")
        else:
            st.info(
                "No supported facts were extracted. You can still enter details "
                "using the structured input section."
            )

st.subheader("2. Review extracted facts")
st.caption(
    "Nothing extracted is used in a calculation until you make an explicit decision."
)
if not session.candidates:
    st.info("No extracted facts yet. Describe your appliance above to begin.")
else:
    for index, candidate in enumerate(session.candidates):
        label = session.engine.fact_definitions.get(
            candidate.fact_id, {}
        ).get("description", candidate.fact_id)
        with st.expander(f"Candidate {index + 1}: {label}", expanded=index not in session.reviewed):
            st.write(f"**Proposed value:** {render_value(candidate.value)}")
            st.write(f"**Matched text:** {candidate.matched_text}")
            st.write(f"**Extractor status:** {candidate.status}")
            st.write(f"**Confidence indicator:** {candidate.confidence:.0%} (not a calibrated probability)")
            if candidate.note:
                st.caption(candidate.note)
            if index in session.reviewed:
                st.success(f"Reviewed: {session.reviewed[index]}")
            else:
                left, right = st.columns(2)
                with left:
                    confirm_label = (
                        "Confirm negated statement"
                        if candidate.status == "rejected"
                        else "Confirm this fact"
                    )
                    if st.button(confirm_label, key=f"confirm_{index}", use_container_width=True):
                        session.review_candidate(index, confirm=True)
                        clear_result()
                        st.rerun()
                with right:
                    if st.button("Reject candidate", key=f"reject_{index}", use_container_width=True):
                        session.review_candidate(index, confirm=False)
                        clear_result()
                        st.rerun()

st.subheader("3. Add structured information")
st.write(
    "Use this section for details that were not extracted. "
    "Values are recorded as user-confirmed inputs. If a different value is added for a fact already confirmed, "
    "the system will report conflicting evidence rather than silently replacing the earlier value."
)
fact_definitions = session.engine.fact_definitions
fact_ids = list(fact_definitions)
with st.form("structured_fact_form"):
    selected_fact = st.selectbox(
        "Fact to add",
        fact_ids,
        format_func=lambda fact_id: (
            f"{fact_definitions[fact_id].get('description', fact_id)} "
            f"({fact_id})"
        ),
    )
    definition = fact_definitions[selected_fact]
    kind = definition["type"]
    unit = definition.get("unit")
    if kind == "number" or kind == "integer":
        minimum = definition.get("minimum")
        maximum = definition.get("maximum")
        input_min = float(minimum) if minimum is not None else None
        input_max = float(maximum) if maximum is not None else None
        default_value = input_min if input_min is not None else 0.0
        if kind == "integer":
            structured_value = st.number_input(
                f"Value{f' ({unit})' if unit else ''}",
                min_value=int(input_min) if input_min is not None else None,
                max_value=int(input_max) if input_max is not None else None,
                value=int(default_value),
                step=1,
                format="%d",
            )
        else:
            structured_value = st.number_input(
                f"Value{f' ({unit})' if unit else ''}",
                min_value=input_min,
                max_value=input_max,
                value=default_value,
                step=0.1,
                format="%.2f",
            )
    elif kind == "boolean":
        structured_value = st.selectbox("Value", [True, False], format_func=lambda value: "Yes" if value else "No")
    elif kind == "enum":
        allowed = definition.get("allowed_values", [])
        structured_value = st.selectbox("Value", allowed)
    else:
        structured_value = st.text_input("Value")
    submitted_fact = st.form_submit_button("Add confirmed input")

if submitted_fact:
    if isinstance(structured_value, str) and not structured_value.strip():
        st.warning("Enter a value before adding this fact.")
    else:
        try:
            session.add_fact(selected_fact, structured_value)
            clear_result()
            st.success(f"Added: {definition.get('description', selected_fact)}")
        except (TypeError, ValueError) as exc:
            st.error(f"Input was not accepted: {exc}")

st.subheader("4. Check what information is missing")
target_options = [
    "energy.monthly_kwh_estimate_available",
    "cost.monthly_variable_estimate_available",
    "standby.energy_estimate_available",
]
target = st.selectbox(
    "What would you like to assess?",
    target_options,
    format_func=lambda item: session.engine.conclusion_definitions[item]["description"],
)
if st.button("Find missing information"):
    questions = session.missing_questions(target)
    if questions:
        st.info("Please provide the following details:")
        for item in questions:
            unit_label = f" ({item['unit']})" if item["unit"] else ""
            st.markdown(f"- **{item['question']}**{unit_label}")
    else:
        st.info(
            "No missing fact prompts were returned for this target. "
            "Review the evidence and any blockers below, then run the assessment."
        )

st.subheader("5. Run the assessment")
if st.button("Run electricity assessment", type="primary", use_container_width=True):
    try:
        assessment = session.run()
        st.session_state.last_result = assessment
        history_entry = build_history_entry(session, assessment)
        st.session_state.consultation_history.insert(0, history_entry)
        st.session_state.consultation_history = st.session_state.consultation_history[:MAX_HISTORY_ITEMS]
    except Exception as exc:
        st.error(f"The assessment could not be completed: {exc}")

result = st.session_state.last_result
if result is not None:
    st.divider()
    st.header("Assessment results")

    if result["safety_notice"]:
        st.error(result["safety_notice"])

    conclusions = result["conclusions"]
    if conclusions:
        st.subheader("Rule-supported findings")
        metric_columns = st.columns(min(3, max(1, len(conclusions))))
        for position, (conclusion_id, conclusion) in enumerate(conclusions.items()):
            metadata = session.engine.conclusion_definitions[conclusion_id]
            with metric_columns[position % len(metric_columns)]:
                st.metric(
                    metadata.get("description", conclusion_id),
                    render_value(conclusion["value"], conclusion.get("unit")),
                )
                caveat = conclusion.get("caveat") or metadata.get("caveat")
                if caveat:
                    st.caption(caveat)
    else:
        st.info(
            "No conclusion was derived from the currently confirmed evidence. "
            "Add the missing inputs or resolve conflicting evidence, then run again."
        )

    if result["conflicts"]:
        st.warning("Conflicting evidence or derived values need review.")
        st.json(result["conflicts"])

    st.subheader("Evidence status")
    evidence_rows = [
        {
            "Fact": item["label"],
            "Status": item["status"],
            "Value": render_value(item["value"]) if item["value"] is not None else "—",
            "Records": item["record_count"],
        }
        for item in result["evidence"].values()
        if item["record_count"] > 0
    ]
    if evidence_rows:
        st.dataframe(evidence_rows, use_container_width=True, hide_index=True)
    else:
        st.caption("No facts have been recorded yet.")

    st.subheader("Why did the system reach these findings?")
    if result["explanations"]:
        for explanation in result["explanations"]:
            with st.expander(f"Rule {explanation['rule_id']}"):
                st.write(explanation["explanation"])
                if explanation["limitations"]:
                    st.markdown("**Limitations**")
                    for limitation in explanation["limitations"]:
                        st.write(f"- {limitation}")
    else:
        st.caption("No rules fired for the current evidence.")

    st.subheader("Recommendations")
    if result["recommendations"]:
        for recommendation in result["recommendations"]:
            st.markdown(f"**{recommendation['id']}**")
            st.write(recommendation["text"])
            if recommendation.get("safety_note"):
                st.caption(f"Safety note: {recommendation['safety_note']}")
    else:
        st.caption("No rule-supported recommendations are available yet.")

    st.caption(
        "Energy values are estimates based on the supplied inputs. Cost is a "
        "variable energy-cost estimate using the entered rate, not the complete "
        "electricity bill. Fixed charges, taxes, slabs and adjustments may be excluded. "
        "Savings are not guaranteed."
    )

st.divider()
st.subheader("6. Consultation history and reports")
history_items = st.session_state.consultation_history
st.caption(
    f"{len(history_items)} assessment(s) in this browser session. "
    f"History is limited to the latest {MAX_HISTORY_ITEMS} assessments and is not durable storage."
)
if history_items:
    history_labels = {
        item["assessment_id"]: (
            f"{item['created_at']} — "
            f"{len(item['result'].get('conclusions', {}))} finding(s)"
        )
        for item in history_items
    }
    selected_history_id = st.selectbox(
        "Choose a previous assessment",
        list(history_labels),
        format_func=lambda item_id: history_labels[item_id],
        key="history_selection",
    )
    selected_entry = next(
        item for item in history_items if item["assessment_id"] == selected_history_id
    )
    with st.expander("Previous assessment details", expanded=True):
        st.write(f"**Assessment ID:** {selected_entry['assessment_id']}")
        st.write(f"**Created (UTC):** {selected_entry['created_at']}")
        old_result = selected_entry["result"]
        if old_result.get("safety_notice"):
            st.error(old_result["safety_notice"])
        if old_result.get("conclusions"):
            st.dataframe(
                [
                    {
                        "Conclusion": conclusion_id,
                        "Value": render_value(item.get("value"), item.get("unit")),
                        "Caveat": item.get("caveat") or "",
                    }
                    for conclusion_id, item in old_result["conclusions"].items()
                ],
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.info("This assessment did not derive any conclusions.")
        st.write(f"**Fired rules:** {', '.join(old_result.get('fired_rules', [])) or 'None'}")
        st.write(f"**Recorded evidence entries:** {len(selected_entry.get('facts', []))}")

    safe_id = selected_entry["assessment_id"]
    json_report = export_json(selected_entry)
    csv_report = export_csv(selected_entry)
    html_report = export_html(selected_entry)
    download_cols = st.columns(3)
    with download_cols[0]:
        st.download_button(
            "Download JSON report",
            data=json_report,
            file_name=f"electricity-assessment-{safe_id}.json",
            mime="application/json",
            on_click="ignore",
            use_container_width=True,
        )
    with download_cols[1]:
        st.download_button(
            "Download CSV report",
            data=csv_report,
            file_name=f"electricity-assessment-{safe_id}.csv",
            mime="text/csv",
            on_click="ignore",
            use_container_width=True,
        )
    with download_cols[2]:
        st.download_button(
            "Download printable HTML",
            data=html_report,
            file_name=f"electricity-assessment-{safe_id}.html",
            mime="text/html",
            on_click="ignore",
            use_container_width=True,
        )
    st.caption("Open the HTML report in a browser and choose Print → Save as PDF if you need a PDF copy.")

    all_history_json = export_json({
        "schema_version": "1.0",
        "export_type": "session_history",
        "assessment_count": len(history_items),
        "assessments": history_items,
    })
    st.download_button(
        "Export all session history (JSON)",
        data=all_history_json,
        file_name="electricity-advisor-session-history.json",
        mime="application/json",
        on_click="ignore",
    )

    remove_col, clear_col = st.columns(2)
    with remove_col:
        if st.button("Delete selected history item", use_container_width=True):
            st.session_state.consultation_history = [
                item for item in history_items
                if item["assessment_id"] != safe_id
            ]
            st.rerun()
    with clear_col:
        if st.button("Clear all session history", use_container_width=True):
            st.session_state.consultation_history = []
            st.rerun()
else:
    st.info("Run an assessment to create the first history entry and downloadable report.")

st.caption(
    "Privacy: history is stored only in this active Streamlit session. It is not saved "
    "to a database or shared between users. Exported reports are downloaded to your device; "
    "keep them secure because they contain the values and evidence you entered. "
    "Reloading or ending the session may clear history."
)

st.divider()
st.caption(
    "Privacy and limitations: consultation data is held in Streamlit session state "
    "and is not saved to a project database. Reloading or ending the session may clear it. "
    "The tool does not diagnose electrical faults or provide repair instructions."
)


st.divider()
with st.expander("Knowledge-base Management", expanded=False):
    st.write(
        "Review or prepare changes to the project's JSON knowledge base. "
        "Draft edits are session-only and never overwrite the active files."
    )
    if "kb_draft" not in st.session_state:
        st.session_state.kb_draft = load_documents(KNOWLEDGE_BASE)
    if "kb_editor_revision" not in st.session_state:
        st.session_state.kb_editor_revision = 0
    if "kb_validation" not in st.session_state:
        st.session_state.kb_validation = None

    draft_documents = st.session_state.kb_draft
    document_names = list(KNOWLEDGE_FILES)
    selected_document = st.selectbox(
        "Knowledge-base document",
        document_names,
        format_func=lambda name: f"{name} — {KNOWLEDGE_FILES[name]}",
    )

    st.caption(
        "The JSON Schema is a controlled validation contract and is not editable here. "
        "Choose one of the five domain-data documents to prepare a draft."
    )
    with st.form(f"kb_editor_form_{selected_document}_{st.session_state.kb_editor_revision}"):
        editor_text = st.text_area(
            "JSON draft",
            value=json.dumps(draft_documents[selected_document], indent=2, ensure_ascii=False),
            height=360,
            help="Edit the selected JSON document. Changes are held in this browser session until exported.",
        )
        save_draft = st.form_submit_button("Save changes to session draft")

    if save_draft:
        try:
            parsed_document = json.loads(editor_text)
            if not isinstance(parsed_document, dict):
                raise ValueError("The document root must be a JSON object.")
            st.session_state.kb_draft[selected_document] = parsed_document
            st.session_state.kb_editor_revision += 1
            st.session_state.kb_validation = None
            st.success("Draft updated in this session. Validate the complete knowledge base before export.")
            st.rerun()
        except (json.JSONDecodeError, ValueError) as exc:
            st.error(f"Draft was not saved: {exc}")

    uploaded_document = st.file_uploader(
        "Or upload replacement JSON for the selected document",
        type=["json"],
        key=f"kb_upload_{selected_document}",
    )
    if uploaded_document is not None and st.button(
        "Load uploaded file into session draft",
        key=f"kb_load_upload_{selected_document}",
    ):
        try:
            uploaded_json = json.loads(uploaded_document.getvalue().decode("utf-8"))
            if not isinstance(uploaded_json, dict):
                raise ValueError("The uploaded document root must be a JSON object.")
            st.session_state.kb_draft[selected_document] = uploaded_json
            st.session_state.kb_editor_revision += 1
            st.session_state.kb_validation = None
            st.success("Uploaded JSON loaded into the session draft.")
            st.rerun()
        except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
            st.error(f"Upload was not accepted: {exc}")

    if st.button("Validate complete knowledge base", type="primary"):
        schema_path = KNOWLEDGE_BASE / "schema.json"
        with schema_path.open("r", encoding="utf-8") as schema_file:
            schema_document = json.load(schema_file)
        st.session_state.kb_validation = validate_documents(
            st.session_state.kb_draft,
            schema_document,
        )

    validation = st.session_state.kb_validation
    if validation is not None:
        if validation.is_valid:
            st.success("Validation passed. The complete draft set is structurally and semantically consistent.")
        else:
            st.error(f"Validation found {len(validation.errors)} error(s). Export is disabled.")
            for issue in validation.errors:
                st.write(f"- {issue}")
        if validation.warnings:
            st.warning(f"{len(validation.warnings)} warning(s)")
            for warning in validation.warnings:
                st.write(f"- {warning}")

        if validation.is_valid:
            bundle = io.BytesIO()
            with zipfile.ZipFile(bundle, mode="w", compression=zipfile.ZIP_DEFLATED) as archive:
                for filename in document_names:
                    archive.writestr(
                        filename,
                        json.dumps(st.session_state.kb_draft[filename], indent=2, ensure_ascii=False) + "\n",
                    )
                archive.writestr(
                    "schema.json",
                    (KNOWLEDGE_BASE / "schema.json").read_text(encoding="utf-8"),
                )
                archive.writestr(
                    "VALIDATION.txt",
                    "Knowledge-base draft passed JSON Schema and cross-file semantic validation.\n"
                    "Review the changes and apply them through the repository's normal Git workflow.\n",
                )
            st.download_button(
                "Download validated knowledge-base bundle",
                data=bundle.getvalue(),
                file_name="electricityadvisor-knowledge-base-draft.zip",
                mime="application/zip",
                use_container_width=True,
            )

    st.info(
        "Safety and change control: this screen does not modify active knowledge-base files "
        "or commit to GitHub. Drafts can be lost when the Streamlit session ends. "
        "Review and commit exported changes through GitHub so the repository keeps an audit trail."
    )
