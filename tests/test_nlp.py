"""Tests for constrained natural-language fact extraction."""

import unittest

from nlp import extract_facts, normalize_text, tokenize


class NormalizationTests(unittest.TestCase):
    def test_normalize_case_spacing_and_decimal_comma(self):
        self.assertEqual(normalize_text("  RATED POWER: 1,500 W  "), "rated power 1.500 w")

    def test_tokenize_decimal_as_one_token(self):
        self.assertEqual(tokenize("uses 2.5 hours/day"), ["uses", "2.5", "hours", "day"])


class ExtractionTests(unittest.TestCase):
    def test_extract_explicit_numeric_facts(self):
        facts = extract_facts("Rated power is 1200 W and used for 5 hours per day.")
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


if __name__ == "__main__":
    unittest.main()
