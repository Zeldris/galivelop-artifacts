"""The JSON Schema subset validator: one test per keyword, with the `code` and `path` of each error."""

import unittest

from gart import SchemaError, ValidationError, check_schema, validate
from gart.schema import ANNOTATIONS, CODES, VALIDATING


def errs(instance, schema):
    return [(e.path, e.code) for e in validate(instance, schema)]


class TypeTests(unittest.TestCase):
    def test_each_type_accepts_and_rejects(self):
        cases = {
            "object": ({}, [1], "array"), "array": ([], {}, "object"), "string": ("a", 1, "integer"),
            "integer": (3, "3", "string"), "number": (1.5, "1.5", "string"), "boolean": (True, 0, "integer"),
            "null": (None, 0, "integer"),
        }
        for name, (good, bad, actual) in cases.items():
            with self.subTest(type=name):
                self.assertEqual(validate(good, {"type": name}), [])
                self.assertEqual(validate(bad, {"type": name}),
                                 [ValidationError("", "type", {"expected": name, "actual": actual})])

    def test_type_list(self):
        sch = {"type": ["string", "null"]}
        self.assertEqual(validate(None, sch), [])
        self.assertEqual(validate("a", sch), [])
        self.assertEqual(validate(1, sch), [ValidationError("", "type", {"expected": "string/null", "actual": "integer"})])

    def test_bool_is_not_integer_or_number(self):
        for name in ("integer", "number"):
            self.assertEqual(errs(True, {"type": name}), [("", "type")])
        self.assertEqual(errs(1, {"type": "boolean"}), [("", "type")])

    def test_whole_float_is_integer(self):
        self.assertEqual(validate(1.0, {"type": "integer"}), [])
        self.assertEqual(errs(1.5, {"type": "integer"}), [("", "type")])

    def test_int_is_number(self):
        self.assertEqual(validate(2, {"type": "number"}), [])

    def test_inf_and_nan_are_not_numbers(self):
        for value in (float("inf"), float("-inf"), float("nan")):
            for name in ("number", "integer"):
                with self.subTest(value=value, type=name):
                    self.assertEqual(errs(value, {"type": name}), [("", "type")])

    def test_actual_names_the_json_type_of_the_instance(self):
        cases = [(True, "boolean"), (None, "null"), (3, "integer"), (1.0, "integer"), (1.5, "number"),
                 ("s", "string"), ([], "array"), ({}, "object"), (float("inf"), "number")]
        for value, actual in cases:
            with self.subTest(value=value):
                got = validate(value, {"type": "object" if actual != "object" else "array"})
                self.assertEqual(got[0].params["actual"], actual)

    def test_unknown_type_is_a_schema_error(self):
        with self.assertRaisesRegex(SchemaError, "unknown type 'text'"):
            check_schema({"type": "text"})
        with self.assertRaisesRegex(SchemaError, "unknown type 5"):
            check_schema({"type": [5]})


