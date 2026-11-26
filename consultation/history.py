"""Session-scoped consultation history and portable report exports.

This module deliberately avoids filesystem/database persistence. It creates
JSON-safe snapshots from the consultation service and builds downloadable
JSON, CSV and self-contained HTML reports.
"""

from __future__ import annotations

import csv
import html
import io
import json
import uuid
from datetime import datetime, timezone
from typing import Any


def _json_safe(value: Any) -> Any:
    """Convert supported Python values into JSON-safe primitives."""
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, dict):
        return {str(key): _json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_safe(item) for item in value]
    if hasattr(value, "isoformat"):
        return value.isoformat()
    return str(value)


def build_history_entry(session, result: dict[str, Any]) -> dict[str, Any]:
    """Build an immutable, portable snapshot of one completed assessment."""
    fact_records = []
    for fact_id, records in session.store.all_records().items():
        definition = session.engine.fact_definitions.get(fact_id, {})
        for record in records:
            fact_records.append({
                "fact_id": fact_id,
                "label": definition.get("description", fact_id),
                "value": _json_safe(record.value),
                "status": record.status,
                "source": record.source,
                "note": record.note,
            })

    now = datetime.now(timezone.utc)
    return {
        "schema_version": "1.0",
        "assessment_id": str(uuid.uuid4()),
        "created_at": now.isoformat(timespec="seconds"),
        "application": "Smart Home Electricity Advisor",
        "disclosures": [
            "Energy values are estimates based on supplied inputs.",
            "Variable energy cost is not a complete electricity bill.",
            "Savings are not guaranteed.",
            "This report is informational and is not an electrical safety inspection.",
        ],
        "facts": fact_records,
        "result": _json_safe(result),
    }


def export_json(entry: dict[str, Any]) -> str:
    """Serialize a single report or a history collection as readable JSON."""
    return json.dumps(_json_safe(entry), ensure_ascii=False, indent=2) + "\n"


def export_csv(entry: dict[str, Any]) -> str:
    """Export a normalized, spreadsheet-friendly view of a single report."""
    output = io.StringIO(newline="")
    columns = [
        "record_type", "record_id", "label", "value", "unit",
        "status", "source", "note", "details",
    ]
    writer = csv.DictWriter(output, fieldnames=columns)
    writer.writeheader()
    result = entry.get("result", {})

    for fact in entry.get("facts", []):
        writer.writerow({
            "record_type": "fact",
            "record_id": fact.get("fact_id", ""),
            "label": fact.get("label", ""),
            "value": json.dumps(fact.get("value"), ensure_ascii=False),
            "status": fact.get("status", ""),
            "source": fact.get("source", ""),
            "note": fact.get("note", ""),
        })

    for conclusion_id, conclusion in result.get("conclusions", {}).items():
        writer.writerow({
            "record_type": "conclusion",
            "record_id": conclusion_id,
            "label": conclusion_id,
            "value": json.dumps(conclusion.get("value"), ensure_ascii=False),
            "unit": conclusion.get("unit") or "",
            "status": "derived",
            "details": conclusion.get("caveat") or "",
        })

    for explanation in result.get("explanations", []):
        writer.writerow({
            "record_type": "rule_explanation",
            "record_id": explanation.get("rule_id", ""),
            "label": explanation.get("conclusion", ""),
            "status": "fired",
            "details": explanation.get("explanation", ""),
            "note": " | ".join(explanation.get("limitations", [])),
        })

    for recommendation in result.get("recommendations", []):
        writer.writerow({
            "record_type": "recommendation",
            "record_id": recommendation.get("id", ""),
            "label": recommendation.get("id", ""),
            "status": "rule_supported",
            "details": recommendation.get("text", ""),
        })

    for conflict in result.get("conflicts", []):
        writer.writerow({
            "record_type": "conflict",
            "record_id": conflict.get("rule_id") or conflict.get("conclusion") or "",
            "status": "requires_review",
            "details": json.dumps(conflict, ensure_ascii=False),
        })

    if result.get("safety_notice"):
        writer.writerow({
            "record_type": "safety_notice",
            "record_id": "safety.professional_inspection_required",
            "status": "referral",
            "details": result["safety_notice"],
        })

    return output.getvalue()


