"""`Registry`: local schema folders, `$ref` between schemas and fingerprints (DDD section 4, invariants 2, 6, 7, 12).

A schema folder holds:
- `<ns>.<name>/<n>.json`: the schema of kind `<ns>.<name>/<n>`; its `title` is the kind id.
- `<x>.schema.json` (directly in the folder): a sibling document without kind id, reachable by `$ref`.
- `fingerprints.json`: `{kind: "sha256:<hex>"}` for the stable kinds (version >= 1) of the folder.
Any other `.json` file is an error (fail closed); other files are ignored. No network: `$ref` never leaves the folders.
"""

from __future__ import annotations

import copy
import hashlib
import json
import os
import re
from typing import Any

from gart.canon import CanonError, canonical_bytes, loads_strict
from gart.kind_id import KindId, KindIdError
from gart.schema import SchemaError, ValidationError, check_schema, validate

FINGERPRINTS = "fingerprints.json"
SIBLING = re.compile(r"[a-z0-9][a-z0-9_-]*\.schema\.json")
FINGERPRINT = re.compile(r"sha256:[0-9a-f]{64}")
# The codes `Registry.validate` adds to those of `gart.schema.CODES`.
CODES = ("kind_invalid", "kind_unknown")
_HERE = os.path.dirname(os.path.abspath(__file__))
OWN_SCHEMAS = os.path.join(_HERE, "schemas")
NAMESPACES = os.path.join(_HERE, "namespaces.json")


def fingerprint(schema: Any) -> str:
    """`sha256:<hex>` of the canonical bytes of `schema` (`meta` is not stripped: it is part of the schema)."""
    return "sha256:" + hashlib.sha256(canonical_bytes(schema)).hexdigest()


def namespaces() -> dict:
    """The table of `gart/namespaces.json`: `{namespace: {"repo": name or None}}`."""
    with open(NAMESPACES, encoding="utf-8") as handle:
        return loads_strict(handle.read())


def _read_json(path: str, label: str) -> Any:
    try:
        with open(path, encoding="utf-8") as handle:
            return loads_strict(handle.read())
    except (OSError, UnicodeDecodeError, CanonError) as exc:
        raise SchemaError(f"{label}: cannot read as strict JSON: {exc}") from exc


def _scan(folder: str) -> tuple[dict, dict, dict | None]:
    """Read a schema folder: `(kinds, siblings, fingerprints)`, each file checked for its name and title."""
    if not os.path.isdir(folder):
        raise SchemaError(f"{folder}: not a folder")
    kinds: dict[str, Any] = {}
    siblings: dict[str, Any] = {}
    pins: dict | None = None
    for top, dirs, files in os.walk(folder):
        dirs.sort()
        rel_dir = os.path.relpath(top, folder)
        parts = [] if rel_dir == "." else rel_dir.split(os.sep)
        for name in sorted(files):
            if not name.endswith(".json"):
                continue
            rel = "/".join(parts + [name])
            full = os.path.join(top, name)
            if not parts and name == FINGERPRINTS:
                pins = _read_json(full, rel)
                continue
            if not parts and SIBLING.fullmatch(name):
                siblings[name] = _read_json(full, rel)
                continue
            kind = _kind_of_file(parts, name)
            if kind is None:
                raise SchemaError(
                    f"{rel}: unexpected json file (expected <ns>.<name>/<n>.json, <x>.schema.json or {FINGERPRINTS})"
                )
            schema = _read_json(full, rel)
            if not isinstance(schema, dict):
                raise SchemaError(f"{rel}: a schema must be a JSON object")
            if schema.get("title") != kind:
                raise SchemaError(f"{rel}: title {schema.get('title')!r} must be the kind id {kind!r}")
            kinds[kind] = schema
    for name, schema in siblings.items():
        if not isinstance(schema, dict):
            raise SchemaError(f"{name}: a schema must be a JSON object")
    return kinds, siblings, pins


