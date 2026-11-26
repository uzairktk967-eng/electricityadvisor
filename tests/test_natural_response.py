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


    def test_general_kwh_definition_without_assessment(self):
        answer = generate_natural_language_answer("What does one kWh mean?", None)
        self.assertIn("one electricity unit", answer)

    def test_calculation_method_without_assessment(self):
        answer = generate_natural_language_answer("How do you calculate monthly electricity consumption?", None)
        self.assertIn("rated power", answer)
        self.assertIn("÷ 1,000", answer)

    def test_required_inputs_without_assessment(self):
        answer = generate_natural_language_answer("What information do you need to calculate my usage?", None)
        self.assertIn("quantity", answer)
        self.assertIn("tariff", answer)

    def test_standby_requires_separate_standby_power(self):
        answer = generate_natural_language_answer("How is standby electricity calculated?", None)
        self.assertIn("standby mode", answer)
        self.assertIn("must not be assumed", answer)

    def test_full_bill_scope_is_explained(self):
        answer = generate_natural_language_answer("Does this calculate my full electricity bill?", None)
        self.assertIn("complete utility bill", answer)

    def test_efficiency_question_is_grounded_in_labels(self):
        answer = generate_natural_language_answer("How can I compare appliance efficiency?", None)
        self.assertIn("verified energy labels", answer)

    def test_confirmed_inputs_are_reported(self):
        result = {
            "evidence": {
                "appliance.rated_power_w": {"status": "confirmed", "value": 100},
                "appliance.quantity": {"status": "confirmed", "value": 2},
                "usage.hours_per_day": {"status": "confirmed", "value": 5},
                "usage.days_per_month": {"status": "confirmed", "value": 30},
                "tariff.price_per_kwh": {"status": "confirmed", "value": 55},
            },
            "conclusions": {},
            "recommendations": [],
            "conflicts": [],
            "safety_notice": None,
        }
        answer = generate_natural_language_answer("Show my confirmed inputs", result)
        self.assertIn("100 W", answer)
        self.assertIn("2", answer)
        self.assertIn("55 Rs./kWh", answer)

    def test_unknown_topic_is_explicitly_outside_knowledge_base(self):
        answer = generate_natural_language_answer("Who will win the next cricket world cup?", None)
        self.assertIn("not covered by this knowledge base", answer)

    def test_unknown_question_after_assessment_does_not_guess(self):
        result = {
            "conclusions": {},
            "evidence": {},
            "recommendations": [],
            "conflicts": [],
            "safety_notice": None,
        }
        answer = generate_natural_language_answer("What is the best mobile phone?", result)
        self.assertIn("current knowledge base", answer)
        self.assertIn("I won't guess", answer)


    def test_watts_and_kwh_are_distinguished(self):
        answer = generate_natural_language_answer("What is the difference between watts and kWh?", None)
        self.assertIn("Watt (W) measures power", answer)
        self.assertIn("Kilowatt-hour", answer)

    def test_unknown_question_with_empty_assessment_is_not_misreported_as_missing_inputs(self):
        result = {"conclusions": {}, "evidence": {}, "recommendations": [], "conflicts": [], "safety_notice": None}
        answer = generate_natural_language_answer("Who is the current president of France?", result)
        self.assertIn("current knowledge base", answer)
        self.assertIn("I won't guess", answer)


if __name__ == "__main__":
    unittest.main()
