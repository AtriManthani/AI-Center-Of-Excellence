import copy
import unittest

from tools.repository_model import (
    ROOT,
    load_configuration,
    load_json,
    validate_issue_record,
    validate_license_record,
    validate_use_case_record,
)


EXAMPLE_DIR = ROOT / "shared" / "examples" / "AI-0001-example"


class RepositoryModelTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.vocab, cls.mapping = load_configuration()
        cls.use_case = load_json(EXAMPLE_DIR / "use-case.json")
        cls.license = load_json(EXAMPLE_DIR / "license.json")
        cls.issue = load_json(EXAMPLE_DIR / "issue.json")

    def test_synthetic_use_case_is_valid(self):
        self.assertEqual(validate_use_case_record(self.use_case, self.vocab, self.mapping), [])

    def test_synthetic_license_is_valid(self):
        self.assertEqual(validate_license_record(self.license, self.vocab), [])

    def test_synthetic_issue_is_valid(self):
        self.assertEqual(validate_issue_record(self.issue, self.vocab), [])

    def test_lifecycle_mismatch_is_rejected(self):
        record = copy.deepcopy(self.use_case)
        record["inventory"]["bucket"] = "in_production"
        errors = validate_use_case_record(record, self.vocab, self.mapping)
        self.assertTrue(any("not allowed" in error for error in errors))

    def test_license_arithmetic_is_enforced(self):
        record = copy.deepcopy(self.license)
        record["capacity"]["available"] = 4
        errors = validate_license_record(record, self.vocab)
        self.assertTrue(any("must equal" in error for error in errors))

    def test_closed_issue_requires_resolution(self):
        record = copy.deepcopy(self.issue)
        record["resolution"] = None
        errors = validate_issue_record(record, self.vocab)
        self.assertTrue(any("require resolution" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
