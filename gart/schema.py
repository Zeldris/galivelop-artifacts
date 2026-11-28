"""Strict validator for the JSON Schema subset of gart (stdlib only).

Ported from gvoice (`gvoice/schema.py` at galivelop-voice-generator@1990d92), itself a copy of gimg. Dropped:
- `$ref` to sibling files, `load_schema`, the schemas folder and its cache: they belong to the `Registry` (gart-H4).
- i18n and `format_error`: messages come with the catalog (gart-H6); `code` and `params` are the stable contract.
Added from opportunity_intel: `enum` must be a non-empty list, and errors come in a stable order (by path, then code).
Kept from the copies (gart-H3, Q-18): `maxProperties`, `dependentRequired` (gimg) and `allOf`, `if`/`then`/`else`
(gvoice). `then` or `else` without `if` is a `SchemaError` (fail closed). The errors of `if` are never reported.
Where the copies disagree on a rule the strictest wins (`gart.diff/0`): `$ref: "#"` is rejected, and path order
compares array indices as numbers (`/2` before `/10`).

Paths are JSON Pointers (RFC 6901): the root is `""`, and a root key `""` is `/`.
Errors come sorted by `(path, code)`; the path compares token by token, array indices numerically.
"""

from __future__ import annotations

import functools
import json
import math
import re
from typing import Any, Callable, NamedTuple

from gart.kind_id import KindId

ANNOTATIONS = frozenset(["$schema", "$id", "title", "description", "default", "examples", "$comment"])
VALIDATING = frozenset(
    [
        "type", "properties", "required", "additionalProperties", "propertyNames",
        "minProperties", "maxProperties", "dependentRequired", "allOf", "if", "then", "else",
        "items", "minItems", "maxItems", "enum", "const", "pattern",
        "minLength", "maxLength", "minimum", "maximum", "$ref", "$defs",
    ]
)
# Every `code` a ValidationError can carry (the keys the catalog will translate).
CODES = (
    "required", "type", "enum", "const", "pattern", "minimum", "maximum",
    "minLength", "maxLength", "minItems", "maxItems", "minProperties", "maxProperties",
    "dependentRequired", "additionalProperties", "propertyNames", "false",
)
TYPES = ("object", "array", "string", "integer", "number", "boolean", "null")


class SchemaError(Exception):
    """The schema itself is not valid (or not supported)."""


class ValidationError(NamedTuple):
    path: str
    code: str
    params: dict


def _ecma_pattern(pattern: str) -> str:
    """Translate an ECMA-262 pattern to Python: `$` only matches at the very end."""
    out = []
    in_class = False
    i = 0
    while i < len(pattern):
        ch = pattern[i]
        if ch == "\\":
            out.append(pattern[i:i + 2])
            i += 2
            continue
        if in_class:
            in_class = ch != "]"
        elif ch == "[":
            in_class = True
        elif ch == "$":
            ch = r"\Z"
        out.append(ch)
        i += 1
    return "".join(out)


@functools.lru_cache(maxsize=None)
def _compile(pattern: str) -> re.Pattern:
    return re.compile(_ecma_pattern(pattern), re.ASCII)