class ObjectKeywordTests(unittest.TestCase):
    def test_properties_with_nested_path(self):
        sch = {"properties": {"a": {"properties": {"b": {"type": "integer"}}}}}
        self.assertEqual(validate({"a": {"b": 1}}, sch), [])
        self.assertEqual(validate({"a": {"b": "x"}}, sch),
                         [ValidationError("/a/b", "type", {"expected": "integer", "actual": "string"})])

    def test_required(self):
        sch = {"required": ["a", "b"]}
        self.assertEqual(validate({"a": 1, "b": 2}, sch), [])
        self.assertEqual(validate({"a": 1}, sch), [ValidationError("", "required", {"name": "b"})])

    def test_additional_properties_false(self):
        sch = {"properties": {"a": {}}, "additionalProperties": False}
        self.assertEqual(validate({"a": 1}, sch), [])
        self.assertEqual(validate({"a": 1, "z": 2}, sch),
                         [ValidationError("/z", "additionalProperties", {"name": "z"})])

    def test_additional_properties_schema(self):
        sch = {"properties": {"a": {}}, "additionalProperties": {"type": "integer"}}
        self.assertEqual(validate({"a": "free", "z": 2}, sch), [])
        self.assertEqual(validate({"z": "x"}, sch), [ValidationError("/z", "type", {"expected": "integer", "actual": "string"})])

    def test_additional_properties_true(self):
        self.assertEqual(validate({"z": 1}, {"additionalProperties": True}), [])

    def test_property_names(self):
        sch = {"propertyNames": {"pattern": "^[a-z]+$"}}
        self.assertEqual(validate({"abc": 1}, sch), [])
        self.assertEqual(validate({"Bad": 1}, sch),
                         [ValidationError("/Bad", "propertyNames", {"name": "Bad", "reason": "pattern", "detail": {"pattern": "^[a-z]+$"}})])

    def test_min_properties(self):
        sch = {"minProperties": 2}
        self.assertEqual(validate({"a": 1, "b": 2}, sch), [])
        self.assertEqual(validate({"a": 1}, sch), [ValidationError("", "minProperties", {"limit": 2})])

    def test_keywords_ignore_other_types(self):
        self.assertEqual(validate("x", {"required": ["a"], "minProperties": 3, "minItems": 3}), [])

    def test_pointer_escapes(self):
        sch = {"properties": {"a/b": {"type": "integer"}, "c~d": {"type": "integer"}}}
        self.assertEqual(errs({"a/b": "x", "c~d": "y"}, sch), [("/a~1b", "type"), ("/c~0d", "type")])


class ArrayKeywordTests(unittest.TestCase):
    def test_items(self):
        sch = {"items": {"type": "integer"}}
        self.assertEqual(validate([1, 2], sch), [])
        self.assertEqual(validate([1, "x"], sch), [ValidationError("/1", "type", {"expected": "integer", "actual": "string"})])

    def test_items_path_is_nested(self):
        sch = {"items": {"properties": {"id": {"type": "integer"}}}}
        self.assertEqual(errs([{"id": 1}, {"id": "x"}], sch), [("/1/id", "type")])

    def test_min_items(self):
        self.assertEqual(validate([1], {"minItems": 1}), [])
        self.assertEqual(validate([], {"minItems": 1}), [ValidationError("", "minItems", {"limit": 1})])

    def test_max_items(self):
        self.assertEqual(validate([1], {"maxItems": 1}), [])
        self.assertEqual(validate([1, 2], {"maxItems": 1}), [ValidationError("", "maxItems", {"limit": 1})])


