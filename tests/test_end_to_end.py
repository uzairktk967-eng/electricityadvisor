"""End-to-end scenarios across evidence review, consultation and inference.

These tests are authored for execution after Streamlit deployment, as requested.
They intentionally exercise public package interfaces rather than Streamlit widgets.
"""

import unittest
from pathlib import Path

from consultation import ConsultationSession

ROOT = Path(__file__).resolve().parents[1]
KB = ROOT / "knowledge_base"


class EndToEndConsultationTests(unittest.TestCase):
    def setUp(self):
        self.session = ConsultationSession(KB)

    def add_energy_inputs(self, *, power=100, quantity=2, hours=5, days=30):
        self.session.add_fact("appliance.rated_power_w", power)
        self.session.add_fact("appliance.quantity", quantity)
        self.session.add_fact("usage.hours_per_day", hours)
        self.session.add_fact("usage.days_per_month", days)

    def test_energy_and_variable_cost_are_explained_end_to_end(self):
        self.add_energy_inputs()
        self.session.add_fact("tariff.price_per_kwh", 40)
        response = self.session.run()

        energy = response["conclusions"]["energy.monthly_kwh_estimate_available"]
        cost = response["conclusions"]["cost.monthly_variable_estimate_available"]
        self.assertAlmostEqual(energy["value"], 30.0)
        self.assertAlmostEqual(cost["value"], 1200.0)
        self.assertIn("R-ENERGY-001", response["fired_rules"])
        self.assertIn("R-COST-001", response["fired_rules"])
        self.assertEqual(
            {item["rule_id"] for item in response["explanations"]},
            {"R-ENERGY-001", "R-COST-001"},
        )
        self.assertTrue(all(item["explanation"] for item in response["explanations"]))
        self.assertTrue(all(item["limitations"] for item in response["explanations"]))
        self.assertEqual(len(response["recommendations"]), 2)

    def test_cost_is_not_derived_without_user_tariff(self):
        self.add_energy_inputs()
        response = self.session.run()
        self.assertIn("energy.monthly_kwh_estimate_available", response["conclusions"])
        self.assertNotIn("cost.monthly_variable_estimate_available", response["conclusions"])
        self.assertNotIn("R-COST-001", response["fired_rules"])

    def test_natural_language_candidates_require_review_before_inference(self):
        self.session.submit_text(
            "My refrigerator has rated power 100 W and runs 5 hours per day."
        )
        before_review = self.session.run()
        self.assertNotIn("energy.monthly_kwh_estimate_available", before_review["conclusions"])
        for index in range(len(self.session.candidates)):
            self.session.review_candidate(index, confirm=True)
        self.session.add_fact("appliance.quantity", 1)
        self.session.add_fact("usage.days_per_month", 30)
        after_review = self.session.run()
        self.assertIn("energy.monthly_kwh_estimate_available", after_review["conclusions"])

    def test_conflicting_power_values_block_energy_estimate(self):
        self.session.add_fact("appliance.rated_power_w", 100)
        self.session.add_fact("appliance.rated_power_w", 200)
        self.session.add_fact("appliance.quantity", 1)
        self.session.add_fact("usage.hours_per_day", 5)
        self.session.add_fact("usage.days_per_month", 30)
        response = self.session.run()
        self.assertNotIn("energy.monthly_kwh_estimate_available", response["conclusions"])
        self.assertTrue(response["conflicts"])

    def test_uncertain_power_does_not_support_energy_estimate(self):
        self.session.store.add(
            "appliance.rated_power_w", 100, status="uncertain", source="uncertain_user_statement"
        )
        self.session.add_fact("appliance.quantity", 1)
        self.session.add_fact("usage.hours_per_day", 5)
        self.session.add_fact("usage.days_per_month", 30)
        response = self.session.run()
        self.assertNotIn("energy.monthly_kwh_estimate_available", response["conclusions"])

    def test_standby_estimate_uses_standby_specific_power(self):
        self.session.add_fact("appliance.measured_power_w", 100)
        self.session.add_fact("appliance.quantity", 2)
        self.session.add_fact("usage.standby_hours_per_day", 12)
        self.session.add_fact("usage.days_per_month", 30)
        self.assertNotIn(
            "standby.energy_estimate_available", self.session.run()["conclusions"]
        )
        self.session.add_fact("appliance.standby_power_w", 2, source="standby_meter_reading")
        response = self.session.run()
        self.assertAlmostEqual(
            response["conclusions"]["standby.energy_estimate_available"]["value"], 1.44
        )

    def test_electrical_warning_produces_professional_referral(self):
        self.session.add_fact("supply.has_electrical_symptom", True)
        response = self.session.run()
        self.assertIsNotNone(response["safety_notice"])
        self.assertIn("R-SAFETY-001", response["fired_rules"])
        self.assertTrue(any(item["id"] == "rec.contact_electrician" for item in response["recommendations"]))

    def test_flexible_schedule_is_only_a_review_candidate(self):
        self.session.add_fact("usage.schedule_flexible", True)
        self.session.add_fact("usage.hours_per_day", 4)
        response = self.session.run()
        self.assertIn("usage.schedule_review_candidate", response["conclusions"])
        self.assertIn("R-USAGE-001", response["fired_rules"])

    def test_energy_label_triggers_comparison_not_efficiency_ranking(self):
        self.session.add_fact("appliance.has_energy_label", True)
        response = self.session.run()
        self.assertIn("efficiency.specification_comparison_advised", response["conclusions"])
        self.assertIn("R-EFF-001", response["fired_rules"])
        self.assertTrue(any(item["id"] == "rec.compare_energy_labels" for item in response["recommendations"]))

    def test_backward_questions_for_cost_include_energy_inputs_and_tariff(self):
        questions = self.session.missing_questions(
            "cost.monthly_variable_estimate_available"
        )
        missing = {item["fact_id"] for item in questions}
        self.assertEqual(
            missing,
            {
                "appliance.rated_power_w",
                "appliance.quantity",
                "usage.hours_per_day",
                "usage.days_per_month",
                "tariff.price_per_kwh",
            },
        )

    def test_evidence_summary_retains_source_status_and_record_count(self):
        self.session.add_fact("appliance.rated_power_w", 100, source="manufacturer_label")
        evidence = self.session.evidence_summary()["appliance.rated_power_w"]
        self.assertEqual(evidence["status"], "confirmed")
        self.assertEqual(evidence["record_count"], 1)
        self.assertEqual(evidence["value"], 100)


if __name__ == "__main__":
    unittest.main()
