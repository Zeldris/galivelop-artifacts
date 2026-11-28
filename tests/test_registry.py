"""`Registry` (gart-H4): schema folders, `$ref` between schemas, fingerprints and namespaces (DDD invariants 2, 12)."""

import json
import os
import tempfile
import unittest
from pathlib import Path

from gart import Registry, SchemaError, fingerprint, loads_strict
from gart.canon import canonical_bytes

GART = Path(__file__).resolve().parent.parent / "gart"
HASH = "sha256:" + "a" * 64


def schema(kind, **extra):
    return {"title": kind, "type": "object", **extra}


class Folder:
    """A temp schema folder; `put(rel, obj_or_text)` writes a file."""

    def __init__(self, test):
        self._dir = tempfile.TemporaryDirectory()
        test.addCleanup(self._dir.cleanup)
        self.path = self._dir.name

    def put(self, rel, content):
        target = os.path.join(self.path, *rel.split("/"))
        os.makedirs(os.path.dirname(target), exist_ok=True)
        text = content if isinstance(content, str) else json.dumps(content)
        with open(target, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(text)
        return target

    def read(self, rel):
        with open(os.path.join(self.path, rel), encoding="utf-8") as handle:
            return handle.read()


class Base(unittest.TestCase):
    def folder(self):
        return Folder(self)

    def assertLoadFails(self, reason, path, **kwargs):
        with self.assertRaises(SchemaError) as ctx:
            Registry().load(path, **kwargs)
        self.assertRegex(str(ctx.exception), reason)


class NamingTest(Base):
    def test_kind_file_loads(self):
        f = self.folder()
        f.put("oi.thing/0.json", schema("oi.thing/0"))
        reg = Registry().load(f.path, owner="oi")
        self.assertIn("oi.thing/0", reg.kinds())
        self.assertEqual(reg.get("oi.thing/0")["title"], "oi.thing/0")

    def test_load_returns_self_and_kinds_sorted(self):
        f = self.folder()
        f.put("oi.b/0.json", schema("oi.b/0"))
        f.put("oi.a/0.json", schema("oi.a/0"))
        reg = Registry()
        self.assertIs(reg.load(f.path, foreign=True), reg)
        self.assertEqual(reg.kinds(), sorted(reg.kinds()))

    def test_title_must_equal_kind(self):
        f = self.folder()
        f.put("oi.thing/0.json", schema("oi.other/0"))
        self.assertLoadFails(r"oi\.thing/0\.json: title 'oi\.other/0' must be the kind id 'oi\.thing/0'", f.path, foreign=True)

    def test_missing_title(self):
        f = self.folder()
        f.put("oi.thing/0.json", {"type": "object"})
        self.assertLoadFails(r"title None must be the kind id", f.path, foreign=True)

    def test_stray_json_names_the_file(self):
        for rel in ("stray.json", "oi.thing/readme.json", "oi.thing/00.json", "oi.thing/x/0.json", "Bad.schema.json", "oi.thing/0.schema.json"):
            with self.subTest(rel=rel):
                f = self.folder()
                f.put(rel, {})
                self.assertLoadFails("unexpected json file", f.path, foreign=True)
                with self.assertRaises(SchemaError) as ctx:
                    Registry().load(f.path, foreign=True)
                self.assertIn(rel, str(ctx.exception))

    def test_non_json_ignored(self):
        f = self.folder()
        f.put("notes.txt", "hi")
        f.put("oi.thing/README.md", "hi")
        Registry().load(f.path, foreign=True)

    def test_duplicate_keys_rejected(self):
        f = self.folder()
        f.put("oi.thing/0.json", '{"title": "oi.thing/0", "type": "object", "type": "string"}')
        self.assertLoadFails(r"oi\.thing/0\.json: cannot read as strict JSON.*duplicate", f.path, foreign=True)

    def test_schema_checked_on_load(self):
        f = self.folder()
        f.put("oi.thing/0.json", schema("oi.thing/0", bogus=1))
        self.assertLoadFails(r"oi\.thing/0: .*unsupported keyword 'bogus'", f.path, foreign=True)

    def test_failed_load_leaves_registry_unchanged(self):
        f = self.folder()
        f.put("oi.a/0.json", schema("oi.a/0"))
        f.put("oi.b/0.json", schema("oi.b/0", bogus=1))
        reg = Registry()
        before = reg.kinds()
        with self.assertRaises(SchemaError):
            reg.load(f.path, foreign=True)
        self.assertEqual(reg.kinds(), before)

    def test_not_a_folder(self):
        self.assertLoadFails("not a folder", "/nonexistent-gart-folder", foreign=True)

    def test_same_kind_twice(self):
        f, g = self.folder(), self.folder()
        f.put("oi.thing/0.json", schema("oi.thing/0"))
        g.put("oi.thing/0.json", schema("oi.thing/0"))
        reg = Registry().load(f.path, foreign=True).load(g.path, foreign=True)  # same fingerprint: no-op
        self.assertEqual(reg.kinds().count("oi.thing/0"), 1)
        g.put("oi.thing/0.json", schema("oi.thing/0", description="changed"))
        with self.assertRaisesRegex(SchemaError, r"oi\.thing/0: already loaded with a different schema"):
            reg.load(g.path, foreign=True)


class RefTest(Base):
    def test_kind_ref_across_folders(self):
        f, g = self.folder(), self.folder()
        f.put("oi.a/0.json", {"title": "oi.a/0", "$defs": {"N": {"type": "integer"}}})
        g.put("oi.b/0.json", schema("oi.b/0", properties={"n": {"$ref": "oi.a/0#/$defs/N"}}))
        reg = Registry().load(f.path, foreign=True).load(g.path, foreign=True)
        self.assertEqual(reg.validate({"n": 1}, "oi.b/0"), [])
        self.assertEqual([(e.path, e.code) for e in reg.validate({"n": "x"}, "oi.b/0")], [("/n", "type")])

    def test_kind_ref_to_gart_common(self):
        f = self.folder()
        f.put("oi.b/0.json", schema("oi.b/0", properties={"h": {"$ref": "gart.common/0#/$defs/ContentHash"}}))
        reg = Registry().load(f.path, foreign=True)
        self.assertEqual(reg.validate({"h": HASH}, "oi.b/0"), [])
        self.assertEqual([e.code for e in reg.validate({"h": "x"}, "oi.b/0")], ["pattern"])

    def test_refs_in_any_order(self):
        f = self.folder()
        f.put("oi.a/0.json", schema("oi.a/0", properties={"x": {"$ref": "oi.z/0"}}))
        f.put("oi.z/0.json", schema("oi.z/0", properties={"y": {"type": "string"}}))
        Registry().load(f.path, foreign=True)

    def test_sibling_ref(self):
        f = self.folder()
        f.put("common.schema.json", {"$defs": {"S": {"type": "string", "minLength": 2}}})
        f.put("oi.a/0.json", schema("oi.a/0", properties={"s": {"$ref": "common.schema.json#/$defs/S"}}))
        reg = Registry().load(f.path, foreign=True)
        self.assertEqual(reg.validate({"s": "ab"}, "oi.a/0"), [])
        self.assertEqual([e.code for e in reg.validate({"s": "a"}, "oi.a/0")], ["minLength"])

    def test_sibling_refers_sibling_and_validate_schema(self):
        f = self.folder()
        f.put("a.schema.json", {"properties": {"s": {"$ref": "b.schema.json#/$defs/S"}}})
        f.put("b.schema.json", {"$defs": {"S": {"type": "string"}}})
        reg = Registry().load(f.path, foreign=True)
        copy_of_a = loads_strict(f.read("a.schema.json"))  # what a consumer's load_schema returns: a deep copy
        self.assertEqual(reg.validate_schema({"s": "x"}, copy_of_a, base=f.path), [])
        self.assertEqual([(e.path, e.code) for e in reg.validate_schema({"s": 1}, copy_of_a, base=f.path)], [("/s", "type")])
        with self.assertRaisesRegex(SchemaError, "unresolved reference 'b.schema.json'"):
            reg.validate_schema({"s": "x"}, copy_of_a, base=self.folder().path)

    def test_unsafe_refs_rejected_with_reason(self):
        cases = {
            "https://example.org/a.schema.json": "remote or unsafe",
            "file:a.schema.json": "remote or unsafe",
            "../a.schema.json": "remote or unsafe",
            "sub\\a.schema.json": "remote or unsafe",
            "sub/a.schema.json": "neither a kind id nor a sibling",
        }
        for ref, reason in cases.items():
            with self.subTest(ref=ref):
                f = self.folder()
                f.put("oi.a/0.json", schema("oi.a/0", properties={"x": {"$ref": ref}}))
                self.assertLoadFails(reason, f.path, foreign=True)

    def test_unresolved(self):
        for ref, name in (("oi.nope/0", "oi.nope/0"), ("nope.schema.json", "nope.schema.json")):
            with self.subTest(ref=ref):
                f = self.folder()
                f.put("oi.a/0.json", schema("oi.a/0", properties={"x": {"$ref": ref}}))
                self.assertLoadFails(f"unresolved reference '{name}'", f.path, foreign=True)

    def test_hash_alone_still_rejected(self):
        f = self.folder()
        f.put("oi.a/0.json", schema("oi.a/0", properties={"x": {"$ref": "#"}}))
        self.assertLoadFails("reference '#' is not supported", f.path, foreign=True)

    def test_cycle_across_two_documents(self):
        f = self.folder()
        f.put("a.schema.json", {"$defs": {"x": {"$ref": "b.schema.json#/$defs/y"}}})
        f.put("b.schema.json", {"$defs": {"y": {"$ref": "a.schema.json#/$defs/x"}}})
        self.assertLoadFails("cyclic reference", f.path, foreign=True)

    def test_cycle_across_kinds(self):
        f = self.folder()
        f.put("oi.a/0.json", {"title": "oi.a/0", "$defs": {"x": {"$ref": "oi.b/0#/$defs/y"}}})
        f.put("oi.b/0.json", {"title": "oi.b/0", "$defs": {"y": {"$ref": "oi.a/0#/$defs/x"}}})
        self.assertLoadFails("cyclic reference", f.path, foreign=True)

    def test_same_local_pointer_in_two_documents_is_not_a_cycle(self):
        f = self.folder()
        f.put("b.schema.json", {"$defs": {"x": {"type": "integer"}}})
        f.put("oi.a/0.json", {"title": "oi.a/0", "$defs": {"x": {"$ref": "b.schema.json#/$defs/x"}}, "$ref": "#/$defs/x"})
        reg = Registry().load(f.path, foreign=True)
        self.assertEqual(reg.validate(1, "oi.a/0"), [])
        self.assertEqual([e.code for e in reg.validate("s", "oi.a/0")], ["type"])


class FingerprintTest(Base):
    def stable(self, f, body=None):
        f.put("oi.thing/1.json", body or schema("oi.thing/1"))

    def test_fingerprint_value(self):
        import hashlib
        s = schema("oi.thing/1", meta={"a": 1})
        self.assertEqual(fingerprint(s), "sha256:" + hashlib.sha256(canonical_bytes(s)).hexdigest())
        self.assertNotEqual(fingerprint(s), fingerprint({k: v for k, v in s.items() if k != "meta"}))

    def test_stable_without_file(self):
        f = self.folder()
        self.stable(f)
        self.assertLoadFails(r"oi\.thing/1: stable kind without an entry", f.path, foreign=True)

    def test_pin_then_load(self):
        f = self.folder()
        self.stable(f)
        f.put("oi.thing/0.json", schema("oi.thing/0"))
        pins = Registry().pin(f.path)
        self.assertEqual(list(pins), ["oi.thing/1"])  # /0 is not pinned
        self.assertEqual(f.read("fingerprints.json"), json.dumps(pins, indent=2, sort_keys=True) + "\n")
        Registry().load(f.path, foreign=True)

    def test_missing_entry_among_others(self):
        f = self.folder()
        self.stable(f)
        f.put("oi.other/1.json", schema("oi.other/1"))
        Registry().pin(f.path)
        f.put("oi.new/2.json", schema("oi.new/2"))
        self.assertLoadFails(r"oi\.new/2: stable kind without an entry", f.path, foreign=True)

    def test_one_byte_change_is_a_mismatch(self):
        f = self.folder()
        self.stable(f)
        Registry().pin(f.path)
        f.put("oi.thing/1.json", schema("oi.thing/1", description="x"))
        self.assertLoadFails(r"oi\.thing/1: fingerprint sha256:[0-9a-f]{64} does not match fingerprints\.json", f.path, foreign=True)

    def test_entry_for_provisional_kind(self):
        f = self.folder()
        f.put("oi.thing/0.json", schema("oi.thing/0"))
        f.put("fingerprints.json", {"oi.thing/0": HASH})
        self.assertLoadFails(r"oi\.thing/0 is provisional", f.path, foreign=True)

    def test_entry_for_absent_kind(self):
        f = self.folder()
        f.put("oi.thing/0.json", schema("oi.thing/0"))
        f.put("fingerprints.json", {"oi.gone/1": HASH})
        self.assertLoadFails(r"entry for oi\.gone/1, which is not in the folder", f.path, foreign=True)

    def test_bad_entry_shapes(self):
        for content, reason in (({"nope": HASH}, "is not a kind id"), ({"oi.thing/1": "abc"}, "fingerprint must be"), ([], "must be an object")):
            with self.subTest(content=content):
                f = self.folder()
                self.stable(f)
                f.put("fingerprints.json", content)
                self.assertLoadFails(reason, f.path, foreign=True)

    def test_pin_refuses_to_change_an_entry(self):
        f = self.folder()
        self.stable(f)
        Registry().pin(f.path)
        before = f.read("fingerprints.json")
        f.put("oi.thing/1.json", schema("oi.thing/1", description="x"))
        with self.assertRaisesRegex(SchemaError, r"oi\.thing/1: fingerprint changed .*publish oi\.thing/2 instead"):
            Registry().pin(f.path)
        self.assertEqual(f.read("fingerprints.json"), before)

    def test_pin_adds_missing_and_keeps_existing(self):
        f = self.folder()
        self.stable(f)
        first = Registry().pin(f.path)
        f.put("oi.more/1.json", schema("oi.more/1"))
        second = Registry().pin(f.path)
        self.assertEqual(sorted(second), ["oi.more/1", "oi.thing/1"])
        self.assertEqual(second["oi.thing/1"], first["oi.thing/1"])
        self.assertTrue(f.read("fingerprints.json").endswith("}\n"))
        self.assertEqual(Registry().pin(f.path), second)  # idempotent


class OwnerTest(Base):
    def test_owner_rule_both_ways(self):
        f = self.folder()
        f.put("gworld.pack/0.json", schema("gworld.pack/0"))
        self.assertLoadFails(r"gworld\.pack/0: namespace is not that of owner 'gmod'", f.path, owner="gmod")
        Registry().load(f.path, foreign=True)
        Registry().load(f.path, owner="gworld")

    def test_exactly_one_of_owner_and_foreign(self):
        f = self.folder()
        f.put("oi.a/0.json", schema("oi.a/0"))
        self.assertLoadFails("exactly one of owner", f.path)
        self.assertLoadFails("exactly one of owner", f.path, owner="oi", foreign=True)

    def test_unknown_owner(self):
        f = self.folder()
        self.assertLoadFails("owner 'nope' is not in namespaces.json", f.path, owner="nope")

    def test_namespaces_table(self):
        table = loads_strict((GART / "namespaces.json").read_text(encoding="utf-8"))
        self.assertEqual(
            sorted(table), sorted(["gdev", "gimg", "gvoice", "oi", "gve", "gmod", "grun", "gforge", "gworld", "gart"])
        )
        self.assertEqual(table["oi"], {"repo": "galivelop-client-catcher"})
        self.assertEqual(table["gworld"], {"repo": None})


class ValidateTest(Base):
    def setUp(self):
        self.reg = Registry()

    def test_default_registry(self):
        self.assertIn("gart.common/0", self.reg.kinds())
        self.assertIn("gart.diff/0", self.reg.kinds())

    def test_get_is_a_copy_and_unknown_raises(self):
        got = self.reg.get("gart.common/0")
        got["title"] = "changed"
        self.assertEqual(self.reg.get("gart.common/0")["title"], "gart.common/0")
        with self.assertRaisesRegex(SchemaError, "unknown kind 'gart.nope/0'"):
            self.reg.get("gart.nope/0")

    def test_validate_by_schema_field(self):
        f = self.folder()
        f.put("oi.a/0.json", schema("oi.a/0", required=["schema", "n"], properties={"n": {"type": "integer"}}))
        self.reg.load(f.path, foreign=True)
        self.assertEqual(self.reg.validate({"schema": "oi.a/0", "n": 1}), [])
        errors = self.reg.validate({"schema": "oi.a/0", "n": "x"})
        self.assertEqual([(e.path, e.code) for e in errors], [("/n", "type")])
        # An explicit kind wins over the field; here the schema itself demands `schema`.
        self.assertEqual(self.reg.validate({"n": 1}, "oi.a/0"), [("", "required", {"name": "schema"})])

    def test_three_error_cases(self):
        self.assertEqual(self.reg.validate([1]), [("", "required", {"name": "schema"})])
        self.assertEqual(self.reg.validate({"n": 1}), [("", "required", {"name": "schema"})])
        got = self.reg.validate({"schema": "nope"})
        self.assertEqual((got[0].path, got[0].code, got[0].params["value"]), ("/schema", "kind_invalid", "nope"))
        self.assertEqual(self.reg.validate({"schema": 3})[0].code, "kind_invalid")
        self.assertEqual(self.reg.validate({"schema": "oi.zzz/0"}), [("/schema", "kind_unknown", {"kind": "oi.zzz/0"})])

    def test_diff_json_validates(self):
        artifact = loads_strict((GART / "diff.json").read_text(encoding="utf-8"))
        self.assertEqual(self.reg.validate(artifact), [])
        artifact["rows"] = "x"
        self.assertEqual([e.code for e in self.reg.validate(artifact)], ["type"])

    def test_gart_common_defs(self):
        check = self._def

        good = {
            "ContentHash": [HASH],
            "ArtifactRef": [{"hash": HASH}, {"kind": "gworld.pack/1", "hash": HASH}],
            "License": [{"id": "MIT", "author": "A"}, {"id": "Apache-2.0", "author": "A"}, {"id": "LicenseRef-mine", "author": "A"}],
            "Timestamp": ["2026-11-28T10:20:30Z", "2026-11-28T10:20:30.123Z"],
            "Meta": [{}, {"a": 1}],
        }
        bad = {
            "ContentHash": ["sha256:" + "A" * 64, "sha256:abc", "md5:" + "a" * 64, 1],
            "ArtifactRef": [{}, {"kind": "gworld.pack/1"}, {"kind": "bad", "hash": HASH}, {"hash": HASH, "extra": 1}, {"hash": "x"}],
            "License": [{"id": "MIT"}, {"author": "A"}, {"id": "MIT", "author": ""}, {"id": "not spdx!", "author": "A"}, {"id": "MIT", "author": "A", "x": 1}],
            "Timestamp": ["2026-11-28T10:20:30", "2026-11-28 10:20:30Z", "2026-13-28T10:20:30Z", "2026-11-28T10:20:30+01:00"],
            "Meta": [[], "x", 1],
        }
        for name, values in good.items():
            for value in values:
                with self.subTest(name=name, value=value):
                    self.assertEqual(check(name, value), [])
        for name, values in bad.items():
            for value in values:
                with self.subTest(name=name, value=value):
                    self.assertNotEqual(check(name, value), [])

    def _def(self, name, value):
        return self.reg.validate_schema(value, {"$ref": f"gart.common/0#/$defs/{name}"})

    def test_gart_common_has_only_defs(self):
        s = self.reg.get("gart.common/0")
        self.assertEqual(sorted(k for k in s if k not in ("$schema", "title", "description")), ["$defs"])
        self.assertEqual(sorted(s["$defs"]), ["ArtifactRef", "ContentHash", "License", "Meta", "Timestamp"])

    def test_deterministic_across_registries(self):
        a = self.reg.validate({"schema": "gart.diff/0", "rows": 1, "copies": 2})
        b = Registry().validate({"schema": "gart.diff/0", "rows": 1, "copies": 2})
        self.assertEqual(a, b)
        self.assertEqual(a, sorted(a, key=lambda e: (e.path, e.code)))


if __name__ == "__main__":
    unittest.main()
