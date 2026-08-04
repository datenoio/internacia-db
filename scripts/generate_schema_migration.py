#!/usr/bin/env python3
"""Compare JSON Schema property sets and emit migration.vX.Y.Z.json.

Usage:
  python scripts/generate_schema_migration.py \\
    --previous data/datasets/schema_baseline/ \\
    --current data/schemas/ \\
    --version 1.11.0 \\
    --output data/datasets/migration.v1.11.0.json

If --previous is missing, writes an empty migration (no prior baseline).
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DATASETS = ("countries", "intblocks", "blocktypes")


def load_props(schema_path: Path) -> dict[str, Any]:
    if not schema_path.exists():
        return {}
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    return dict(schema.get("properties") or {})


def _type_sig(prop: dict[str, Any]) -> str:
    t = prop.get("type")
    if isinstance(t, list):
        return "|".join(str(x) for x in t)
    if t:
        return str(t)
    if "enum" in prop:
        return "enum:" + ",".join(str(x) for x in prop["enum"])
    return "any"


def diff_props(prev: dict[str, Any], curr: dict[str, Any]) -> dict[str, Any]:
    added = sorted(set(curr) - set(prev))
    removed = sorted(set(prev) - set(curr))
    type_changed = []
    for name in sorted(set(prev) & set(curr)):
        if _type_sig(prev[name] if isinstance(prev[name], dict) else {}) != _type_sig(
            curr[name] if isinstance(curr[name], dict) else {}
        ):
            type_changed.append(
                {
                    "field": name,
                    "from": _type_sig(prev[name] if isinstance(prev[name], dict) else {}),
                    "to": _type_sig(curr[name] if isinstance(curr[name], dict) else {}),
                }
            )
    return {
        "added": added,
        "removed": removed,
        "type_changed": type_changed,
        "renamed": [],
    }


def build_migration(previous_dir: Path | None, current_dir: Path, version: str) -> dict[str, Any]:
    datasets: dict[str, Any] = {}
    changed = False
    for name in DATASETS:
        curr = load_props(current_dir / f"{name}.schema.json")
        prev = load_props(previous_dir / f"{name}.schema.json") if previous_dir else {}
        d = diff_props(prev, curr) if previous_dir else {"added": [], "removed": [], "type_changed": [], "renamed": []}
        if previous_dir and (d["added"] or d["removed"] or d["type_changed"]):
            changed = True
        datasets[name] = d
    return {
        "version": version,
        "schema_changed": changed if previous_dir else False,
        "note": "Field-level schema migration for Internacia datasets",
        "datasets": datasets,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--previous", type=Path, default=None, help="Directory with previous *.schema.json")
    parser.add_argument(
        "--current",
        type=Path,
        default=ROOT / "data" / "schemas",
        help="Directory with current *.schema.json",
    )
    parser.add_argument("--version", required=True, help="Semver for migration file, e.g. 1.11.0")
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Output path (default: data/datasets/migration.vVERSION.json)",
    )
    args = parser.parse_args()
    out = args.output or (ROOT / "data" / "datasets" / f"migration.v{args.version}.json")
    prev = args.previous.resolve() if args.previous else None
    if prev and not prev.exists():
        prev = None
    migration = build_migration(prev, args.current.resolve(), args.version)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(migration, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {out} (schema_changed={migration['schema_changed']})")


if __name__ == "__main__":
    main()
