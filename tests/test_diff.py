"""`gart/diff.json` (`gart.diff/0`): it is a valid artifact, its rows are well formed, and each rule row has its case.

DDD invariant 8: where the copies differ the strictest wins, and the table says so; each `regla` or `alcance` row
has a probe here that shows what gart does today.
"""

import unittest
from pathlib import Path

from gart import SchemaError, check_schema, loads_strict, validate

ROOT = Path(__file__).resolve().parent.parent / "gart"
INF, NAN = float("inf"), float("nan")
SCHEMA_ERROR = "schema-error"
VALID = "valid"

_CYCLE = {"$defs": {"a": {"$ref": "#/$defs/b"}, "b": {"$ref": "#/$defs/a"}}, "$ref": "#/$defs/a"}

# row id -> (schema, instance, what gart does: "schema-error" | "valid" | "invalid:<code>")
PROBES = {
    "D01": ({"type": "number"}, INF, "invalid:type"),
    "D02": ({"type": "object"}, object(), "invalid:type"),
    "D03": ({"pattern": "^\\d$"}, "١", "invalid:pattern"),
    "D04": ({"minimum": NAN}, 5, SCHEMA_ERROR),
    "D05": ({"minimum": "1"}, 5, SCHEMA_ERROR),
    "D06": ({"minLength": -1}, "a", SCHEMA_ERROR),
    "D07": ({"enum": []}, 1, SCHEMA_ERROR),
    "D08": ({"required": "a"}, {}, SCHEMA_ERROR),
    "D09": ({"properties": []}, {}, SCHEMA_ERROR),
    "D10": ({"type": []}, 1, SCHEMA_ERROR),
    "D11": ({"pattern": "("}, "a", SCHEMA_ERROR),
    "D12": (_CYCLE, 1, SCHEMA_ERROR),
    "D13": ({"$ref": "#"}, 1, SCHEMA_ERROR),
    "D14": ({"const": 1}, 2, "invalid:const"),
    "D15": ({"propertyNames": {"pattern": "^a"}}, {"b": 1}, "invalid:propertyNames"),
    "D16": ({"minProperties": 1}, {}, "invalid:minProperties"),
    "D17": ({"$defs": {"n": {"type": "integer"}}, "$ref": "#/$defs/n"}, "x", "invalid:type"),
    "D18": (False, 1, "invalid:false"),
    "D19": ({"default": 1, "examples": [1], "type": "integer"}, 1, VALID),
    "D20": ({"maxProperties": 1}, {"a": 1, "b": 2}, "invalid:maxProperties"),
    "D21": ({"dependentRequired": {"a": ["b"]}}, {"a": 1}, "invalid:dependentRequired"),
    "D22": ({"allOf": [{"minimum": 5}]}, 1, "invalid:minimum"),
    "D23": ({"if": {"type": "integer"}, "then": {"minimum": 5}}, 1, "invalid:minimum"),
}


def _load(relative):
    return loads_strict((ROOT / relative).read_text(encoding="utf-8"))


class DiffArtifactTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.diff = _load("diff.json")
        cls.schema = _load("schemas/gart.diff/0.json")

    def test_schema_is_in_the_supported_subset(self):
        check_schema(self.schema)
        self.assertIn("$schema", self.schema)
        self.assertIn("title", self.schema)

    def test_artifact_conforms_to_its_schema(self):
        self.assertEqual(self.diff["schema"], "gart.diff/0")
        self.assertEqual(validate(self.diff, self.schema), [])

    def test_schema_rejects_a_malformed_artifact(self):
        bad = {**self.diff, "rows": [{**self.diff["rows"][0], "kind": "otra"}], "extra": 1}
        self.assertEqual({(e.path, e.code) for e in validate(bad, self.schema)},
                         {("/extra", "additionalProperties"), ("/rows/0/kind", "enum")})

    def test_row_ids_are_unique_and_sorted(self):
        ids = [row["id"] for row in self.diff["rows"]]
        self.assertEqual(ids, sorted(set(ids)))

    def test_outcomes_name_every_copy_and_gart(self):
        expected = {c["id"] for c in self.diff["copies"]} | {"gart"}
        for row in self.diff["rows"]:
            with self.subTest(row=row["id"]):
                self.assertEqual(set(row["outcomes"]), expected)
                if "consumer" in row:
                    self.assertIn(row["consumer"], expected - {"gart"})

    def test_every_rule_and_scope_row_has_its_probe(self):
        with_probe = {row["id"] for row in self.diff["rows"] if row["kind"] in ("regla", "alcance")}
        self.assertEqual(set(PROBES), with_probe)

    def test_pending_rows_name_their_milestone(self):
        for row in self.diff["rows"]:
            if row["kind"] == "pendiente":
                with self.subTest(row=row["id"]):
                    self.assertIn("milestone", row)

    def test_probes_show_what_gart_does(self):
        for row_id, (schema, instance, expected) in PROBES.items():
            with self.subTest(row=row_id):
                if expected == SCHEMA_ERROR:
                    with self.assertRaises(SchemaError):
                        validate(instance, schema)
                else:
                    got = validate(instance, schema)
                    if expected == VALID:
                        self.assertEqual(got, [])
                    else:
                        self.assertEqual([f"invalid:{e.code}" for e in got], [expected])


if __name__ == "__main__":
    unittest.main()
