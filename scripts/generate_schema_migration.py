#!/usr/bin/env python3
"""Report recursive source/export contract changes against a named prior release.

With --previous-ref the report also carries the record-level data diff (ids added, removed and
changed, membership edges) from internacia_builder.release.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import tempfile
from pathlib import Path
from typing import Any

import _checkout  # noqa: F401  (this checkout's internacia_builder, not an installed one)
import pyarrow as pa
import pyarrow.parquet as pq

from internacia_builder.release import Snapshot, data_diff, extract_sources
from internacia_builder.schemas import logical_type

ROOT = Path(__file__).resolve().parents[1]
DATASETS = ("countries", "intblocks", "blocktypes", "memberships")
ANNOTATIONS = {"description", "title", "$comment", "examples"}


def load_props(schema_path: Path) -> dict[str, Any]:
    return (json.loads(schema_path.read_text()).get("properties") or {}) if schema_path.exists() else {}


def _type_sig(prop: dict) -> str:
    value = prop.get("type", "any")
    return "|".join(sorted(value)) if isinstance(value, list) else str(value)


def diff_props(prev: dict, curr: dict) -> dict:
    return diff_schema({"type": "object", "properties": prev}, {"type": "object", "properties": curr})


def diff_schema(prev: dict, curr: dict) -> dict:
    result = {"added": [], "removed": [], "type_changed": [], "constraints_changed": [], "renamed": []}

    def visit(old, new, path):
        if not isinstance(old, dict) or not isinstance(new, dict):
            if old != new:
                result["constraints_changed"].append({"field": path or "$", "from": old, "to": new})
            return
        if _type_sig(old) != _type_sig(new):
            result["type_changed"].append({"field": path or "$", "from": _type_sig(old), "to": _type_sig(new)})
        for container in ("properties", "$defs", "definitions"):
            before, after = old.get(container, {}), new.get(container, {})
            prefix = path + ("." if path else "") + (f"{container}." if container != "properties" else "")
            result["added"].extend(prefix + key for key in sorted(after.keys() - before.keys()))
            result["removed"].extend(prefix + key for key in sorted(before.keys() - after.keys()))
            for key in sorted(before.keys() & after.keys()):
                visit(before[key], after[key], prefix + key)
        for key in ("items", "additionalProperties", "keys", "values"):
            if isinstance(old.get(key), dict) and isinstance(new.get(key), dict):
                visit(old[key], new[key], path + ("[]" if key == "items" else "." + key))
            elif old.get(key) != new.get(key):
                result["constraints_changed"].append({"field": (path or "$") + "." + key, "from": old.get(key), "to": new.get(key)})
        excluded = ANNOTATIONS | {"type", "properties", "$defs", "definitions", "items", "additionalProperties", "keys", "values"}
        for key in sorted((old.keys() | new.keys()) - excluded):
            before, after = old.get(key), new.get(key)
            if key in ("required", "enum"):
                before = sorted(before or [], key=str)
                after = sorted(after or [], key=str)
            if before != after:
                result["constraints_changed"].append({"field": (path or "$") + "." + key, "from": before, "to": after})

    visit(prev, curr, "")
    return result


def arrow_contract(schema: pa.Schema) -> dict:
    def datatype(t):
        if pa.types.is_struct(t):
            return fields(t)
        if pa.types.is_list(t) or pa.types.is_large_list(t):
            return {"type": "array", "items": datatype(t.value_type)}
        if pa.types.is_map(t):
            return {"type": "map", "keys": datatype(t.key_type), "values": datatype(t.item_type)}
        try:
            return {"type": logical_type(t)}
        except ValueError:
            return {"type": str(t)}

    def fields(fs):
        return {"type": "object", "properties": {f.name: {**datatype(f.type), "nullable": f.nullable} for f in fs}}

    return fields(schema)


def _split_top_level(text: str) -> list[str]:
    parts, depth, start = [], 0, 0
    for i, char in enumerate(text):
        depth += char == "<"
        depth -= char == ">"
        if char == "," and depth == 0:
            parts.append(text[start:i])
            start = i + 1
    parts.append(text[start:])
    return parts


def logical_contract(type_: str) -> dict:
    """Parse an ``internacia-logical-types/1`` string into the ``arrow_contract`` shape.
    Nested struct fields are nullable, as in every export schema."""
    if type_.startswith("list<"):
        return {"type": "array", "items": logical_contract(type_[5:-1])}
    if type_.startswith("map<"):
        key, value = _split_top_level(type_[4:-1])
        return {"type": "map", "keys": logical_contract(key), "values": logical_contract(value)}
    if type_.startswith("struct<"):
        props = {}
        for part in _split_top_level(type_[7:-1]):
            name, _, sub = part.partition(":")
            props[name] = {**logical_contract(sub), "nullable": True}
        return {"type": "object", "properties": props}
    return {"type": type_}


def contract_table(contract: dict, name: str) -> dict | None:
    table = next((t for t in contract.get("tables", []) if t["name"] == name), None)
    if table is None:
        return None
    return {
        "type": "object",
        "properties": {c["name"]: {**logical_contract(c["type"]), "nullable": c["nullable"]} for c in table["columns"]},
    }


def _git_bytes(ref: str, path: str) -> bytes | None:
    result = subprocess.run(["git", "show", f"{ref}:{path}"], cwd=ROOT, capture_output=True, check=False)
    return result.stdout if result.returncode == 0 else None


def build_migration(previous_dir: Path | None, current_dir: Path, version: str, *, previous_ref: str | None = None, current_datasets: Path | None = None) -> dict:
    baseline_commit = None
    if previous_ref:
        result = subprocess.run(["git", "rev-parse", "--verify", f"{previous_ref}^{{commit}}"], cwd=ROOT, capture_output=True, text=True, check=True)
        baseline_commit = result.stdout.strip()
    available = bool(previous_ref or (previous_dir and previous_dir.is_dir()))
    datasets, exports, missing = {}, {}, []
    for name in DATASETS:
        current_path = current_dir / f"{name}.schema.json"
        old_bytes = _git_bytes(previous_ref, f"data/schemas/{name}.schema.json") if previous_ref else None
        if previous_dir and (previous_dir / current_path.name).exists():
            old_bytes = (previous_dir / current_path.name).read_bytes()
        if current_path.exists():
            current = json.loads(current_path.read_text())
            if old_bytes is None:
                missing.append(f"source:{name}")
            datasets[name] = diff_schema(json.loads(old_bytes) if old_bytes else {}, current) if available else diff_props({}, {})
        if name not in datasets:
            datasets[name] = diff_props({}, {})
        if current_datasets and (current_datasets / f"{name}.parquet").exists():
            current = arrow_contract(pq.read_schema(current_datasets / f"{name}.parquet"))
            old_parquet = _git_bytes(previous_ref, f"data/datasets/{name}.parquet") if previous_ref else None
            old_contract = _git_bytes(previous_ref, "data/datasets/contract.json") if previous_ref else None
            previous_parquet = previous_dir / f"{name}.parquet" if previous_dir else None
            contract_before = contract_table(json.loads(old_contract), name) if old_contract else None
            if old_parquet:
                before = arrow_contract(pq.read_schema(pa.BufferReader(old_parquet)))
            elif contract_before is not None:
                # Binary exports are not committed since db-1.3; the committed contract describes them.
                before = contract_before
            elif previous_parquet and previous_parquet.exists():
                before = arrow_contract(pq.read_schema(previous_parquet))
            else:
                missing.append(f"export:{name}")
                before = {}
            exports[name] = diff_schema(before, current) if available else diff_props({}, {})
    changed = any(d[k] for d in [*datasets.values(), *exports.values()] for k in ("added", "removed", "type_changed", "constraints_changed"))
    data = None
    if previous_ref:
        with tempfile.TemporaryDirectory() as tmp:
            before = Snapshot.load(extract_sources(ROOT, previous_ref, Path(tmp)))
        data = data_diff(before, Snapshot.load(ROOT))
    return {
        "version": version, "schema_changed": changed if available else None,
        "baseline": {"ref": previous_ref, "commit": baseline_commit, "directory": str(previous_dir) if previous_dir else None,
                     "status": "partial" if available and missing else "available" if available else "unavailable",
                     "missing_contracts": missing},
        "note": "Recursive source and export schema differences; unavailable baselines do not establish compatibility",
        "datasets": datasets, "exports": exports, "data": data,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    previous = parser.add_mutually_exclusive_group()
    previous.add_argument("--previous", type=Path)
    previous.add_argument("--previous-ref", help="Explicit previous release tag or commit")
    parser.add_argument("--current", type=Path, default=ROOT / "data/schemas")
    parser.add_argument("--current-datasets", type=Path)
    parser.add_argument("--version", required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = build_migration(args.previous, args.current, args.version, previous_ref=args.previous_ref, current_datasets=args.current_datasets)
    out = args.output or ROOT / "data/datasets" / f"migration.v{args.version}.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2) + "\n")
    print(f"Wrote {out} (schema_changed={result['schema_changed']}; baseline={result['baseline']['status']})")


if __name__ == "__main__":
    main()
