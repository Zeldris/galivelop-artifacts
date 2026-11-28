"""Every schema file of the copies passes `check_schema` (needs the clones; skipped without `GART_COPIES`).

`GART_COPIES="gdev=/path/to/clone,oi=/path/to/clone,gimg=...,gvoice=..."`. Each `*.json` under a `schemas` folder of a
clone must be accepted, except those that only fail because of a `$ref` to a sibling file: the `gart.diff/0`
row "pendiente gart-H4" (Registry). Those must fail with "is not local" and are only counted.
The private clones are read, never copied into this repo.
"""

import os
import unittest
from pathlib import Path

from gart import SchemaError, check_schema, loads_strict


def _copies():
    raw = os.environ.get("GART_COPIES", "").strip()
    out = {}
    for item in filter(None, (part.strip() for part in raw.split(","))):
        name, _, path = item.partition("=")
        out[name.strip()] = Path(path.strip())
    return out


class CopiesSchemasTests(unittest.TestCase):
    def test_every_schema_of_the_copies_is_accepted(self):
        copies = _copies()
        if not copies:
            self.skipTest("GART_COPIES is not set (name=path of each clone, comma separated)")
        for name, root in copies.items():
            with self.subTest(copy=name):
                self.assertTrue(root.is_dir(), f"{name}: {root} is not a directory")
                files = sorted(f for d in root.rglob("schemas") if d.is_dir() for f in d.rglob("*.json"))
                self.assertTrue(files, f"{name}: no schema under {root}")
                accepted = pending = 0
                for path in files:
                    with self.subTest(copy=name, file=str(path.relative_to(root))):
                        try:
                            check_schema(loads_strict(path.read_text(encoding="utf-8")))
                            accepted += 1
                        except SchemaError as exc:
                            self.assertIn("is not local", str(exc))  # the only reason allowed: gart-H4
                            pending += 1
                print(f"copies[{name}]: {accepted} ok, {pending} pending gart-H4")


if __name__ == "__main__":
    unittest.main()
