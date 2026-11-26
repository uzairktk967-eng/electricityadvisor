"""Unit tests for the core symbolic inference engine."""

import unittest
from pathlib import Path

from expert_system import InferenceEngine


ROOT = Path(__file__).resolve().parents[1]
KB_DIR = ROOT / "knowledge_base"


class InferenceEngineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.engine = InferenceEngine(KB_DIR)

    def test_forward_chain_energy_and_cost(self):
        facts = self.engine.new_fact_store()
        facts.add("appliance.rated_power_w", 1000)
        facts.add("appliance.quantity", 2)
        facts.add("usage.hours_per_day", 3)
        facts.add("usage.days_per_month", 30)
        facts.add("tariff.price_per_kwh", 50)
        result = self.engine.forward_chain(facts)
        self.assertAlmostEqual(result.conclusions["energy.monthly_kwh_estimate_available"].value, 180.0)
        self.assertAlmostEqual(result.conclusions["cost.monthly_variable_estimate_available"].value, 9000.0)
        self.assertIn("R-ENERGY-001", result.fired_rules)
        self.assertIn("R-COST-001", result.fired_rules)

    def test_unknown_and_uncertain_facts_do_not_fire(self):
        facts = self.engine.new_fact_store()
        facts.add("supply.has_electrical_symptom", True, status="uncertain")
        result = self.engine.forward_chain(facts)
        self.assertNotIn("safety.professional_inspection_required", result.conclusions)

    def test_rejected_fact_does_not_fire(self):
        facts = self.engine.new_fact_store()
        facts.add("supply.has_electrical_symptom", True, status="rejected")
        result = self.engine.forward_chain(facts)
        self.assertNotIn("safety.professional_inspection_required", result.conclusions)

    def test_safety_rule_fires_for_confirmed_symptom(self):
        facts = self.engine.new_fact_store()
        facts.add("supply.has_electrical_symptom", True, source="user_report")
        result = self.engine.forward_chain(facts)
        self.assertTrue(result.conclusions["safety.professional_inspection_required"].value)
        self.assertIn("R-SAFETY-001", result.fired_rules)

    def test_standby_requires_standby_specific_power(self):
        facts = self.engine.new_fact_store()
        facts.add("appliance.measured_power_w", 20)
        facts.add("appliance.quantity", 1)
        facts.add("usage.standby_hours_per_day", 10)
        facts.add("usage.days_per_month", 30)
        result = self.engine.forward_chain(facts)
        self.assertNotIn("standby.energy_estimate_available", result.conclusions)

        facts.add("appliance.standby_power_w", 2, source="standby_meter_reading")
        result = self.engine.forward_chain(facts)
        self.assertAlmostEqual(result.conclusions["standby.energy_estimate_available"].value, 0.6)

    def test_fact_conflict_is_reported_and_not_used(self):
        facts = self.engine.new_fact_store()
        facts.add("supply.has_electrical_symptom", True)
        facts.add("supply.has_electrical_symptom", False)
        result = self.engine.forward_chain(facts)
        self.assertNotIn("safety.professional_inspection_required", result.conclusions)
        self.assertTrue(any(item["type"] == "contradictory_fact_evidence" for item in result.conflicts))

    def test_backward_chain_identifies_missing_inputs(self):
        facts = self.engine.new_fact_store()
        result = self.engine.backward_chain("energy.monthly_kwh_estimate_available", facts)
        alternative = result.alternatives[0]
        self.assertEqual(alternative["status"], "needs_information")
        self.assertEqual(set(alternative["missing_facts"]), {
            "appliance.rated_power_w", "appliance.quantity",
            "usage.hours_per_day", "usage.days_per_month"
        })

    def test_backward_chain_reports_ready_rule(self):
        facts = self.engine.new_fact_store()
        facts.add("supply.has_electrical_symptom", True)
        result = self.engine.backward_chain("safety.professional_inspection_required", facts)
        self.assertEqual(result.alternatives[0]["status"], "ready")

    def test_fact_type_validation(self):
        facts = self.engine.new_fact_store()
        with self.assertRaises(ValueError):
            facts.add("supply.has_electrical_symptom", "yes")


if __name__ == "__main__":
    unittest.main()