def _is_int(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def _is_number(value: Any) -> bool:
    # math.isfinite(int) would overflow on huge ints, so only floats are asked.
    return _is_int(value) or (isinstance(value, float) and math.isfinite(value))


# `resolver(base, target) -> (document_root, document_base)`: `target` is a kind id or a sibling file name, `base`
# the folder of the referring document. It raises `SchemaError("unresolved reference ...")` for what it cannot find.
Resolver = Callable[[Any, str], tuple]


class Doc(NamedTuple):
    """The document a schema node lives in: its root (where `#/pointer` starts), its base and the resolver."""

    root: Any
    base: Any
    resolver: Resolver | None


def _check(schema: Any, doc: Doc, where: str, seen: set) -> None:
    if isinstance(schema, bool):
        return
    if not isinstance(schema, dict):
        raise SchemaError(f"{where}: schema must be an object")
    if id(schema) in seen:  # already checked (or being checked, through a reference)
        return
    seen.add(id(schema))
    for key, value in schema.items():
        if key in ANNOTATIONS:
            continue
        if key not in VALIDATING:
            raise SchemaError(f"{where}: unsupported keyword {key!r}")
        here = f"{where}/{key}"
        if key in ("properties", "$defs"):
            if not isinstance(value, dict):
                raise SchemaError(f"{here}: must be an object")
            for name, sub in value.items():
                _check(sub, doc, f"{here}/{name}", seen)
        elif key in ("items", "propertyNames", "if"):
            _check(value, doc, here, seen)
        elif key in ("then", "else"):
            if "if" not in schema:
                raise SchemaError(f"{here}: {key!r} requires 'if'")
            _check(value, doc, here, seen)
        elif key == "allOf":
            if not isinstance(value, list) or not value:
                raise SchemaError(f"{here}: must be a non-empty list")
            for i, sub in enumerate(value):
                _check(sub, doc, f"{here}/{i}", seen)
        elif key == "dependentRequired":
            if not isinstance(value, dict) or not all(
                isinstance(names, list) and all(isinstance(n, str) for n in names) for names in value.values()
            ):
                raise SchemaError(f"{here}: must be an object of lists of strings")
        elif key == "additionalProperties":
            _check(value, doc, here, seen)
        elif key == "enum":
            if not isinstance(value, list) or not value:
                raise SchemaError(f"{here}: must be a non-empty list")
        elif key == "required":
            if not isinstance(value, list) or not all(isinstance(n, str) for n in value):
                raise SchemaError(f"{here}: must be a list of strings")
        elif key == "type":
            names = value if isinstance(value, list) else [value]
            if not names:
                raise SchemaError(f"{here}: must not be an empty list")
            for name in names:
                if not isinstance(name, str) or name not in TYPES:
                    raise SchemaError(f"{where}: unknown type {name!r}")
        elif key == "pattern":
            try:
                if not isinstance(value, str):
                    raise TypeError("pattern must be a string")
                _compile(value)
            except (re.error, TypeError) as exc:
                raise SchemaError(f"{where}: invalid pattern {value!r}: {exc}") from exc
        elif key in ("minLength", "maxLength", "minItems", "maxItems", "minProperties", "maxProperties"):
            if not _is_int(value) or value < 0:
                raise SchemaError(f"{here}: must be a non-negative integer")
        elif key in ("minimum", "maximum"):
            if not _is_number(value):
                raise SchemaError(f"{here}: must be a finite number")
        elif key == "$ref":
            _check_ref(doc, value, where, seen)
    try:
        _walk_same_instance(schema, doc, frozenset(), set())
    except SchemaError as exc:
        raise SchemaError(f"{where}: {exc}") from None


def _walk_same_instance(schema: Any, doc: Doc, chain: frozenset, done: set) -> None:
    """Follow what `_validate` follows without going down the instance (`$ref`, `allOf`, `if`, `then`, `else`)."""
    if not isinstance(schema, dict):
        return
    key = (id(schema), chain)
    if key in done:
        return
    done.add(key)
    ref = schema.get("$ref")
    if "$ref" in schema:
        # Keyed by document too: the same `#/$defs/x` in two documents is not a cycle.
        key = (id(doc.root), ref)
        if key in chain:
            raise SchemaError(f"cyclic reference {ref!r}")
        node, target = _resolve(doc, ref)
        _walk_same_instance(node, target, chain | {key}, done)
    for sub in schema.get("allOf", []):
        _walk_same_instance(sub, doc, chain, done)
    for name in ("if", "then", "else"):
        if name in schema:
            _walk_same_instance(schema[name], doc, chain, done)


def _check_ref(doc: Doc, ref: Any, where: str, seen_nodes: set) -> None:
    """The reference resolves to a valid schema and its chain of bare references is not a cycle."""
    try:
        node, target = _resolve(doc, ref)
        seen = {(id(doc.root), ref)}
        while True:
            if not isinstance(node, (dict, bool)):
                raise SchemaError(f"reference {ref!r} does not point to a schema")
            _check(node, target, ref, seen_nodes)
            if not (isinstance(node, dict) and "$ref" in node):
                break
            nxt = node["$ref"]
            if not isinstance(nxt, str):
                raise SchemaError("reference must be a string")
            key = (id(target.root), nxt)
            if key in seen:
                raise SchemaError(f"cyclic reference {ref!r}")
            seen.add(key)
            node, target = _resolve(target, nxt)
    except SchemaError as exc:
        raise SchemaError(f"{where}: {exc}") from None


def check_schema(schema: Any, resolver: Resolver | None = None, base: Any = None) -> None:
    """Raise `SchemaError` (naming the path and the cause) unless `schema` is in the supported subset.

    Without a `resolver` only local `#/...` references are accepted. With one, `$ref` may also name a kind id or a
    sibling document of `base` (see `Doc`).
    """
    _check(schema, Doc(schema, base, resolver), "#", set())


def _is_type(value: Any, name: str) -> bool:
    if name == "object":
        return isinstance(value, dict)
    if name == "array":
        return isinstance(value, list)
    if name == "string":
        return isinstance(value, str)
    if name == "boolean":
        return isinstance(value, bool)
    if name == "null":
        return value is None
    if isinstance(value, bool):
        return False
    if isinstance(value, int):
        return True
    if not isinstance(value, float) or not math.isfinite(value):
        return False
    return name == "number" or value.is_integer()


def _type_name(value: Any) -> str:
    """The JSON type of `value` for the `actual` param of a type error; `not-json` for inf, NaN or a non-JSON object."""
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "boolean"
    if isinstance(value, int):
        return "integer"
    if isinstance(value, float) and math.isfinite(value):
        return "integer" if value.is_integer() else "number"
    for name, kind in (("string", str), ("array", list), ("object", dict)):
        if isinstance(value, kind):
            return name
    return "not-json"


def _same(a: Any, b: Any) -> bool:
    """JSON equality: booleans are not numbers, 1 equals 1.0, deep for containers."""
    if isinstance(a, bool) or isinstance(b, bool):
        return isinstance(a, bool) and isinstance(b, bool) and a == b
    if isinstance(a, (int, float)) and isinstance(b, (int, float)):
        return a == b
    if isinstance(a, list) and isinstance(b, list):
        return len(a) == len(b) and all(_same(x, y) for x, y in zip(a, b))
    if isinstance(a, dict) and isinstance(b, dict):
        return set(a) == set(b) and all(_same(a[k], b[k]) for k in a)
    return type(a) is type(b) and a == b


_SIBLING = re.compile(r"[a-z0-9][a-z0-9_-]*\.schema\.json")


def _target(doc: Doc, name: str, ref: str) -> Doc:
    """The document a `$ref` with a part before `#` points to: a kind id or a sibling file of the same folder."""
    if doc.resolver is None:
        raise SchemaError(f"reference {ref!r} is not local: only '#/...' is supported")
    if ":" in name or "\\" in name or ".." in name:
        raise SchemaError(f"reference {ref!r}: remote or unsafe reference ({name!r} has ':', '\\' or '..')")
    if KindId.is_valid(name) or _SIBLING.fullmatch(name):
        root, base = doc.resolver(doc.base, name)
        return Doc(root, base, doc.resolver)
    raise SchemaError(f"reference {ref!r}: {name!r} is neither a kind id nor a sibling file name")


def _resolve(doc: Doc, ref: Any) -> tuple[Any, Doc]:
    """The node a `$ref` points to and the document it lives in (the node's `#/pointer` is relative to it)."""
    if not isinstance(ref, str):
        raise SchemaError("reference must be a string")
    name, hashed, frag = ref.partition("#")
    if name:
        doc = _target(doc, name, ref)
    elif not hashed:  # the empty text
        raise SchemaError(f"reference {ref!r} is not local: only '#/...' is supported")
    elif ref == "#":  # gdev, gimg and oi reject the whole root: strictest wins (gart.diff/0, B1)
        raise SchemaError("reference '#' is not supported: only '#/...' is supported")
    if frag and not frag.startswith("/"):
        raise SchemaError(f"reference {ref!r}: fragment must be a JSON pointer")
    node = doc.root
    for part in frag[1:].split("/") if frag else []:
        part = part.replace("~1", "/").replace("~0", "~")
        if not isinstance(node, dict) or part not in node:
            raise SchemaError(f"unresolved reference {ref!r}")
        node = node[part]
    return node, doc


def _pointer(path: tuple, token: Any) -> tuple:
    return path + (str(token),)


def _render(path: tuple) -> str:
    # RFC 6901: the root is the empty pointer; a root key "" is "/".
    return "".join("/" + t.replace("~", "~0").replace("/", "~1") for t in path)


def _validate(value: Any, schema: Any, doc: Doc, path: tuple, out: list, seen: frozenset = frozenset()) -> None:
    if schema is True:
        return
    if schema is False:
        out.append(ValidationError(_render(path), "false", {}))
        return

    def add(code: str, **params: Any) -> None:
        out.append(ValidationError(_render(path), code, params))

    if "$ref" in schema:
        ref = schema["$ref"]
        key = (id(doc.root), ref)
        if key in seen:
            raise SchemaError(f"cyclic reference {ref!r}")
        node, target = _resolve(doc, ref)
        _validate(value, node, target, path, out, seen | {key})
    for sub in schema.get("allOf", []):
        _validate(value, sub, doc, path, out, seen)
    if "if" in schema:
        probe: list = []
        _validate(value, schema["if"], doc, path, probe, seen)
        branch = schema.get("else" if probe else "then")
        if branch is not None:
            _validate(value, branch, doc, path, out, seen)
    if "type" in schema:
        names = schema["type"] if isinstance(schema["type"], list) else [schema["type"]]
        if not any(_is_type(value, n) for n in names):
            add("type", expected="/".join(names), actual=_type_name(value))
            return
    if "enum" in schema and not any(_same(value, v) for v in schema["enum"]):
        add("enum", allowed=", ".join(json.dumps(v) for v in schema["enum"]))
    if "const" in schema and not _same(value, schema["const"]):
        add("const", expected=json.dumps(schema["const"]))

    if isinstance(value, str):
        if "minLength" in schema and len(value) < schema["minLength"]:
            add("minLength", limit=schema["minLength"])
        if "maxLength" in schema and len(value) > schema["maxLength"]:
            add("maxLength", limit=schema["maxLength"])
        if "pattern" in schema and not _compile(schema["pattern"]).search(value):
            add("pattern", pattern=schema["pattern"])

    if isinstance(value, (int, float)) and not isinstance(value, bool):
        if "minimum" in schema and value < schema["minimum"]:
            add("minimum", limit=schema["minimum"])
        if "maximum" in schema and value > schema["maximum"]:
            add("maximum", limit=schema["maximum"])

    if isinstance(value, list):
        if "minItems" in schema and len(value) < schema["minItems"]:
            add("minItems", limit=schema["minItems"])
        if "maxItems" in schema and len(value) > schema["maxItems"]:
            add("maxItems", limit=schema["maxItems"])
        if "items" in schema:
            for i, item in enumerate(value):
                _validate(item, schema["items"], doc, _pointer(path, i), out)

    if isinstance(value, dict):
        props = schema.get("properties", {})
        for name in schema.get("required", []):
            if name not in value:
                add("required", name=name)
        if "minProperties" in schema and len(value) < schema["minProperties"]:
            add("minProperties", limit=schema["minProperties"])
        if "maxProperties" in schema and len(value) > schema["maxProperties"]:
            add("maxProperties", limit=schema["maxProperties"])
        for trigger, needed in schema.get("dependentRequired", {}).items():
            if trigger in value:
                for name in needed:
                    if name not in value:
                        add("dependentRequired", name=name, trigger=trigger)
        # Sorted by name, so the error list does not depend on insertion order.
        keys = sorted(value)
        if "propertyNames" in schema:
            for key in keys:
                sub: list = []
                _validate(key, schema["propertyNames"], doc, path, sub)
                if sub:
                    out.append(
                        ValidationError(
                            _render(_pointer(path, key)), "propertyNames",
                            {"name": key, "reason": sub[0].code, "detail": sub[0].params},
                        )
                    )
        extra = schema.get("additionalProperties", True)
        for key in keys:
            if key in props:
                _validate(value[key], props[key], doc, _pointer(path, key), out)
            elif extra is False:
                out.append(ValidationError(_render(_pointer(path, key)), "additionalProperties", {"name": key}))
            elif extra is not True:
                _validate(value[key], extra, doc, _pointer(path, key), out)


def _token_key(t: str) -> tuple:
    """Digits-only tokens compare as numbers without `int()` (which fails on very long digit strings)."""
    if t.isascii() and t.isdigit():
        s = t.lstrip("0") or "0"
        return (0, len(s), s, t)
    return (1, 0, t, t)


def _sort_key(error: ValidationError) -> tuple:
    """Order by path, comparing array indices as numbers (`/2` before `/10`), then by code."""
    tokens = [] if error.path == "" else error.path[1:].split("/")
    return (
        tuple(_token_key(t) for t in tokens),
        error.code,
    )


def validate(instance: Any, schema: Any, resolver: Resolver | None = None, base: Any = None) -> list[ValidationError]:
    """Every way `instance` breaks `schema`, in a stable order (by path, then code); `[]` when it conforms.

    Raises `SchemaError` if the schema itself is invalid.
    """
    check_schema(schema, resolver, base)
    errors: list[ValidationError] = []
    _validate(instance, schema, Doc(schema, base, resolver), (), errors)
    errors.sort(key=_sort_key)  # stable: DDD section 5 invariant 7
    return errors