def _kind_of_file(parts: list[str], name: str) -> str | None:
    if len(parts) != 1:
        return None
    text = f"{parts[0]}/{name[:-len('.json')]}"
    try:
        kind = KindId.parse(text)
    except KindIdError:
        return None
    return text if str(kind) == text else None


def _check_pins(pins: Any, kinds: dict) -> dict:
    """The `fingerprints.json` entries, checked against the stable kinds of the folder."""
    if pins is None:
        pins = {}
    if not isinstance(pins, dict):
        raise SchemaError(f"{FINGERPRINTS}: must be an object of kind id to fingerprint")
    for kind, value in pins.items():
        if not KindId.is_valid(kind):
            raise SchemaError(f"{FINGERPRINTS}: {kind!r} is not a kind id")
        if KindId.parse(kind).provisional:
            raise SchemaError(f"{FINGERPRINTS}: {kind} is provisional (/0); only stable kinds are pinned")
        if kind not in kinds:
            raise SchemaError(f"{FINGERPRINTS}: entry for {kind}, which is not in the folder")
        if not isinstance(value, str) or not FINGERPRINT.fullmatch(value):
            raise SchemaError(f"{FINGERPRINTS}: {kind}: fingerprint must be 'sha256:' and 64 hex digits")
    return pins


class Registry:
    """The schema folders a process has loaded. `Registry()` starts with gart's own (`gart/schemas`)."""

    def __init__(self) -> None:
        self._kinds: dict[str, dict] = {}  # kind -> {"schema", "fingerprint", "base"}
        self._siblings: dict[str, dict[str, dict]] = {}  # folder -> file name -> schema
        self.load(OWN_SCHEMAS, owner="gart")

    # -- loading ---------------------------------------------------------------------------------------------

    def load(self, path: str | os.PathLike, *, owner: str | None = None, foreign: bool = False) -> Registry:
        """Load a schema folder, all or nothing. Exactly one of `owner` (a namespace) or `foreign=True`."""
        if (owner is None) == (not foreign):
            raise SchemaError("load: give exactly one of owner=<namespace> or foreign=True")
        if owner is not None and owner not in namespaces():
            raise SchemaError(f"load: owner {owner!r} is not in namespaces.json")
        folder = os.path.abspath(os.fspath(path))
        kinds, siblings, pins = _scan(folder)
        fingerprints = {kind: fingerprint(schema) for kind, schema in kinds.items()}
        if owner is not None:
            for kind in sorted(kinds):
                if KindId.parse(kind).namespace != owner:
                    raise SchemaError(f"{kind}: namespace is not that of owner {owner!r} (use foreign=True for a copy)")
        for kind in sorted(kinds):
            known = self._kinds.get(kind)
            if known is not None and known["fingerprint"] != fingerprints[kind]:
                raise SchemaError(f"{kind}: already loaded with a different schema (fingerprint differs)")
        pins = _check_pins(pins, kinds)
        for kind in sorted(kinds):
            if KindId.parse(kind).stable:
                if kind not in pins:
                    raise SchemaError(f"{kind}: stable kind without an entry in {FINGERPRINTS}")
                if pins[kind] != fingerprints[kind]:
                    raise SchemaError(
                        f"{kind}: fingerprint {fingerprints[kind]} does not match {FINGERPRINTS} ({pins[kind]}); "
                        "a stable schema never changes: publish the next version"
                    )
        # Every file is read, so references between them work in any order; check them with the folder in place.
        staged = {kind: {"schema": kinds[kind], "fingerprint": fingerprints[kind], "base": folder} for kind in kinds}

        def resolver(base: Any, target: str) -> tuple:
            if KindId.is_valid(target):
                entry = staged.get(target) or self._kinds.get(target)
                if entry is not None:
                    return entry["schema"], entry["base"]
            elif base == folder and target in siblings:
                return siblings[target], folder
            else:
                other = self._siblings.get(base, {}).get(target)
                if other is not None:
                    return other, base
            raise SchemaError(f"unresolved reference {target!r}")

        for name in sorted(siblings):
            self._check(siblings[name], resolver, folder, name)
        for kind in sorted(kinds):
            self._check(kinds[kind], resolver, folder, kind)
        for kind, entry in staged.items():
            self._kinds.setdefault(kind, entry)
        self._siblings.setdefault(folder, {}).update(siblings)
        return self

    @staticmethod
    def _check(schema: Any, resolver: Any, folder: str, label: str) -> None:
        try:
            check_schema(schema, resolver, folder)
        except SchemaError as exc:
            raise SchemaError(f"{label}: {exc}") from None

    def pin(self, path: str | os.PathLike) -> dict:
        """Write `fingerprints.json` of a folder for its stable kinds; returns the entries written.

        Missing entries are added. An existing entry that differs is never changed: `SchemaError` and the file stays as it
        was. Entries for a `/0` kind or a kind that is not in the folder are an error as well.
        """
        folder = os.path.abspath(os.fspath(path))
        kinds, _siblings, pins = _scan(folder)
        pins = dict(_check_pins(pins, kinds))
        for kind in sorted(kinds):
            if not KindId.parse(kind).stable:
                continue
            current = fingerprint(kinds[kind])
            if kind in pins and pins[kind] != current:
                raise SchemaError(
                    f"{kind}: fingerprint changed ({pins[kind]} -> {current}); a stable schema never changes: "
                    f"publish {KindId.parse(kind).next()} instead"
                )
            pins[kind] = current
        target = os.path.join(folder, FINGERPRINTS)
        text = json.dumps(pins, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
        try:
            with open(target, encoding="utf-8") as handle:
                same = handle.read() == text
        except FileNotFoundError:
            same = False
        if not same:
            with open(target, "w", encoding="utf-8", newline="\n") as handle:
                handle.write(text)
        return pins

    # -- queries ---------------------------------------------------------------------------------------------

    def kinds(self) -> list[str]:
        return sorted(self._kinds)

    def get(self, kind: str) -> dict:
        """A deep copy of the schema of `kind`."""
        entry = self._kinds.get(kind) if isinstance(kind, str) else None
        if entry is None:
            raise SchemaError(f"unknown kind {kind!r}")
        return copy.deepcopy(entry["schema"])

    def _resolve(self, base: Any, target: str) -> tuple:
        if KindId.is_valid(target):
            entry = self._kinds.get(target)
            if entry is not None:
                return entry["schema"], entry["base"]
        else:
            other = self._siblings.get(base, {}).get(target) if isinstance(base, str) else None
            if other is not None:
                return other, base
        raise SchemaError(f"unresolved reference {target!r}")

    def validate(self, artifact: Any, kind: str | None = None) -> list[ValidationError]:
        """Errors of `artifact` against `kind` (default: its top-level `schema` field). Never raises for the artifact."""
        if kind is None:
            if not isinstance(artifact, dict) or "schema" not in artifact:
                return [ValidationError("", "required", {"name": "schema"})]
            kind = artifact["schema"]
        try:
            KindId.parse(kind)
        except KindIdError as exc:
            return [ValidationError("/schema", "kind_invalid", {"value": kind, "reason": exc.code})]
        entry = self._kinds.get(kind)
        if entry is None:
            return [ValidationError("/schema", "kind_unknown", {"kind": kind})]
        return validate(artifact, entry["schema"], self._resolve, entry["base"])

    def validate_schema(self, instance: Any, schema: Any, base: str | os.PathLike | None = None) -> list[ValidationError]:
        """Errors of `instance` against an unregistered `schema`; its sibling refs resolve in the loaded folder `base`."""
        return validate(instance, schema, self._resolve, None if base is None else os.path.abspath(os.fspath(base)))
