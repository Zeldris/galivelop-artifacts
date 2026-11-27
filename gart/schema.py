"""Strict validator for the JSON Schema subset of gart (stdlib only).

Ported from gvoice (`gvoice/schema.py` at galivelop-voice-generator@1990d92), itself a copy of gimg. Dropped:
- `$ref` to sibling files, `load_schema`, the schemas folder and its cache: they belong to the `Registry` (gart-H4).
- i18n and `format_error`: messages come with the catalog (gart-H6); `code` and `params` are the stable contract.
Added from opportunity_intel: `enum` must be a non-empty list, and errors come in a stable order (by path, then code).
Added from gimg (gart-H3): `maxProperties` and `dependentRequired` (code `dependentRequired`, params `name` and `trigger`).
Added from gvoice (gart-H3): `allOf` and `if`/`then`/`else`. `if` never yields an error itself, only the failures of the
branch that applies; `then`/`else` without `if` are checked as schemas and ignored (as in gvoice). The `type` error
carries `expected` and `actual` (the JSON type name of the instance).

Paths are JSON Pointers (RFC 6901): the root is `""`, and a root key `""` is `/`.
Errors come sorted by `(path, code)`.
"""

from __future__ import annotations

import functools
import json
import math
import re
from typing import Any, NamedTuple