class ScalarKeywordTests(unittest.TestCase):
    def test_enum(self):
        sch = {"enum": ["a", 2, None]}
        for ok in ("a", 2, 2.0, None):
            self.assertEqual(validate(ok, sch), [])
        self.assertEqual(validate("b", sch), [ValidationError("", "enum", {"allowed": '"a", 2, null'})])

    def test_enum_and_const_do_not_equate_bool_and_number(self):
        self.assertEqual(errs(True, {"enum": [1]}), [("", "enum")])
        self.assertEqual(errs(0, {"enum": [False]}), [("", "enum")])
        self.assertEqual(errs(1, {"const": True}), [("", "const")])

    def test_enum_compares_containers_deeply(self):
        self.assertEqual(validate({"a": [1.0]}, {"enum": [{"a": [1]}]}), [])
        self.assertEqual(errs({"a": [True]}, {"enum": [{"a": [1]}]}), [("", "enum")])

    def test_const(self):
        self.assertEqual(validate("x", {"const": "x"}), [])
        self.assertEqual(validate("y", {"const": "x"}), [ValidationError("", "const", {"expected": '"x"'})])

    def test_pattern_uses_search(self):
        self.assertEqual(validate("xxabcxx", {"pattern": "abc"}), [])
        self.assertEqual(validate("xyz", {"pattern": "abc"}), [ValidationError("", "pattern", {"pattern": "abc"})])

    def test_pattern_dollar_does_not_match_before_trailing_newline(self):
        sch = {"pattern": "^[a-z]+$"}
        self.assertEqual(validate("abc", sch), [])
        self.assertEqual(errs("abc\n", sch), [("", "pattern")])
        self.assertEqual(validate("a$", {"pattern": "^a[$]$"}), [])
        self.assertEqual(validate("a$", {"pattern": "^a\\$$"}), [])

    def test_pattern_is_ascii(self):
        self.assertEqual(errs("١", {"pattern": "^\\d$"}), [("", "pattern")])
        self.assertEqual(validate("1", {"pattern": "^\\d$"}), [])

    def test_min_length(self):
        self.assertEqual(validate("ab", {"minLength": 2}), [])
        self.assertEqual(validate("a", {"minLength": 2}), [ValidationError("", "minLength", {"limit": 2})])

    def test_max_length(self):
        self.assertEqual(validate("ab", {"maxLength": 2}), [])
        self.assertEqual(validate("abc", {"maxLength": 2}), [ValidationError("", "maxLength", {"limit": 2})])

    def test_minimum(self):
        self.assertEqual(validate(5, {"minimum": 5}), [])
        self.assertEqual(validate(4.5, {"minimum": 5}), [ValidationError("", "minimum", {"limit": 5})])

    def test_maximum(self):
        self.assertEqual(validate(5, {"maximum": 5}), [])
        self.assertEqual(validate(6, {"maximum": 5}), [ValidationError("", "maximum", {"limit": 5})])

    def test_bounds_ignore_bool(self):
        self.assertEqual(validate(True, {"minimum": 5}), [])

    def test_boolean_schemas(self):
        self.assertEqual(validate(1, True), [])
        self.assertEqual(validate(1, False), [ValidationError("", "false", {})])
        self.assertEqual(errs({"a": 1}, {"properties": {"a": False}}), [("/a", "false")])


class RefTests(unittest.TestCase):
    def test_ref_into_defs(self):
        sch = {"$defs": {"n": {"type": "integer"}}, "properties": {"a": {"$ref": "#/$defs/n"}}}
        self.assertEqual(validate({"a": 1}, sch), [])
        self.assertEqual(validate({"a": "x"}, sch), [ValidationError("/a", "type", {"expected": "integer", "actual": "string"})])

    def test_defs_alone_validate_nothing(self):
        self.assertEqual(validate(1, {"$defs": {"n": {"type": "string"}}}), [])

    def test_defs_are_checked(self):
        with self.assertRaisesRegex(SchemaError, r"#/\$defs/n: unsupported keyword 'format'"):
            check_schema({"$defs": {"n": {"format": "x"}}})

    def test_ref_to_root(self):
        sch = {"type": "object", "properties": {"child": {"$ref": "#"}}}
        self.assertEqual(errs({"child": {"child": 1}}, sch), [("/child/child", "type")])

    def test_self_reference_is_a_schema_error_not_recursion(self):
        with self.assertRaisesRegex(SchemaError, "cyclic reference"):
            validate(1, {"$ref": "#"})
        with self.assertRaisesRegex(SchemaError, "cyclic reference"):
            check_schema({"$defs": {"a": {"$ref": "#/$defs/b"}, "b": {"$ref": "#/$defs/a"}},
                          "$ref": "#/$defs/a"})

    def test_ref_must_be_local(self):
        for ref in ("other.schema.json", "other.schema.json#/a", "http://x/y#/a"):
            with self.subTest(ref=ref):
                with self.assertRaisesRegex(SchemaError, "is not local"):
                    check_schema({"$ref": ref})

    def test_unresolved_ref(self):
        with self.assertRaisesRegex(SchemaError, "unresolved reference '#/\\$defs/nope'"):
            check_schema({"$ref": "#/$defs/nope"})

    def test_ref_fragment_must_be_a_pointer(self):
        with self.assertRaisesRegex(SchemaError, "fragment must be a JSON pointer"):
            check_schema({"$ref": "#defs"})

    def test_ref_must_be_a_string(self):
        with self.assertRaisesRegex(SchemaError, "reference must be a string"):
            check_schema({"$ref": 3})


