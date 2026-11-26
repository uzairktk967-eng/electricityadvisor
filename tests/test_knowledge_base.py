"""Tests for knowledge-base structure and cross-file validation."""

import json
import unittest
from pathlib import Path

from knowledge_base import load_documents, validate_documents

ROOT = Path(__file__).resolve().parents[1]
KB = ROOT / "knowledge_base"


class KnowledgeBaseValidationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.documents = load_documents(KB)
        cls.schema = json.loads((KB / "schema.json").read_text(encoding="utf-8"))

    def test_current_knowledge_base_is_valid(self):
        report = validate_documents(self.documents, self.schema)
        self.assertTrue(report.is_valid, "\n".join(report.errors))

    def test_duplicate_fact_id_is_rejected(self):
        draft = json.loads(json.dumps(self.documents))
        draft["facts.json"]["facts"].append(draft["facts.json"]["facts"][0])
        report = validate_documents(draft, self.schema)
        self.assertFalse(report.is_valid)
        self.assertTrue(any("duplicate ID" in error for error in report.errors))

    def test_unknown_fact_reference_is_rejected(self):
        draft = json.loads(json.dumps(self.documents))
        draft["rules.json"]["rules"][0]["conditions"][0]["fact"] = "unknown.fact"
        report = validate_documents(draft, self.schema)
        self.assertFalse(report.is_valid)
        self.assertTrue(any("unknown fact" in error for error in report.errors))

    def test_numeric_operator_on_boolean_fact_is_rejected(self):
        draft = json.loads(json.dumps(self.documents))
        condition = draft["rules.json"]["rules"][0]["conditions"][0]
        condition["fact"] = "appliance.has_energy_label"
        condition["operator"] = "gt"
        condition["value"] = 0
        report = validate_documents(draft, self.schema)
        self.assertFalse(report.is_valid)
        self.assertTrue(any("numeric operator" in error for error in report.errors))

    def test_unapproved_formula_is_rejected(self):
        draft = json.loads(json.dumps(self.documents))
        draft["rules.json"]["rules"][0]["formula"] = "__import__('os').system('echo unsafe')"
        report = validate_documents(draft, self.schema)
        self.assertFalse(report.is_valid)
        self.assertTrue(any("not explicitly allow-listed" in error for error in report.errors))

    def test_prerequisite_cycle_is_rejected(self):
        draft = json.loads(json.dumps(self.documents))
        # Add a dependency from the energy conclusion back to the cost conclusion.
        draft["rules.json"]["rules"][0]["requires_conclusion"] = "cost.monthly_variable_estimate_available"
        report = validate_documents(draft, self.schema)
        self.assertFalse(report.is_valid)
        self.assertTrue(any("dependency cycle" in error for error in report.errors))


if __name__ == "__main__":
    unittest.main()