ANNOTATIONS = frozenset(["$schema", "$id", "title", "description", "default", "examples", "$comment"])
VALIDATING = frozenset(
    [
        "type", "properties", "required", "additionalProperties", "propertyNames",
        "minProperties", "maxProperties", "dependentRequired", "allOf", "if", "then", "else", "items", "minItems", "maxItems", "enum", "const", "pattern",
        "minLength", "maxLength", "minimum", "maximum", "$ref", "$defs",
    ]
)
# Every `code` a ValidationError can carry (the keys the catalog will translate).
CODES = (
    "required", "type", "enum", "const", "pattern", "minimum", "maximum",
    "minLength", "maxLength", "minItems", "maxItems", "minProperties",
    "maxProperties", "dependentRequired", "additionalProperties", "propertyNames", "false",
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


def _check(schema: Any, root: Any, where: str, seen: set) -> None:
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
                _check(sub, root, f"{here}/{name}", seen)
        elif key in ("items", "propertyNames", "if", "then", "else"):
            _check(value, root, here, seen)
        elif key == "allOf":
            if not isinstance(value, list) or not value:
                raise SchemaError(f"{here}: must be a non-empty list")
            for i, sub in enumerate(value):
                _check(sub, root, f"{here}/{i}", seen)
        elif key == "dependentRequired":
            if not isinstance(value, dict):
                raise SchemaError(f"{here}: must be an object")
            for name, needed in value.items():
                if not isinstance(needed, list) or not all(isinstance(n, str) for n in needed):
                    raise SchemaError(f"{here}/{name}: must be a list of strings")
                if len(set(needed)) != len(needed):
                    raise SchemaError(f"{here}/{name}: items must be unique")
        elif key == "additionalProperties":
            _check(value, root, here, seen)
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
            _check_ref(root, value, where, seen)


def _check_ref(root: Any, ref: Any, where: str, seen_nodes: set) -> None:
    """The reference resolves to a valid schema and its chain of bare references is not a cycle."""
    try:
        node = _resolve(root, ref)
        seen = {ref}
        while True:
            if not isinstance(node, (dict, bool)):
                raise SchemaError(f"reference {ref!r} does not point to a schema")
            _check(node, root, ref, seen_nodes)
            if not (isinstance(node, dict) and "$ref" in node):
                break
            nxt = node["$ref"]
            if not isinstance(nxt, str):
                raise SchemaError("reference must be a string")
            if nxt in seen:
                raise SchemaError(f"cyclic reference {ref!r}")
            seen.add(nxt)
            node = _resolve(root, nxt)
    except SchemaError as exc:
        raise SchemaError(f"{where}: {exc}") from None


def check_schema(schema: Any) -> None:
    """Raise `SchemaError` (naming the path and the cause) unless `schema` is in the supported subset."""
    _check(schema, schema, "#", set())
    _check_cycles(schema)


def _check_cycles(root: Any) -> None:
    """No schema reaches itself through edges that consume no instance: `$ref`, `allOf`, `if`, `then`, `else`."""
    nodes: dict = {}
    todo = [root]
    while todo:  # every schema node, however it is reached
        node = todo.pop()
        if isinstance(node, dict) and id(node) not in nodes:
            nodes[id(node)] = node
            todo.extend(_same_instance_edges(node, root))
            todo.extend(_applicators(node))
    done: set = set()
    for start in nodes.values():
        if id(start) in done:
            continue
        active = {id(start)}
        stack = [(start, iter(_same_instance_edges(start, root)))]
        while stack:
            node, children = stack[-1]
            child = next(children, None)
            if child is None:
                stack.pop()
                active.discard(id(node))
                done.add(id(node))
            elif id(child) in active:
                raise SchemaError("cyclic reference: a schema reaches itself without consuming the instance")
            elif id(child) not in done:
                active.add(id(child))
                stack.append((child, iter(_same_instance_edges(child, root))))


def _same_instance_edges(node: dict, root: Any) -> list:
    edges = []
    if "$ref" in node:
        target = _resolve(root, node["$ref"])
        if isinstance(target, dict):
            edges.append(target)
    for sub in node.get("allOf", []):
        if isinstance(sub, dict):
            edges.append(sub)
    for key in ("if", "then", "else"):
        if isinstance(node.get(key), dict):
            edges.append(node[key])
    return edges


def _applicators(node: Any) -> list:
    """Direct subschemas reached by keywords that do consume the instance (or are only definitions)."""
    if not isinstance(node, dict):
        return []
    subs = []
    for key in ("properties", "$defs"):
        subs.extend(v for v in node.get(key, {}).values() if isinstance(v, dict))
    for key in ("items", "propertyNames", "additionalProperties"):
        if isinstance(node.get(key), dict):
            subs.append(node[key])
    return subs


def _json_type(value: Any) -> str:
    """The JSON type name of an instance (whole numbers, 1.0 included, are `integer`)."""
    if isinstance(value, bool):
        return "boolean"
    if value is None:
        return "null"
    if isinstance(value, int):
        return "integer"
    if isinstance(value, float):
        return "integer" if value.is_integer() else "number"  # inf and nan are not whole: "number"
    if isinstance(value, str):
        return "string"
    if isinstance(value, list):
        return "array"
    return "object"


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


def _resolve(root: Any, ref: Any) -> Any:
    """The node a local `#/pointer` reference points to."""
    if not isinstance(ref, str):
        raise SchemaError("reference must be a string")
    if not ref.startswith("#"):
        raise SchemaError(f"reference {ref!r} is not local: only '#/...' is supported")
    frag = ref[1:]
    if frag and not frag.startswith("/"):
        raise SchemaError(f"reference {ref!r}: fragment must be a JSON pointer")
    node = root
    for part in frag[1:].split("/") if frag else []:
        part = part.replace("~1", "/").replace("~0", "~")
        if not isinstance(node, dict) or part not in node:
            raise SchemaError(f"unresolved reference {ref!r}")
        node = node[part]
    return node


def _pointer(path: tuple, token: Any) -> tuple:
    return path + (str(token),)


def _render(path: tuple) -> str:
    # RFC 6901: the root is the empty pointer; a root key "" is "/".
    return "".join("/" + t.replace("~", "~0").replace("/", "~1") for t in path)


def _validate(value: Any, schema: Any, root: Any, path: tuple, out: list, seen: frozenset = frozenset()) -> None:
    if schema is True:
        return
    if schema is False:
        out.append(ValidationError(_render(path), "false", {}))
        return

    def add(code: str, **params: Any) -> None:
        out.append(ValidationError(_render(path), code, params))

    if "$ref" in schema:
        ref = schema["$ref"]
        if ref in seen:
            raise SchemaError(f"cyclic reference {ref!r}")
        _validate(value, _resolve(root, ref), root, path, out, seen | {ref})
    for sub in schema.get("allOf", []):
        _validate(value, sub, root, path, out, seen)
    if "if" in schema:
        probe: list = []
        _validate(value, schema["if"], root, path, probe, seen)
        branch = schema.get("else" if probe else "then")
        if branch is not None:
            _validate(value, branch, root, path, out, seen)
    if "type" in schema:
        names = schema["type"] if isinstance(schema["type"], list) else [schema["type"]]
        if not any(_is_type(value, n) for n in names):
            add("type", expected="/".join(names), actual=_json_type(value))
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
                _validate(item, schema["items"], root, _pointer(path, i), out)

    if isinstance(value, dict):
        props = schema.get("properties", {})
        for name in schema.get("required", []):
            if name not in value:
                add("required", name=name)
        if "minProperties" in schema and len(value) < schema["minProperties"]:
            add("minProperties", limit=schema["minProperties"])
        if "maxProperties" in schema and len(value) > schema["maxProperties"]:
            add("maxProperties", limit=schema["maxProperties"])
        for name, needed in schema.get("dependentRequired", {}).items():
            if name in value:
                for other in needed:
                    if other not in value:
                        add("dependentRequired", name=other, trigger=name)
        # Sorted by name, so the error list does not depend on insertion order.
        keys = sorted(value)
        if "propertyNames" in schema:
            for key in keys:
                sub: list = []
                _validate(key, schema["propertyNames"], root, path, sub)
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
                _validate(value[key], props[key], root, _pointer(path, key), out)
            elif extra is False:
                out.append(ValidationError(_render(_pointer(path, key)), "additionalProperties", {"name": key}))
            elif extra is not True:
                _validate(value[key], extra, root, _pointer(path, key), out)


def validate(instance: Any, schema: Any) -> list[ValidationError]:
    """Every way `instance` breaks `schema`, in a stable order (by path, then code); `[]` when it conforms.

    Raises `SchemaError` if the schema itself is invalid.
    """
    check_schema(schema)
    errors: list[ValidationError] = []
    _validate(instance, schema, schema, (), errors)
    errors.sort(key=lambda e: (e.path, e.code))  # stable: DDD section 5 invariant 7
    return errors