def export_html(entry: dict[str, Any]) -> str:
    """Create a self-contained, escaped HTML report suitable for printing."""
    result = entry.get("result", {})
    esc = lambda value: html.escape(str(value if value is not None else ""))
    findings = []
    for conclusion_id, conclusion in result.get("conclusions", {}).items():
        value = conclusion.get("value")
        unit = conclusion.get("unit") or ""
        caveat = conclusion.get("caveat") or ""
        findings.append(
            "<tr><td>" + esc(conclusion_id) + "</td><td>" +
            esc(value) + " " + esc(unit) + "</td><td>" + esc(caveat) + "</td></tr>"
        )
    if not findings:
        findings.append('<tr><td colspan="3">No rule-supported conclusions were derived.</td></tr>')

    facts = []
    for fact in entry.get("facts", []):
        facts.append(
            "<tr><td>" + esc(fact.get("label")) + "</td><td>" +
            esc(fact.get("value")) + "</td><td>" + esc(fact.get("status")) +
            "</td><td>" + esc(fact.get("source")) + "</td></tr>"
        )
    if not facts:
        facts.append('<tr><td colspan="4">No facts were recorded.</td></tr>')

    explanations = []
    for item in result.get("explanations", []):
        limits = "; ".join(item.get("limitations", []))
        explanations.append(
            "<li><strong>" + esc(item.get("rule_id")) + "</strong>: " +
            esc(item.get("explanation")) + "<br><em>Limitations: " +
            esc(limits) + "</em></li>"
        )
    if not explanations:
        explanations.append("<li>No rules fired.</li>")

    recommendations = []
    for item in result.get("recommendations", []):
        recommendations.append(
            "<li><strong>" + esc(item.get("id")) + "</strong>: " +
            esc(item.get("text")) + "</li>"
        )
    if not recommendations:
        recommendations.append("<li>No rule-supported recommendations.</li>")

    conflicts = [
        "<li>" + esc(json.dumps(item, ensure_ascii=False)) + "</li>"
        for item in result.get("conflicts", [])
    ]
    if not conflicts:
        conflicts.append("<li>No conflicts recorded.</li>")

    safety = ""
    if result.get("safety_notice"):
        safety = '<section class="warning"><h2>Electrical safety notice</h2><p>' + esc(result["safety_notice"]) + "</p></section>"

    disclosures = "".join("<li>" + esc(item) + "</li>" for item in entry.get("disclosures", []))
    return """<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Electricity Advisor Assessment Report</title>
<style>
body{font-family:Arial,sans-serif;max-width:950px;margin:36px auto;padding:0 20px;color:#202124;line-height:1.5}
h1,h2{color:#17365d}table{border-collapse:collapse;width:100%;margin:12px 0 24px}
th,td{border:1px solid #d5d9df;padding:8px;text-align:left;vertical-align:top}
th{background:#eef2f7}.warning{border-left:5px solid #b42318;padding:8px 16px;background:#fff4f2}
.meta{color:#555;font-size:.9rem}.disclaimer{background:#f5f6f7;padding:12px}
@media print{body{margin:0;max-width:none}.no-print{display:none}}
</style></head><body>
<h1>Smart Home Electricity Advisor</h1>
<p class="meta">Assessment ID: """ + esc(entry.get("assessment_id")) + """<br>
Created (UTC): """ + esc(entry.get("created_at")) + """</p>
""" + safety + """
<h2>Rule-supported findings</h2>
<table><thead><tr><th>Conclusion</th><th>Estimated value</th><th>Caveat</th></tr></thead>
<tbody>""" + "".join(findings) + """</tbody></table>
<h2>Evidence records</h2>
<table><thead><tr><th>Fact</th><th>Value</th><th>Status</th><th>Source</th></tr></thead>
<tbody>""" + "".join(facts) + """</tbody></table>
<h2>Reasoning and limitations</h2><ul>""" + "".join(explanations) + """</ul>
<h2>Recommendations</h2><ul>""" + "".join(recommendations) + """</ul>
<h2>Conflicts</h2><ul>""" + "".join(conflicts) + """</ul>
<section class="disclaimer"><h2>Important disclosures</h2><ul>""" + disclosures + """</ul></section>
<p class="meta">This report is generated from user-supplied evidence and the application's current rule base. It is not a utility bill, electrical inspection or guarantee of savings.</p>
<p class="no-print"><button onclick="window.print()">Print / Save as PDF</button></p>
</body></html>"""