class MaxPropertiesTests(unittest.TestCase):
    def test_max_properties(self):
        sch = {"maxProperties": 1}
        self.assertEqual(validate({"a": 1}, sch), [])
        self.assertEqual(validate({"a": 1, "b": 2}, sch), [ValidationError("", "maxProperties", {"limit": 1})])
        self.assertEqual(validate("xx", sch), [])  # only objects are counted

    def test_max_properties_nested_path(self):
        self.assertEqual(errs({"o": {"a": 1, "b": 2}}, {"properties": {"o": {"maxProperties": 1}}}),
                         [("/o", "maxProperties")])

    def test_malformed_max_properties(self):
        for bad in (-1, 1.5, True, "1", None):
            with self.subTest(bad=bad):
                with self.assertRaisesRegex(SchemaError, "#/maxProperties: must be a non-negative integer"):
                    check_schema({"maxProperties": bad})


class DependentRequiredTests(unittest.TestCase):
    SCH = {"type": "object", "dependentRequired": {"b": ["a", "c"]}}

    def test_dependent_required(self):
        for ok in ({}, {"a": 1}, {"a": 1, "b": 2, "c": 3}):
            self.assertEqual(validate(ok, self.SCH), [])
        self.assertEqual(validate({"b": 2, "c": 3}, self.SCH),
                         [ValidationError("", "dependentRequired", {"name": "a", "trigger": "b"})])
        self.assertEqual([e.params["name"] for e in validate({"b": 2}, self.SCH)], ["a", "c"])

    def test_dependent_required_nested_path_and_non_object(self):
        sch = {"properties": {"o": {"dependentRequired": {"x": ["y"]}}}}
        self.assertEqual(errs({"o": {"x": 1}}, sch), [("/o", "dependentRequired")])
        self.assertEqual(validate("x", {"dependentRequired": {"x": ["y"]}}), [])

    def test_malformed_dependent_required(self):
        cases = [
            ([], "#/dependentRequired: must be an object"),
            ({"x": "y"}, "#/dependentRequired/x: must be a list of strings"),
            ({"x": [1]}, "#/dependentRequired/x: must be a list of strings"),
            ({"x": ["y", "y"]}, "#/dependentRequired/x: items must be unique"),
        ]
        for bad, why in cases:
            with self.subTest(bad=bad):
                with self.assertRaises(SchemaError) as cm:
                    check_schema({"dependentRequired": bad})
                self.assertIn(why, str(cm.exception))


class ConditionalTests(unittest.TestCase):
    SCH = {"allOf": [
        {"if": {"required": ["t"], "properties": {"t": {"const": "a"}}}, "then": {"required": ["x"]}},
        {"if": {"required": ["t"], "properties": {"t": {"const": "b"}}},
         "then": {"properties": {"x": False}}, "else": {"required": ["y"]}},
    ]}

    def test_if_then_else(self):
        check_schema(self.SCH)
        self.assertEqual(errs({"t": "a", "x": 1, "y": 1}, self.SCH), [])
        self.assertEqual(errs({"t": "a", "y": 1}, self.SCH), [("", "required")])
        self.assertEqual(errs({"t": "b", "x": 1}, self.SCH), [("/x", "false")])
        self.assertEqual(errs({"t": "b"}, self.SCH), [])

    def test_else_branch_runs_when_the_condition_fails(self):
        self.assertEqual(errs({"t": "a", "x": 1}, self.SCH), [("", "required")])

    def test_if_alone_never_errors(self):
        self.assertEqual(validate(1, {"if": {"type": "string"}}), [])
        self.assertEqual(validate("a", {"if": {"type": "string"}}), [])

    def test_failing_if_does_not_leak_its_errors(self):
        self.assertEqual(validate(1, {"if": {"type": "string"}, "then": False}), [])
        self.assertEqual(errs(1, {"if": {"type": "string"}, "else": False}), [("", "false")])

    def test_then_and_else_without_if_are_ignored(self):
        sch = {"then": False, "else": False}
        check_schema(sch)
        self.assertEqual(validate(1, sch), [])

    def test_malformed_if_then_else(self):
        for key in ("if", "then", "else"):
            with self.subTest(key=key):
                with self.assertRaisesRegex(SchemaError, f"#/{key}: schema must be an object"):
                    check_schema({key: 1})
        with self.assertRaisesRegex(SchemaError, "#/then: unsupported keyword .bogus."):
            check_schema({"if": True, "then": {"bogus": 1}})


