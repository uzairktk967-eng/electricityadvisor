"""Regression tests for independent multi-appliance assessments."""

from pathlib import Path
import unittest

from consultation.multi_appliance import assess_multiple_appliances

ROOT = Path(__file__).resolve().parents[1]
KB = ROOT / "knowledge_base"


class MultiApplianceTests(unittest.TestCase):
    def setUp(self):
        self.appliances = [
            {"name": "Fans", "rated_power_w": 80, "quantity": 3, "hours_per_day": 10, "days_per_month": 30},
            {"name": "LED bulbs", "rated_power_w": 20, "quantity": 5, "hours_per_day": 6, "days_per_month": 30},
            {"name": "Heater", "rated_power_w": 1000, "quantity": 1, "hours_per_day": 3, "days_per_month": 30},
        ]

    def test_expected_household_energy_and_cost(self):
        result = assess_multiple_appliances(KB, self.appliances, tariff_per_kwh=55)
        self.assertAlmostEqual(result["appliances"][0]["monthly_kwh"], 72)
        self.assertAlmostEqual(result["appliances"][1]["monthly_kwh"], 18)
        self.assertAlmostEqual(result["appliances"][2]["monthly_kwh"], 90)
        self.assertAlmostEqual(result["total_monthly_kwh"], 180)
        self.assertAlmostEqual(result["total_monthly_variable_cost"], 9900)
        self.assertEqual(result["highest_consumption_appliance"], "Heater")

    def test_each_appliance_is_calculated_independently(self):
        result = assess_multiple_appliances(KB, self.appliances)
        self.assertEqual(len(result["appliances"]), 3)
        self.assertIsNone(result["total_monthly_variable_cost"])

    def test_safety_symptom_is_carried_to_household_result(self):
        result = assess_multiple_appliances(KB, self.appliances, electrical_symptom=True)
        self.assertIn("qualified electrician", result["safety_notice"])

    def test_rejects_fractional_quantity(self):
        items = [dict(self.appliances[0], quantity=1.5)]
        with self.assertRaises(ValueError):
            assess_multiple_appliances(KB, items)

    def test_rejects_runtime_over_24_hours(self):
        items = [dict(self.appliances[0], hours_per_day=25)]
        with self.assertRaises(ValueError):
            assess_multiple_appliances(KB, items)

    def test_requires_at_least_one_appliance(self):
        with self.assertRaises(ValueError):
            assess_multiple_appliances(KB, [])

if __name__ == "__main__":
    unittest.main()
