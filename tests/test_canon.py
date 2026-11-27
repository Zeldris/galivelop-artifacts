"""Canon (gart-H9): fixed vectors, rejections, invariants 9 and 14, determinism."""

import enum
import hashlib
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from gart import CanonError, canonical_bytes, content_hash, file_hash, loads_strict

ROOT = Path(__file__).resolve().parent.parent
VECTORS = json.loads((ROOT / "tests" / "vectors" / "canon.json").read_text(encoding="utf-8"))


class VectorTests(unittest.TestCase):
    def test_bytes_and_hash(self):
        for case in VECTORS["cases"]:
            with self.subTest(case["name"]):
                data = canonical_bytes(loads_strict(case["input"]))
                self.assertEqual(data.hex(), case["hex"])
                self.assertEqual("sha256:" + hashlib.sha256(data).hexdigest(), case["hash"])
                self.assertEqual(content_hash(loads_strict(case["input"])), case["hash"])

    def test_rejects(self):
        reasons = {
            "canon.duplicate_key": "duplicate",
            "canon.nan": "NaN",
            "canon.infinity": "infinity",
            "canon.int_range": "outside",
            "canon.negative_zero": "negative zero",
            "canon.syntax": "invalid JSON",
            "canon.type": "surrogate",
        }
        for case in VECTORS["reject"]:
            with self.subTest(case["name"]):
                with self.assertRaises(CanonError) as cm:
                    loads_strict(case["input"])
                self.assertEqual(cm.exception.code, case["code"])
                self.assertIn(case.get("reason", reasons[case["code"]]).lower(), str(cm.exception).lower())

    def test_int_range_vectors_have_reason(self):
        for case in VECTORS["reject"]:
            if case["code"] == "canon.int_range":
                with self.subTest(case["name"]):
                    self.assertIn(case.get("reason"), ("integer outside", "number outside"))

    def test_nested_duplicate_key_path_is_empty(self):
        with self.assertRaises(CanonError) as cm:
            loads_strict('{"a": [{"b": 1, "b": 2}]}')
        self.assertEqual(cm.exception.code, "canon.duplicate_key")
        self.assertEqual(cm.exception.path, "")

    def test_deep_text(self):
        with self.assertRaises(CanonError) as cm:
            loads_strict("[" * 100000 + "]" * 100000)
        self.assertEqual(cm.exception.code, "canon.depth")
        self.assertIn("nested too deeply", str(cm.exception))

    def test_infinity_reason(self):
        for text in ("[Infinity]", "-Infinity", "1e400"):
            with self.assertRaises(CanonError) as cm:
                loads_strict(text)
            self.assertIn("infinity", str(cm.exception).lower())


