"""Differential battery: copy vs gart on hand-picked edge cases. usage: python3 -I probe.py <repo> <pkg>"""
import sys, importlib, math, json
repo, pkg = sys.argv[1:3]
sys.path[:0] = [repo, "/home/user/galivelop-artifacts"]
from gart import schema as G
O = importlib.import_module(pkg + ".schema")
oi = pkg == "opportunity_intel"
inf, nan = float("inf"), float("nan")
C = [
 ("unicode digit vs \\d", "٣", {"pattern": r"^\d$"}),
 ("unicode \\w", "é", {"pattern": r"^\w$"}),
 ("$ before final newline", "ab\n", {"pattern": "^[a-z]+$"}),
 ("pattern unanchored", "xxabxx", {"pattern": "ab"}),
 ("case-insens unicode", "É", {"pattern": "[a-z]", }),
 ("astral minLength", "😀", {"minLength": 2}),
 ("astral maxLength", "😀", {"maxLength": 1}),
 ("bool is not int", True, {"type": "integer"}),
 ("1.0 is integer", 1.0, {"type": "integer"}),
 ("1.5 integer", 1.5, {"type": "integer"}),
 ("inf is number?", inf, {"type": "number"}),
 ("nan is number?", nan, {"type": "number"}),
 ("inf integer", inf, {"type": "integer"}),
 ("inf maximum", inf, {"maximum": 10}),
 ("nan minimum", nan, {"minimum": 0}),
 ("big int number", 10**400, {"type": "number"}),
 ("big int minimum", 10**400, {"maximum": 5}),
 ("bool vs minimum", True, {"minimum": 5}),
 ("bool enum 1", True, {"enum": [1]}),
 ("1 enum true", 1, {"enum": [True]}),
 ("1.0 enum 1", 1.0, {"enum": [1]}),
 ("nested enum list [1] vs [true]", [1], {"enum": [[True]]}),
 ("enum dict", {"a": 1}, {"enum": [{"a": 1.0}]}),
 ("type list", None, {"type": ["string", "null"]}),
 ("type mismatch stops other kw", 5, {"type": "string", "minLength": 3, "enum": ["a"]}),
 ("no type, str+minimum", "a", {"minimum": 3}),
 ("no type, minItems on str", "a", {"minItems": 3}),
 ("minLength on list", [1], {"minLength": 3}),
 ("required on list", [1], {"required": ["a"]}),
 ("required missing", {}, {"required": ["a"]}),
 ("properties on non-dict", [1], {"properties": {"a": {"type": "string"}}}),
 ("addProps false", {"z": 1}, {"additionalProperties": False}),
 ("addProps schema", {"z": "s"}, {"additionalProperties": {"type": "integer"}}),
 ("addProps True", {"z": 1}, {"additionalProperties": True}),
 ("items on dict", {"a": 1}, {"items": {"type": "string"}}),
 ("items bool false", [1], {"items": False}),
 ("properties bool false", {"a": 1}, {"properties": {"a": False}}),
 ("properties bool true", {"a": 1}, {"properties": {"a": True}}),
 ("const", 1, {"const": 2}),
 ("const bool", True, {"const": 1}),
 ("minProperties", {}, {"minProperties": 1}),
 ("propertyNames", {"A": 1}, {"propertyNames": {"pattern": "^[a-z]+$"}}),
 ("maxProperties", {"a": 1, "b": 2}, {"maxProperties": 1}),
 ("$ref local", 1, {"$defs": {"s": {"type": "string"}}, "$ref": "#/$defs/s"}),
 ("$ref + siblings", 1, {"$defs": {"s": {"type": "string"}}, "$ref": "#/$defs/s", "minimum": 5}),
 ("$ref in properties", {"a": 1}, {"$defs": {"s": {"type": "string"}}, "properties": {"a": {"$ref": "#/$defs/s"}}}),
 ("$defs only", 1, {"$defs": {"s": {"type": "string"}}}),
 ("true schema", 1, True),
 ("false schema", 1, False),
 ("non-JSON value (set)", {1}, {"type": "array"}),
 ("tuple as array", (1,), {"type": "array"}),
 ("int-key dict", {1: "a"}, {"type": "object", "properties": {"1": {"type": "string"}}}),
 ("unknown keyword format", "x", {"format": "email"}),
 ("unknown keyword oneOf", 1, {"oneOf": []}),
 ("unknown keyword uniqueItems", [1, 1], {"uniqueItems": True}),
 ("unknown keyword not", 1, {"not": {}}),
 ("annotation default/examples", 1, {"default": 1, "examples": [1], "title": "t"}),
 ("annotation $comment", 1, {"$comment": "c"}),
 ("empty enum", 1, {"enum": []}),
 ("enum non-list", 1, {"enum": "a"}),
 ("type empty list", 1, {"type": []}),
 ("type unknown", 1, {"type": "float"}),
 ("type non-str in list", 1, {"type": [1]}),
 ("minLength negative", "a", {"minLength": -1}),
 ("minLength float", "a", {"minLength": 1.0}),
 ("minLength bool", "a", {"minLength": True}),
 ("minimum nan schema", 1, {"minimum": nan}),
 ("minimum bool schema", 1, {"minimum": True}),
 ("minimum str schema", 1, {"minimum": "0"}),
 ("required non-str", {}, {"required": [1]}),
 ("pattern invalid", "a", {"pattern": "("}),
 ("pattern non-str", "a", {"pattern": 1}),
 ("properties list", {}, {"properties": []}),
 ("schema not dict", 1, []),
 ("cyclic $ref", 1, {"$defs": {"a": {"$ref": "#/$defs/b"}, "b": {"$ref": "#/$defs/a"}}, "$ref": "#/$defs/a"}),
 ("dangling $ref", 1, {"$ref": "#/$defs/x"}),
 ("remote $ref", 1, {"$ref": "http://x/y"}),
 ("additionalProperties bad", {}, {"additionalProperties": 1}),
 ("items bad", [], {"items": 1}),
 ("deep recursion", [[[[[1]]]]], {"items": {"items": {"items": {"items": {"items": {"type": "string"}}}}}}),
 ("error order insertion", {"b": 1, "a": 1}, {"properties": {"a": {"type": "string"}, "b": {"type": "string"}}}),
 ("many required order", {}, {"required": ["z", "a"]}),
 ("both type and nested errors", {"a": 1, "b": 2}, {"additionalProperties": False, "required": ["q"], "properties": {"a": {"type": "string"}}}),
 ("dict key with slash", {"a/b": 1}, {"additionalProperties": False}),
 ("empty-string key", {"": 1}, {"properties": {"": {"type": "string"}}}),
 ("maxLength+pattern both", "abcd", {"maxLength": 2, "pattern": "^x"}),
 ("minimum float vs int", 5, {"minimum": 5.0}),
 ("number string keys unicode", {"é": 1}, {"propertyNames": {"pattern": "^\\w+$"}}),
]
def run(mod, inst, sch):
    try:
        errs = mod.validate(inst, sch)
    except RecursionError: return ("RecursionError",)
    except Exception as e: return ("EXC", type(e).__name__)
    return tuple(sorted(getattr(e, "code", None) or e.keyword for e in errs))
rows = []
for name, inst, sch in C:
    a, b = run(O, inst, sch), run(G, inst, sch)
    if a == b: continue
    rank = "gart-LOOSER" if (len(a) > 0 and a[0] != "EXC" and (b == () or (b[0] != "EXC" and len(b) < len(a)))) else \
           "copy-accepts/gart-rejects-or-raises" if (a == () or a[0] != "EXC") and (b and b[0] == "EXC") else \
           "copy-raises/gart-validates" if a and a[0] == "EXC" else "gart-stricter/differs"
    rows.append(f"{rank}\t{name}\tcopy={a}\tgart={b}")
print("\n".join(rows) or "no difference")
