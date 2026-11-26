"""Tests for session history snapshots and report exports."""

import csv
import json
import unittest
from io import StringIO
from pathlib import Path

from consultation import ConsultationSession
from consultation.history import build_history_entry, export_csv, export_html, export_json

ROOT = Path(__file__).resolve().parents[1]


class ConsultationHistoryTests(unittest.TestCase):
    def setUp(self):
        self.session = ConsultationSession(ROOT / "knowledge_base")
        self.session.add_fact("appliance.rated_power_w", 100, source="manufacturer_label")
        self.session.add_fact("appliance.quantity", 1)
        self.session.add_fact("usage.hours_per_day", 5)
        self.session.add_fact("usage.days_per_month", 30)
        self.result = self.session.run()
        self.entry = build_history_entry(self.session, self.result)

    def test_history_snapshot_has_unique_id_and_timestamp(self):
        second = build_history_entry(self.session, self.result)
        self.assertNotEqual(self.entry["assessment_id"], second["assessment_id"])
        self.assertTrue(self.entry["created_at"].endswith("+00:00"))

    def test_snapshot_preserves_fact_provenance_and_derived_results(self):
        fact = next(item for item in self.entry["facts"] if item["fact_id"] == "appliance.rated_power_w")
        self.assertEqual(fact["source"], "manufacturer_label")
        self.assertEqual(fact["status"], "confirmed")
        self.assertAlmostEqual(
            self.entry["result"]["conclusions"]["energy.monthly_kwh_estimate_available"]["value"],
            15.0,
        )

    def test_json_export_round_trips(self):
        exported = export_json(self.entry)
        restored = json.loads(exported)
        self.assertEqual(restored["assessment_id"], self.entry["assessment_id"])
        self.assertEqual(restored["facts"], self.entry["facts"])

    def test_csv_export_contains_facts_findings_and_explanations(self):
        rows = list(csv.DictReader(StringIO(export_csv(self.entry))))
        types = {row["record_type"] for row in rows}
        self.assertIn("fact", types)
        self.assertIn("conclusion", types)
        self.assertIn("rule_explanation", types)


    def test_csv_export_neutralizes_spreadsheet_formulas(self):
        malicious = dict(self.entry)
        malicious["facts"] = [{
            "fact_id": "test.fact",
            "label": '=HYPERLINK("https://example.invalid")',
            "value": "normal",
            "status": "confirmed",
            "source": "test",
            "note": "",
        }]
        rows = list(csv.DictReader(StringIO(export_csv(malicious))))
        self.assertEqual(rows[0]["label"], '\'=HYPERLINK("https://example.invalid")')

    def test_csv_export_neutralizes_formula_after_leading_whitespace(self):
        malicious = dict(self.entry)
        malicious["facts"] = [{
            "fact_id": "test.fact",
            "label": '  =SUM(1,1)',
            "value": "normal",
            "status": "confirmed",
            "source": "test",
            "note": "",
        }]
        rows = list(csv.DictReader(StringIO(export_csv(malicious))))
        self.assertEqual(rows[0]["label"], "'  =SUM(1,1)")

    def test_html_report_escapes_untrusted_fact_values(self):
        # Exercise escaping independently of the catalogue's normal type constraints.
        malicious = dict(self.entry)
        malicious["facts"] = [{
            "label": "<script>alert(1)</script>",
            "value": "<img src=x onerror=alert(1)>",
            "status": "confirmed",
            "source": "test",
        }]
        report = export_html(malicious)
        self.assertNotIn("<script>alert(1)</script>", report)
        self.assertNotIn("<img src=x onerror=alert(1)>", report)
        self.assertIn("&lt;script&gt;", report)

    def test_html_report_includes_print_action_and_disclosures(self):
        report = export_html(self.entry)
        self.assertIn("window.print()", report)
        self.assertIn("not a utility bill", report)
        self.assertIn("Evidence records", report)

    def test_report_handles_no_findings_or_facts(self):
        empty = {
            "assessment_id": "empty",
            "created_at": "2026-01-01T00:00:00+00:00",
            "facts": [],
            "result": {"conclusions": {}, "explanations": [], "recommendations": [], "conflicts": []},
            "disclosures": [],
        }
        self.assertIn("No facts were recorded", export_html(empty))
        self.assertIn("No rule-supported conclusions", export_html(empty))


if __name__ == "__main__":
    unittest.main()
