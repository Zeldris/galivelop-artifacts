"""DDD invariant 1: a `KindId` matches `^[a-z][a-z0-9]*\\.[a-z][a-z0-9_.]*/(0|[1-9][0-9]*)$`."""

import unittest

from gart import KindId, KindIdError

VALID = [
    ("gworld.pack/0", "gworld", "pack", 0),
    ("gve.run/1", "gve", "run", 1),
    ("gart.common/0", "gart", "common", 0),
    ("gdev.intervention/0", "gdev", "intervention", 0),
    ("oi.signal_score/12", "oi", "signal_score", 12),
    ("g2.a.b.c/3", "g2", "a.b.c", 3),
    ("a.b/0", "a", "b", 0),
    ("a.b9/10", "a", "b9", 10),
]

INVALID = [
    "",
    "gworld.pack",          # no version
    "gworld/0",             # no name
    ".pack/0",              # empty namespace
    "gworld./0",            # empty name
    "Gworld.pack/0",        # uppercase namespace
    "gworld.Pack/0",        # uppercase name
    "1gworld.pack/0",       # namespace starts with a digit
    "g_world.pack/0",       # underscore in namespace
    "gworld.1pack/0",       # name starts with a digit
    "gworld._pack/0",       # name starts with underscore
    "gworld.pack-x/0",      # hyphen in name
    "gworld.pack/01",       # leading zero
    "gworld.pack/-1",       # negative
    "gworld.pack/1.0",      # not an integer
    "gworld.pack/",         # empty version
    "gworld.pack/0\n",      # trailing newline (`$` would accept it)
    " gworld.pack/0",       # leading space
    "gworld.pack/0 ",       # trailing space
    "gworld.pack/٣",        # Unicode digit
    "gwörld.pack/0",        # Unicode letter
    "gworld.pack/0/1",      # two versions
]


class ParseTest(unittest.TestCase):
    def test_valid(self):
        for text, ns, name, version in VALID:
            with self.subTest(text=text):
                kind = KindId.parse(text)
                self.assertEqual((kind.namespace, kind.name, kind.version), (ns, name, version))
                self.assertEqual(str(kind), text)
                self.assertTrue(KindId.is_valid(text))

    def test_invalid_says_why(self):
        for text in INVALID:
            with self.subTest(text=text):
                self.assertFalse(KindId.is_valid(text))
                with self.assertRaises(KindIdError) as caught:
                    KindId.parse(text)
                self.assertEqual(caught.exception.code, "kind_id.format")
                self.assertEqual(caught.exception.text, text)
                self.assertIn("does not match", str(caught.exception))

    def test_not_a_string(self):
        for value in (None, 0, b"gworld.pack/0", ["gworld.pack/0"]):
            with self.subTest(value=value):
                self.assertFalse(KindId.is_valid(value))
                with self.assertRaises(KindIdError) as caught:
                    KindId.parse(value)
                self.assertEqual(caught.exception.code, "kind_id.type")
                self.assertIn("not a string", str(caught.exception))

    def test_is_a_value_error(self):
        with self.assertRaises(ValueError):
            KindId.parse("nope")


class ValueObjectTest(unittest.TestCase):
    def test_constructor_checks_the_format(self):
        self.assertEqual(KindId("gworld", "pack", 0), KindId.parse("gworld.pack/0"))
        for args in (("Gworld", "pack", 0), ("gworld", "", 0), ("gworld", "pack", -1)):
            with self.subTest(args=args):
                with self.assertRaises(KindIdError) as caught:
                    KindId(*args)
                self.assertEqual(caught.exception.code, "kind_id.format")
        for version in ("0", True, 1.0):
            with self.subTest(version=version):
                with self.assertRaises(KindIdError) as caught:
                    KindId("gworld", "pack", version)
                self.assertIn("not an integer", str(caught.exception))

    def test_frozen_hashable_ordered(self):
        a, b = KindId.parse("gworld.pack/0"), KindId.parse("gworld.pack/1")
        with self.assertRaises(AttributeError):
            a.version = 1
        self.assertEqual(len({a, KindId.parse("gworld.pack/0"), b}), 2)
        self.assertLess(a, b)
        self.assertLess(KindId.parse("gworld.pack/2"), KindId.parse("gworld.pack/10"))

    def test_provisional_and_stable(self):
        zero, one = KindId.parse("gmod.machine/0"), KindId.parse("gve.run/1")
        self.assertTrue(zero.provisional)
        self.assertFalse(zero.stable)
        self.assertFalse(one.provisional)
        self.assertTrue(one.stable)

    def test_next(self):
        self.assertEqual(KindId.parse("gve.run/1").next(), KindId.parse("gve.run/2"))
        self.assertEqual(str(KindId.parse("grun.lock/0").next()), "grun.lock/1")


if __name__ == "__main__":
    unittest.main()
