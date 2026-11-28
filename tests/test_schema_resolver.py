"""`check_schema` and `validate` with a resolver: `$ref` to a kind id or a sibling document (gart-H4, Q-23)."""

import unittest

from gart.schema import SchemaError, check_schema, validate

COMMON = {"$defs": {"Hash": {"type": "string", "pattern": "^sha256:"}}}


def make_resolver(kinds=None, siblings=None):
    kinds = kinds or {}
    siblings = siblings or {}
    calls = []

    def resolver(base, target):
        calls.append((base, target))
        if target in kinds:
            return kinds[target], "kinds"
        if (base, target) in siblings:
            return siblings[(base, target)], base
        raise SchemaError(f"unresolved reference {target!r}")

    resolver.calls = calls
    return resolver


class ResolverTest(unittest.TestCase):
    def test_kind_ref_with_pointer_and_bare(self):
        res = make_resolver({"gart.common/0": COMMON, "gart.any/0": {"type": "string"}})
        schema = {"properties": {"h": {"$ref": "gart.common/0#/$defs/Hash"}, "a": {"$ref": "gart.any/0"}}}
        check_schema(schema, res)
        self.assertEqual(validate({"h": "sha256:x", "a": "s"}, schema, res), [])
        errors = validate({"h": "nope", "a": 1}, schema, res)
        self.assertEqual([(e.path, e.code) for e in errors], [("/a", "type"), ("/h", "pattern")])

    def test_sibling_ref_uses_base(self):
        res = make_resolver(siblings={("dir", "c.schema.json"): COMMON})
        schema = {"$ref": "c.schema.json#/$defs/Hash"}
        self.assertEqual(validate("sha256:1", schema, res, "dir"), [])
        with self.assertRaisesRegex(SchemaError, "unresolved reference 'c.schema.json'"):
            validate("sha256:1", schema, res, "other")

    def test_without_resolver_still_rejected(self):
        for ref in ("gart.common/0#/$defs/Hash", "c.schema.json"):
            with self.assertRaisesRegex(SchemaError, "is not local"):
                check_schema({"$ref": ref})

    def test_unsafe_refs_name_the_reason(self):
        res = make_resolver()
        cases = {
            "https://x.org/a.json": "remote or unsafe",
            "../c.schema.json": "remote or unsafe",
            "dir\\c.schema.json": "remote or unsafe",
            "dir/c.schema.json": "neither a kind id nor a sibling",
            "gart.common/01": "neither a kind id nor a sibling",
        }
        for ref, reason in cases.items():
            with self.subTest(ref=ref), self.assertRaisesRegex(SchemaError, reason):
                check_schema({"$ref": ref}, res)
        self.assertEqual(res.calls, [])

    def test_bare_hash_and_empty_still_rejected_with_resolver(self):
        res = make_resolver()
        with self.assertRaisesRegex(SchemaError, "reference '#' is not supported"):
            check_schema({"$ref": "#"}, res)
        with self.assertRaisesRegex(SchemaError, "is not local"):
            check_schema({"$ref": ""}, res)

    def test_unknown_kind(self):
        with self.assertRaisesRegex(SchemaError, "unresolved reference 'gart.nope/0'"):
            check_schema({"$ref": "gart.nope/0"}, make_resolver())

    def test_cycle_across_two_documents(self):
        a = {"$defs": {"x": {"$ref": "b.schema.json#/$defs/y"}}}
        b = {"$defs": {"y": {"$ref": "a.schema.json#/$defs/x"}}}
        res = make_resolver(siblings={("d", "a.schema.json"): a, ("d", "b.schema.json"): b})
        with self.assertRaisesRegex(SchemaError, "cyclic reference"):
            check_schema(a, res, "d")
        with self.assertRaisesRegex(SchemaError, "cyclic reference"):
            validate(1, {"$ref": "a.schema.json#/$defs/x"}, res, "d")

    def test_same_local_pointer_in_two_documents_is_not_a_cycle(self):
        # `#/$defs/x` appears in both documents; the first one hands over to the second one.
        a = {"$defs": {"x": {"$ref": "b.schema.json#/$defs/x"}}, "$ref": "#/$defs/x"}
        b = {"$defs": {"x": {"type": "integer"}}}
        res = make_resolver(siblings={("d", "b.schema.json"): b})
        check_schema(a, res, "d")
        self.assertEqual(validate(1, a, res, "d"), [])
        self.assertEqual([e.code for e in validate("s", a, res, "d")], ["type"])

    def test_local_pointer_after_crossing_is_relative_to_the_target(self):
        b = {"$defs": {"x": {"$ref": "#/$defs/y"}, "y": {"const": 1}}}
        res = make_resolver(siblings={("d", "b.schema.json"): b})
        schema = {"$ref": "b.schema.json#/$defs/x"}
        self.assertEqual(validate(1, schema, res, "d"), [])
        self.assertEqual([e.code for e in validate(2, schema, res, "d")], ["const"])


if __name__ == "__main__":
    unittest.main()
