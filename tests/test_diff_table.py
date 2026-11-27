"""gart.diff/0: the table of differences between the validator copies and gart (gart-H3)."""

import importlib
import json
import unittest
from pathlib import Path

from gart.schema import check_schema, validate

ROOT = Path(__file__).resolve().parent.parent
SCHEMA = json.loads((ROOT / "gart/schemas/diff.schema.json").read_text(encoding="utf-8"))
TABLE = json.loads((ROOT / "docs/records/gart-diff.json").read_text(encoding="utf-8"))


class DiffTableTests(unittest.TestCase):
    def test_schema_is_valid_for_gart(self):
        check_schema(SCHEMA)

    def test_table_matches_its_schema(self):
        self.assertEqual(validate(TABLE, SCHEMA), [])

    def test_ids_are_unique_and_in_order(self):
        ids = [row["id"] for row in TABLE["rows"]]
        self.assertEqual(ids, sorted(set(ids)))

    def test_copies_named_in_rows_are_measured(self):
        measured = {c["name"] for c in TABLE["copies"]}
        for row in TABLE["rows"]:
            with self.subTest(row=row["id"]):
                self.assertLessEqual(set(row["copies"]), measured)
                self.assertLessEqual({t.split(":")[0] for t in row.get("copyTests", [])}, measured)

    def test_each_copy_test_has_one_row(self):
        seen: dict = {}
        for row in TABLE["rows"]:
            for test in row.get("copyTests", []):
                with self.subTest(test=test):
                    self.assertNotIn(test, seen, f"also in {seen.get(test)}")
                    seen[test] = row["id"]

    def test_gart_tests_exist(self):
        for row in TABLE["rows"]:
            for name in row.get("tests", []):
                with self.subTest(row=row["id"], test=name):
                    module, cls, method = name.rsplit(".", 2)
                    self.assertTrue(callable(getattr(getattr(importlib.import_module(module), cls), method, None)))

    def test_rejects_a_deferred_row_without_milestone(self):
        row = {"id": "D99", "topic": "x", "copies": {"oi": "x"}, "gart": "x", "resolution": "deferred"}
        errors = validate({**TABLE, "rows": [row]}, SCHEMA)
        self.assertEqual([(e.path, e.code, e.params.get("name")) for e in errors], [("/rows/0", "required", "milestone")])


if __name__ == "__main__":
    unittest.main()
