"""Tests for the consultation orchestration layer."""

from pathlib import Path
import unittest

from consultation import ConsultationSession

ROOT = Path(__file__).resolve().parents[1]
KB = ROOT / "knowledge_base"


class ConsultationTests(unittest.TestCase):
    def setUp(self):
        self.session = ConsultationSession(KB)

    def test_text_candidates_are_not_automatically_added(self):
        candidates = self.session.submit_text("Rated power is 100 W.")
        self.assertEqual(len(candidates), 1)
        self.assertEqual(self.session.store.evidence("appliance.rated_power_w")["status"], "missing")

    def test_candidate_requires_explicit_confirmation(self):
        candidates = self.session.submit_text("Rated power is 100 W.")
        reviewed = self.session.review_candidate(candidates[0]["index"], confirm=True)
        self.assertEqual(reviewed["status"], "confirmed")
        self.assertEqual(self.session.store.evidence("appliance.rated_power_w")["value"], 100)

    def test_candidate_can_be_rejected_by_user(self):
        candidates = self.session.submit_text("Rated power is 100 W.")
        reviewed = self.session.review_candidate(candidates[0]["index"], confirm=False)
        self.assertEqual(reviewed["status"], "rejected")

    def test_duplicate_review_is_blocked(self):
        candidates = self.session.submit_text("Rated power is 100 W.")
        index = candidates[0]["index"]
        self.session.review_candidate(index, confirm=True)
        with self.assertRaises(ValueError):
            self.session.review_candidate(index, confirm=True)

    def test_missing_questions_for_energy_estimate(self):
        questions = self.session.missing_questions("energy.monthly_kwh_estimate_available")
        ids = {item["fact_id"] for item in questions}
        self.assertTrue({
            "appliance.rated_power_w", "appliance.quantity",
            "usage.hours_per_day", "usage.days_per_month",
        }.issubset(ids))

    def test_energy_and_cost_response_uses_supported_rules(self):
        self.session.add_fact("appliance.rated_power_w", 100)
        self.session.add_fact("appliance.quantity", 2)
        self.session.add_fact("usage.hours_per_day", 5)
        self.session.add_fact("usage.days_per_month", 30)
        self.session.add_fact("tariff.price_per_kwh", 50)
        response = self.session.run()
        self.assertAlmostEqual(response["conclusions"]["energy.monthly_kwh_estimate_available"]["value"], 30)
        self.assertAlmostEqual(response["conclusions"]["cost.monthly_variable_estimate_available"]["value"], 1500)
        self.assertIn("R-ENERGY-001", response["fired_rules"])
        self.assertIn("R-COST-001", response["fired_rules"])
        self.assertEqual(len(response["recommendations"]), 2)

    def test_safety_symptom_returns_professional_referral(self):
        self.session.add_fact("supply.has_electrical_symptom", True)
        response = self.session.run()
        self.assertIsNotNone(response["safety_notice"])
        self.assertIn("R-SAFETY-001", response["fired_rules"])

    def test_conflicting_inputs_are_reported(self):
        self.session.add_fact("appliance.rated_power_w", 100)
        self.session.add_fact("appliance.rated_power_w", 200)
        self.session.add_fact("appliance.quantity", 1)
        self.session.add_fact("usage.hours_per_day", 2)
        self.session.add_fact("usage.days_per_month", 30)
        response = self.session.run()
        self.assertTrue(response["conflicts"])
        self.assertNotIn("energy.monthly_kwh_estimate_available", response["conclusions"])


if __name__ == "__main__":
    unittest.main()