class AllOfTests(unittest.TestCase):
    def test_all_of_collects_every_failure(self):
        sch = {"allOf": [{"required": ["a"]}, {"required": ["b"]}]}
        self.assertEqual([e.params["name"] for e in validate({}, sch)], ["a", "b"])

    def test_all_of_passes_when_all_pass_and_keeps_path(self):
        sch = {"properties": {"n": {"allOf": [{"minimum": 1}, {"maximum": 3}]}}}
        self.assertEqual(validate({"n": 2}, sch), [])
        self.assertEqual(errs({"n": 5}, sch), [("/n", "maximum")])

    def test_malformed_all_of(self):
        cases = [
            ({"allOf": {}}, "#/allOf: must be a non-empty list"),
            ({"allOf": []}, "#/allOf: must be a non-empty list"),
            ({"allOf": [1]}, "#/allOf/0: schema must be an object"),
            ({"allOf": [{}, {"type": "text"}]}, "#/allOf/1: unknown type 'text'"),
        ]
        for sch, why in cases:
            with self.subTest(sch=sch):
                with self.assertRaises(SchemaError) as cm:
                    check_schema(sch)
                self.assertIn(why, str(cm.exception))

    def test_cyclic_ref_is_a_schema_error_not_recursion(self):
        sch = {"$defs": {"a": {"allOf": [{"$ref": "#/$defs/a"}]}}, "$ref": "#/$defs/a"}
        with self.assertRaisesRegex(SchemaError, "cyclic reference"):
            validate(1, sch)
        for key in ("if", "then", "else"):
            with self.subTest(key=key):
                sch = {"$defs": {"a": {"if": True, "then": {"$ref": "#/$defs/a"}, "else": {"$ref": "#/$defs/a"}}},
                       "$ref": "#/$defs/a"}
                with self.assertRaisesRegex(SchemaError, "cyclic reference"):
                    validate(1, sch)
        direct = {"$defs": {"a": {"$ref": "#/$defs/a"}}, "allOf": [{"$ref": "#/$defs/a"}]}
        with self.assertRaisesRegex(SchemaError, "cyclic reference"):
            check_schema(direct)

    def test_check_schema_sees_cycles_through_all_of_if_then_else(self):
        cases = [
            {"allOf": [{"$ref": "#"}]},
            {"if": {"$ref": "#"}},
            {"if": True, "then": {"$ref": "#"}},
            {"if": True, "else": {"$ref": "#"}},
            {"$defs": {"a": {"allOf": [{"$ref": "#/$defs/b"}]}, "b": {"allOf": [{"$ref": "#/$defs/a"}]}},
             "properties": {"x": {"$ref": "#/$defs/a"}}},
        ]
        for sch in cases:
            with self.subTest(sch=sch):
                with self.assertRaisesRegex(SchemaError, "cyclic reference"):
                    check_schema(sch)

    def test_recursion_through_all_of_over_finite_data_is_fine(self):
        sch = {"$defs": {"n": {"properties": {"k": {"allOf": [{"$ref": "#/$defs/n"}]}}}}, "$ref": "#/$defs/n"}
        self.assertEqual(validate({"k": {"k": {}}}, sch), [])


