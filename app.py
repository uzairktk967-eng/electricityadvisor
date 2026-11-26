"""Streamlit interface for the Smart Home Electricity Advisor."""

from pathlib import Path

import streamlit as st

from consultation import ConsultationSession

ROOT = Path(__file__).resolve().parent
KNOWLEDGE_BASE = ROOT / "knowledge_base"

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
        structured_value = st.number_input(
            f"Value{f' ({unit})' if unit else ''}",
            min_value=input_min,
            max_value=input_max,
            value=default_value,
            step=1.0 if kind == "integer" else 0.1,
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
        st.session_state.last_result = session.run()
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
st.caption(
    "Privacy and limitations: consultation data is held in Streamlit session state "
    "and is not saved to a project database. Reloading or ending the session may clear it. "
    "The tool does not diagnose electrical faults or provide repair instructions."
)
