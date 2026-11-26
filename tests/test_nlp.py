"""Tests for constrained natural-language fact extraction."""

import unittest

from nlp import extract_facts, normalize_text, tokenize


class NormalizationTests(unittest.TestCase):
    def test_normalize_case_and_spacing_preserves_grouped_number(self):
        self.assertEqual(normalize_text("  RATED POWER: 1,500 W  "), "rated power 1,500 w")

    def test_tokenize_grouped_number_and_decimal(self):
        self.assertEqual(tokenize("uses 1,500 W for 2.5 hours/day"), ["uses", "1,500", "w", "for", "2.5", "hours", "day"])


class ExtractionTests(unittest.TestCase):
    def test_extract_explicit_numeric_facts(self):
        facts = extract_facts("Rated power is 1,200 W and used for 5 hours per day.")
        pairs = {(item.fact_id, item.value) for item in facts}
        self.assertIn(("appliance.rated_power_w", 1200), pairs)
        self.assertIn(("usage.hours_per_day", 5), pairs)

    def test_extract_standby_specific_power(self):
        facts = extract_facts("Standby power is 2 W.")
        self.assertIn(("appliance.standby_power_w", 2), {(item.fact_id, item.value) for item in facts})

    def test_extract_safety_symptom(self):
        facts = extract_facts("There are sparks near the outlet.")
        candidate = next(item for item in facts if item.fact_id == "supply.has_electrical_symptom")
        self.assertTrue(candidate.value)
        self.assertEqual(candidate.status, "confirmed")

    def test_negated_safety_phrase_is_rejected(self):
        facts = extract_facts("There are no sparks near the outlet.")
        candidate = next(item for item in facts if item.fact_id == "supply.has_electrical_symptom")
        self.assertEqual(candidate.status, "rejected")

    def test_uncertain_numeric_value_is_not_confirmed(self):
        facts = extract_facts("Maybe rated power is 1000 W.")
        candidate = next(item for item in facts if item.fact_id == "appliance.rated_power_w")
        self.assertEqual(candidate.status, "uncertain")

    def test_unrecognized_text_does_not_invent_facts(self):
        self.assertEqual(extract_facts("My electricity bill is too high."), [])

    def test_phrase_map_flexible_schedule(self):
        facts = extract_facts("My schedule is flexible.")
        candidate = next(item for item in facts if item.fact_id == "usage.schedule_flexible")
        self.assertTrue(candidate.value)

    def test_common_paraphrases_for_single_appliance(self):
        facts = extract_facts(
            "My fan is rated at 80 W. It runs 10 hours daily. "
            "I have one fan and use it for 30 days per month. "
            "My electricity tariff is Rs. 55 per kWh."
        )
        pairs = {(item.fact_id, item.value) for item in facts}
        self.assertIn(("appliance.rated_power_w", 80), pairs)
        self.assertIn(("usage.hours_per_day", 10), pairs)
        self.assertIn(("appliance.quantity", 1), pairs)
        self.assertIn(("usage.days_per_month", 30), pairs)
        self.assertIn(("tariff.price_per_kwh", 55), pairs)

    def test_word_quantity_is_normalized(self):
        facts = extract_facts("I have two fans.")
        self.assertIn(
            ("appliance.quantity", 2),
            {(item.fact_id, item.value) for item in facts},
        )

    def test_daily_and_monthly_paraphrases(self):
        facts = extract_facts(
            "The appliance operates for 4.5 hours a day and is used for 28 days in the month."
        )
        pairs = {(item.fact_id, item.value) for item in facts}
        self.assertIn(("usage.hours_per_day", 4.5), pairs)
        self.assertIn(("usage.days_per_month", 28), pairs)


    def test_extract_question_one_two_fans(self):
        facts = extract_facts(
            "I have two electric fans, each rated at 75 W. "
            "They run for 12 hours daily for 30 days. "
            "My electricity tariff is Rs. 55 per kWh."
        )
        pairs = {(item.fact_id, item.value) for item in facts}
        self.assertIn(("appliance.quantity", 2), pairs)
        self.assertIn(("appliance.rated_power_w", 75), pairs)
        self.assertIn(("usage.hours_per_day", 12), pairs)
        self.assertIn(("usage.days_per_month", 30), pairs)
        self.assertIn(("tariff.price_per_kwh", 55), pairs)

    def test_extract_question_two_refrigerator_approximate_runtime(self):
        facts = extract_facts(
            "My refrigerator has a rated power of 200 W and operates "
            "for approximately 8 hours per day. Calculate usage for 30 days "
            "at Rs. 55 per kWh."
        )
        pairs = {(item.fact_id, item.value) for item in facts}
        self.assertIn(("appliance.quantity", 1), pairs)
        self.assertIn(("appliance.rated_power_w", 200), pairs)
        self.assertIn(("usage.hours_per_day", 8), pairs)
        self.assertIn(("usage.days_per_month", 30), pairs)
        self.assertIn(("tariff.price_per_kwh", 55), pairs)

    def test_domain_phrases_match_next_to_punctuation(self):
        facts = extract_facts("There are sparks, and my schedule is flexible.")
        pairs = {(item.fact_id, item.value) for item in facts}
        self.assertIn(("supply.has_electrical_symptom", True), pairs)
        self.assertIn(("usage.schedule_flexible", True), pairs)


if __name__ == "__main__":
    unittest.main()