class RefTargetTests(unittest.TestCase):
    def test_ref_target_must_be_a_schema(self):
        sch = {"$ref": "#/properties/x/minLength", "properties": {"x": {"minLength": 3}}}
        with self.assertRaisesRegex(SchemaError, "does not point to a schema"):
            validate(1, sch)

    def test_ref_target_is_checked(self):
        with self.assertRaisesRegex(SchemaError, "unknown type 'bogus'"):
            validate(1, {"$ref": "#/const", "const": {"type": "bogus"}})

    def test_ref_that_is_not_hashable_is_a_schema_error(self):
        with self.assertRaisesRegex(SchemaError, "reference must be a string"):
            check_schema({"$ref": {}})
        with self.assertRaisesRegex(SchemaError, "reference must be a string"):
            check_schema({"$defs": {"a": {"$ref": {}}}, "$ref": "#/$defs/a"})

    def test_ref_back_to_an_ancestor_terminates(self):
        sch = {"properties": {"a": {"$ref": "#"}}}
        check_schema(sch)
        self.assertEqual(errs({"a": {"a": {}}}, sch), [])


class SchemaCheckTests(unittest.TestCase):
    def test_every_annotation_is_accepted_and_ignored(self):
        for key in sorted(ANNOTATIONS):
            with self.subTest(key=key):
                sch = {key: "anything", "type": "integer"}
                check_schema(sch)
                self.assertEqual(validate(1, sch), [])
                self.assertEqual(errs("x", sch), [("", "type")])

    def test_unknown_keyword_is_rejected_naming_it(self):
        for key in ("format", "oneOf", "anyOf", "not", "dependencies"):
            with self.subTest(key=key):
                with self.assertRaisesRegex(SchemaError, f"unsupported keyword '{key}'"):
                    check_schema({key: {}})

    def test_unknown_keyword_names_its_path(self):
        with self.assertRaisesRegex(SchemaError, r"#/properties/a/items: unsupported keyword 'format'"):
            check_schema({"properties": {"a": {"items": {"format": "x"}}}})

    def test_validate_checks_the_schema_first(self):
        with self.assertRaisesRegex(SchemaError, "unsupported keyword 'format'"):
            validate("x", {"format": "email"})

    def test_empty_enum_is_rejected(self):
        with self.assertRaisesRegex(SchemaError, "#/enum: must be a non-empty list"):
            check_schema({"enum": []})
        with self.assertRaisesRegex(SchemaError, "#/enum: must be a non-empty list"):
            check_schema({"enum": "ab"})

    def test_invalid_pattern(self):
        with self.assertRaisesRegex(SchemaError, "invalid pattern '\\('"):
            check_schema({"pattern": "("})

    def test_malformed_values_name_their_path(self):
        cases = [
            ({"properties": []}, "#/properties: must be an object"),
            ({"$defs": 1}, r"#/\$defs: must be an object"),
            ({"required": "a"}, "#/required: must be a list of strings"),
            ({"required": [1]}, "#/required: must be a list of strings"),
            ({"minLength": -1}, "#/minLength: must be a non-negative integer"),
            ({"maxItems": True}, "#/maxItems: must be a non-negative integer"),
            ({"minimum": "1"}, "#/minimum: must be a finite number"),
            ({"maximum": float("nan")}, "#/maximum: must be a finite number"),
            ({"items": 5}, "#/items: schema must be an object"),
            ({"type": []}, "#/type: must not be an empty list"),
        ]
        for schema, message in cases:
            with self.subTest(schema=schema):
                with self.assertRaisesRegex(SchemaError, message):
                    check_schema(schema)

    def test_schema_must_be_an_object_or_bool(self):
        with self.assertRaisesRegex(SchemaError, "schema must be an object"):
            check_schema([])

    def test_keyword_sets(self):
        self.assertEqual(len(VALIDATING), 24)
        self.assertFalse(VALIDATING & ANNOTATIONS)