class ValueTests(unittest.TestCase):
    def check(self, value, code, reason):
        with self.assertRaises(CanonError) as cm:
            canonical_bytes(value)
        self.assertEqual(cm.exception.code, code)
        self.assertIn(reason, str(cm.exception).lower())
        return cm.exception

    def test_numbers(self):
        self.check(float("nan"), "canon.nan", "nan")
        self.check(float("inf"), "canon.infinity", "infinity")
        self.check(float("-inf"), "canon.infinity", "infinity")
        self.check(-0.0, "canon.negative_zero", "negative zero")
        self.check(2**53, "canon.int_range", "integer outside")
        self.check(-(2**53), "canon.int_range", "integer outside")
        self.assertEqual(canonical_bytes(2**53 - 1), b"9007199254740991")

    def test_subclasses(self):
        class Num(enum.IntEnum):
            A = 7

        class Flt(float):
            pass

        self.assertEqual(canonical_bytes(Num.A), b"7")
        self.assertEqual(canonical_bytes([Num.A, Flt(0.5), Flt(2.0)]), b"[7,0.5,2]")

    def test_depth(self):
        deep = []
        for _ in range(100000):
            deep = [deep]
        cyclic = []
        cyclic.append(cyclic)
        for value in (deep, cyclic):
            err = self.check(value, "canon.depth", "nested too deeply (or cyclic)")
            self.assertTrue(err.path.startswith("/0/0/"), err.path)

    def test_depth_limit_is_exact(self):
        from gart.canon import MAX_DEPTH

        text = "[" * MAX_DEPTH + "]" * MAX_DEPTH
        value = loads_strict(text)
        self.assertEqual(canonical_bytes(value), text.encode())
        deeper = "[" * (MAX_DEPTH + 1) + "]" * (MAX_DEPTH + 1)
        with self.assertRaises(CanonError) as cm:
            loads_strict(deeper)
        self.assertEqual(cm.exception.code, "canon.depth")
        self.assertIn(f"more than {MAX_DEPTH}", str(cm.exception))
        self.check([value], "canon.depth", "nested too deeply (or cyclic)")
        nested = {"a": value}
        self.check(nested, "canon.depth", "nested too deeply (or cyclic)")

    def test_bool_is_bool(self):
        self.assertEqual(canonical_bytes([True, False, 1, 0]), b"[true,false,1,0]")

    def test_types(self):
        self.check({1: "a"}, "canon.type", "key")
        self.check({"a": {1, 2}}, "canon.type", "not a json type")
        self.check(b"x", "canon.type", "not a json type")
        self.check("\ud800", "canon.type", "surrogate")

    def test_path_in_message(self):
        err = self.check({"a": [1, {"b/c": 2**60}]}, "canon.int_range", "/a/1/b~1c")
        self.assertEqual(err.path, "/a/1/b~1c")

    def test_float_integral(self):
        self.assertEqual(canonical_bytes(1.0), b"1")
        self.assertEqual(canonical_bytes([1e15, 1e-7, 0.5]), b"[1000000000000000,1e-7,0.5]")

    def test_big_float_rejected_on_write(self):
        err = self.check(1e20, "canon.int_range", "number outside")
        self.assertIn("1e+20", err.args[0])
        self.assertEqual(canonical_bytes(9007199254740991.0), b"9007199254740991")

    def test_round_trip(self):
        for case in VECTORS["cases"]:
            with self.subTest(case["name"]):
                first = canonical_bytes(loads_strict(case["input"]))
                again = canonical_bytes(loads_strict(first.decode("utf-8")))
                self.assertEqual(first, again)


class HashTests(unittest.TestCase):
    base = {"kind": "a.b/1", "x": 1, "meta": {"date": "2026-01-01"}}

    def test_meta_ignored(self):
        other = dict(self.base, meta={"date": "2030-05-05", "host": "m"})
        self.assertEqual(content_hash(self.base), content_hash(other))
        self.assertEqual(content_hash(self.base), content_hash({"kind": "a.b/1", "x": 1}))

    def test_other_field_counts(self):
        self.assertNotEqual(content_hash(self.base), content_hash(dict(self.base, x=2)))

    def test_nested_meta_counts(self):
        a = {"x": {"meta": 1}}
        b = {"x": {"meta": 2}}
        self.assertNotEqual(content_hash(a), content_hash(b))

    def test_non_dict(self):
        data = canonical_bytes([1])
        self.assertEqual(content_hash([1]), "sha256:" + hashlib.sha256(data).hexdigest())

    def test_file_hash(self):
        payload = b"\r\n raw bytes \x00" * 200000
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "f.bin"
            path.write_bytes(payload)
            self.assertEqual(file_hash(path), "sha256:" + hashlib.sha256(payload).hexdigest())
            self.assertEqual(file_hash(str(path)), file_hash(path))


class DeterminismTests(unittest.TestCase):
    def test_hash_seeds(self):
        code = (
            "import sys; from gart import canonical_bytes, loads_strict;"
            "v = loads_strict(sys.argv[1]); sys.stdout.write(canonical_bytes(v).hex())"
        )
        text = VECTORS["cases"][0]["input"]
        results = set()
        for seed in range(20):
            env = dict(os.environ, PYTHONHASHSEED=str(seed), PYTHONPATH=str(ROOT))
            proc = subprocess.run(
                [sys.executable, "-c", code, text], env=env, capture_output=True, text=True, check=True
            )
            results.add(proc.stdout)
        self.assertEqual(results, {VECTORS["cases"][0]["hex"]})


if __name__ == "__main__":
    unittest.main()
