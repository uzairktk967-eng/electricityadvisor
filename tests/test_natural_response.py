"""Tests for evidence-grounded natural-language answers."""

import unittest

from consultation.natural_response import generate_natural_language_answer


class NaturalResponseTests(unittest.TestCase):
    def test_prompts_for_inputs_when_no_assessment_exists(self):
        answer = generate_natural_language_answer("Why is my bill high?", None)
        self.assertIn("rated power", answer)
        self.assertIn("run an assessment", answer)

    def test_single_appliance_energy_question_gets_conversational_answer(self):
        result = {
            "conclusions": {
                "energy.monthly_kwh_estimate_available": {"value": 72, "unit": "kWh/month"}
            },
            "recommendations": [],
            "conflicts": [],
            "safety_notice": None,
        }
        answer = generate_natural_language_answer("How much electricity does it use?", result)
        self.assertIn("72 kWh per month", answer)
        self.assertIn("quantity", answer)

    def test_single_appliance_cost_requires_entered_tariff(self):
        result = {
            "conclusions": {
                "energy.monthly_kwh_estimate_available": {"value": 72, "unit": "kWh/month"}
            },
            "recommendations": [],
            "conflicts": [],
            "safety_notice": None,
        }
        answer = generate_natural_language_answer("How much will it cost?", result)
        self.assertIn("price per kWh", answer)

    def test_multi_appliance_highest_consumer_answer(self):
        result = {
            "appliances": [
                {"name": "Fans", "monthly_kwh": 72},
                {"name": "LED bulbs", "monthly_kwh": 18},
                {"name": "Heater", "monthly_kwh": 90},
            ],
            "total_monthly_kwh": 180,
            "total_monthly_variable_cost": 9900,
            "highest_consumption_appliance": "Heater",
        }
        answer = generate_natural_language_answer("Which appliance uses the most electricity?", result)
        self.assertIn("Heater", answer)
        self.assertIn("90 kWh", answer)

    def test_multi_appliance_cost_answer_has_bill_caveat(self):
        result = {
            "appliances": [],
            "total_monthly_kwh": 180,
            "total_monthly_variable_cost": 9900,
            "highest_consumption_appliance": "Heater",
        }
        answer = generate_natural_language_answer("What will it cost?", result)
        self.assertIn("Rs. 9,900", answer)
        self.assertIn("not your complete electricity bill", answer)

    def test_safety_question_gets_professional_referral(self):
        answer = generate_natural_language_answer("There are sparks from my socket.", None)
        self.assertIn("qualified electrician", answer)
        self.assertIn("Do not", answer)

if __name__ == "__main__":
    unittest.main()