class OrderAndShapeTests(unittest.TestCase):
    SCHEMA = {
        "properties": {"b": {"type": "integer"}, "a": {"type": "integer"}, "c": {"type": "integer"}},
        "additionalProperties": False,
    }

    def test_errors_do_not_depend_on_insertion_order(self):
        one = validate({"c": "x", "a": "x", "b": "x", "z": 1, "y": 1}, self.SCHEMA)
        two = validate({"y": 1, "z": 1, "b": "x", "a": "x", "c": "x"}, self.SCHEMA)
        self.assertEqual(one, two)
        self.assertEqual([e.path for e in one], ["/a", "/b", "/c", "/y", "/z"])

    def test_property_names_errors_are_sorted(self):
        sch = {"propertyNames": {"pattern": "^[a-z]+$"}}
        self.assertEqual(errs({"B": 1, "A": 1}, sch), [("/A", "propertyNames"), ("/B", "propertyNames")])

    def test_many_errors_at_once(self):
        sch = {"type": "object", "required": ["a"],
               "properties": {"n": {"type": "integer", "minimum": 3}}}
        self.assertEqual(errs({"n": 1}, sch), [("", "required"), ("/n", "minimum")])

    def test_root_path_is_empty_and_an_empty_key_is_slash(self):
        self.assertEqual(validate(1, {"type": "string"})[0].path, "")
        self.assertEqual(errs({"": 1}, {"properties": {"": {"type": "string"}}}), [("/", "type")])

    def test_errors_are_sorted_by_path_then_code(self):
        self.assertEqual(errs({}, {"required": ["a"], "minProperties": 1}),
                         [("", "minProperties"), ("", "required")])
        sch = {"propertyNames": {"maxLength": 0}, "properties": {"a": {"type": "integer"}}}
        self.assertEqual(errs({"a": "x", "b": 1}, sch),
                         [("/a", "propertyNames"), ("/a", "type"), ("/b", "propertyNames")])

    def test_property_names_error_keeps_the_real_cause(self):
        got = validate({"ab": 1}, {"propertyNames": {"maxLength": 1}})
        self.assertEqual(got, [ValidationError("/ab", "propertyNames",
                                               {"name": "ab", "reason": "maxLength", "detail": {"limit": 1}})])

    def test_huge_numbers_do_not_overflow(self):
        self.assertEqual(validate(1, {"minimum": 10**400}), [ValidationError("", "minimum", {"limit": 10**400})])
        self.assertEqual(validate(1, {"maximum": -(10**400)}), [ValidationError("", "maximum", {"limit": -(10**400)})])
        with self.assertRaisesRegex(SchemaError, "must be a finite number"):
            check_schema({"minimum": float("inf")})

    def test_every_code_is_listed(self):
        sch = {"type": "object", "required": ["r"], "minProperties": 9, "propertyNames": {"pattern": "^q$"},
               "properties": {"p": {"enum": [1], "const": 2, "pattern": "x", "minLength": 9, "maxLength": 0,
                                    "minimum": 9, "maximum": 0, "items": {}, "type": ["string", "null"]},
                              "f": False, "l": {"minItems": 3, "maxItems": 0}, "t": {"type": "null"}},
               "additionalProperties": False}
        got = validate({"p": "ab", "f": 1, "l": [1], "t": 1, "zz": 1}, sch)
        self.assertTrue({e.code for e in got} <= set(CODES))
        self.assertTrue({"required", "minProperties", "propertyNames", "false", "minItems", "type",
                         "additionalProperties", "pattern", "minLength"} <= {e.code for e in got})
        more = validate({"a": 1, "b": 2}, {"maxProperties": 1, "dependentRequired": {"a": ["z"]}})
        self.assertEqual({e.code for e in more}, {"maxProperties", "dependentRequired"})
        self.assertTrue({e.code for e in more} <= set(CODES))


if __name__ == "__main__":
    unittest.main()
