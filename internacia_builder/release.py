"""Release train: what changed since the last release, which version comes next, and the bump.

``scripts/prepare_release.py`` and ``.github/workflows/release-train.yml`` use this module to
open a monthly release pull request; ``scripts/generate_schema_migration.py`` adds the same data
diff to ``migration.vX.Y.Z.json``.

The level follows docs/versioning-policy.md:

- ``major``: a removed table, column, source field, enum value or record id, or a changed
  column type. The train never releases these; a maintainer batches MAJOR changes by hand.
- ``minor``: added tables, columns, source fields, enum values or records.
- ``patch``: any other change to the data sources or the builder.
- ``none``: nothing that affects the release changed.
"""

from __future__ import annotations

import io
import json
import re
import subprocess
import tarfile
import tempfile
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Any

import pyarrow as pa
import pyarrow.parquet as pq

from internacia_builder.contract import CONTRACT_FILE, _schema_enums, build_contract
from internacia_builder.paths import project_root
from internacia_builder.schemas import schema_columns
from internacia_builder.validate.registry import load_yaml

SOURCE_PATHS = (
    "data/countries",
    "data/intblocks",
    "data/blocktypes",
    "data/schemas",
    "data/countries_aliases.yaml",
    "data/intblocks_aliases.yaml",
    "data/attribute_intblock_migrations.yaml",
    "data/borders",
)
RELEASE_PATHS = ("data/", "internacia_builder/")
SCHEMA_FILES = ("countries", "intblocks", "blocktypes", "memberships")
MEMBERSHIP_FIELDS = ("status", "joined", "left", "role")
LEVELS = ("none", "patch", "minor", "major")


def _git(root: Path, *args: str) -> str:
    return subprocess.run(["git", *args], cwd=root, capture_output=True, text=True, check=True).stdout


def latest_release_tag(root: Path | None = None, ref: str = "HEAD") -> str | None:
    """The newest ``vX.Y.Z`` tag reachable from ``ref``."""
    root = root or project_root()
    try:
        return _git(root, "describe", "--tags", "--abbrev=0", "--match", "v[0-9]*", ref).strip() or None
    except subprocess.CalledProcessError:
        return None


def changed_paths(root: Path, base: str, ref: str = "HEAD") -> list[str]:
    """Files under data/ or internacia_builder/ that differ between ``base`` and ``ref``."""
    out = _git(root, "diff", "--name-only", f"{base}..{ref}", "--", *RELEASE_PATHS)
    return [line for line in out.splitlines() if line]


def extract_sources(root: Path, ref: str, destination: Path) -> Path:
    """Write the data sources as of ``ref`` under ``destination`` (same layout as the repo)."""
    present = set(_git(root, "ls-tree", "--name-only", ref, "data/").split())
    paths = [p for p in SOURCE_PATHS if p in present]
    archive = subprocess.run(["git", "archive", ref, *paths], cwd=root, capture_output=True, check=True).stdout
    with tarfile.open(fileobj=io.BytesIO(archive)) as tar:
        tar.extractall(destination, filter="data")
    return destination


def _show(root: Path, ref: str, path: str) -> bytes | None:
    result = subprocess.run(["git", "show", f"{ref}:{path}"], cwd=root, capture_output=True, check=False)
    return result.stdout if result.returncode == 0 else None


@dataclass
class Snapshot:
    """The records of one source tree, keyed by their stable ids."""

    countries: dict[str, dict[str, Any]] = field(default_factory=dict)
    intblocks: dict[str, dict[str, Any]] = field(default_factory=dict)
    blocktypes: dict[str, dict[str, Any]] = field(default_factory=dict)
    aliases: dict[str, set[str]] = field(default_factory=dict)

    @classmethod
    def load(cls, root: Path) -> Snapshot:
        snap = cls()
        for path in sorted((root / "data/countries").glob("*.yaml")):
            record = load_yaml(path)
            if isinstance(record, dict) and record.get("code"):
                snap.countries[str(record["code"])] = record
        for path in sorted((root / "data/intblocks").rglob("*.yaml")):
            record = load_yaml(path)
            if isinstance(record, dict) and record.get("id"):
                snap.intblocks[str(record["id"])] = record
        blocktypes = root / "data/blocktypes/blocktypes.yaml"
        if blocktypes.exists():
            for entry in load_yaml(blocktypes) or []:
                if isinstance(entry, dict) and entry.get("id"):
                    snap.blocktypes[str(entry["id"])] = entry
        for dataset in ("countries", "intblocks"):
            path = root / f"data/{dataset}_aliases.yaml"
            entries = (load_yaml(path) or []) if path.exists() else []
            snap.aliases[dataset] = {str(a["alias"]) for a in entries if isinstance(a, dict) and a.get("alias")}
        return snap

    def memberships(self) -> dict[tuple[str, str], dict[str, Any]]:
        edges: dict[tuple[str, str], dict[str, Any]] = {}
        for block_id, record in self.intblocks.items():
            for include in record.get("includes") or []:
                if isinstance(include, dict) and include.get("type", "country") == "country" and include.get("id"):
                    edges.setdefault(
                        (block_id, str(include["id"])),
                        {name: include.get(name) for name in MEMBERSHIP_FIELDS},
                    )
        return edges


def _records_diff(before: dict[str, Any], after: dict[str, Any]) -> dict[str, Any]:
    return {
        "count": [len(before), len(after)],
        "added": sorted(after.keys() - before.keys()),
        "removed": sorted(before.keys() - after.keys()),
        "changed": sorted(k for k in before.keys() & after.keys() if before[k] != after[k]),
    }


def data_diff(before: Snapshot, after: Snapshot) -> dict[str, Any]:
    """Record-level differences: ids added, removed and changed, and membership edges."""
    old_edges, new_edges = before.memberships(), after.memberships()
    changed_edges = []
    for key in sorted(old_edges.keys() & new_edges.keys()):
        fields = {
            name: [old_edges[key][name], new_edges[key][name]]
            for name in MEMBERSHIP_FIELDS
            if old_edges[key][name] != new_edges[key][name]
        }
        if fields:
            changed_edges.append({"intblock": key[0], "country": key[1], "fields": fields})

    def edge_list(keys: set[tuple[str, str]], edges: dict) -> list[dict[str, Any]]:
        return [{"intblock": b, "country": c, "status": edges[(b, c)]["status"]} for b, c in sorted(keys)]

    return {
        "countries": _records_diff(before.countries, after.countries),
        "intblocks": _records_diff(before.intblocks, after.intblocks),
        "blocktypes": _records_diff(before.blocktypes, after.blocktypes),
        "memberships": {
            "count": [len(old_edges), len(new_edges)],
            "added": edge_list(new_edges.keys() - old_edges.keys(), new_edges),
            "removed": edge_list(old_edges.keys() - new_edges.keys(), old_edges),
            "changed": changed_edges,
        },
        "aliases": {
            name: {"added": sorted(after.aliases.get(name, set()) - before.aliases.get(name, set()))}
            for name in ("countries", "intblocks")
        },
    }


Columns = dict[str, list[tuple[str, str, bool]]]


def _contract_columns(contract: dict[str, Any]) -> Columns:
    return {
        t["name"]: [(c["name"], c["type"], c["nullable"]) for c in t["columns"]]
        for t in contract["tables"]
    }


def _columns_at(root: Path, ref: str, current: dict[str, Any]) -> tuple[Columns, set[str]] | None:
    """Exported columns of the release at ``ref`` and the tables they cover.

    Releases before contract.json (v3.0.0 and earlier) are read from their committed Parquet
    files, which cover every table except DuckDB-only ones such as ``_meta``.
    """
    contract = _show(root, ref, f"data/datasets/{CONTRACT_FILE}")
    if contract:
        columns = _contract_columns(json.loads(contract))
        return columns, {t["name"] for t in current["tables"]}
    columns = {}
    for table in current["tables"]:
        data = _show(root, ref, f"data/datasets/{table['name']}.parquet")
        if data:
            columns[table["name"]] = schema_columns(pq.read_schema(pa.BufferReader(data)))
    if not columns:
        return None
    covered = set(columns) | {t["name"] for t in current["tables"] if t["kind"] == "view"}
    return columns, covered


def _source_schema(root: Path, ref: str | None, name: str) -> dict[str, Any]:
    if ref is None:
        path = root / f"data/schemas/{name}.schema.json"
        return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
    data = _show(root, ref, f"data/schemas/{name}.schema.json")
    return json.loads(data) if data else {}


@dataclass
class Plan:
    """The outcome of comparing the working tree with the last release."""

    previous: str | None
    level: str
    reasons: dict[str, list[str]]
    diff: dict[str, Any] | None
    changed_paths: list[str]

    @property
    def version(self) -> str | None:
        if self.previous is None or self.level in ("none", "major"):
            return None
        return next_version(self.previous, self.level)


def next_version(previous: str, level: str) -> str:
    major, minor, patch = (int(p) for p in previous.removeprefix("v").split("."))
    if level == "major":
        return f"{major + 1}.0.0"
    if level == "minor":
        return f"{major}.{minor + 1}.0"
    return f"{major}.{minor}.{patch + 1}"


def schema_changes(root: Path, previous: str) -> dict[str, list[str]]:
    """Export columns, source fields and enum values added or removed since ``previous``."""
    reasons: dict[str, list[str]] = {"major": [], "minor": []}
    current = build_contract("0.0.0", root)
    recorded = _columns_at(root, previous, current)
    if recorded is None:
        reasons["major"].append(f"no export schema recorded for {previous}; compare by hand")
    else:
        before, covered = recorded
        after = {name: cols for name, cols in _contract_columns(current).items() if name in covered}
        for table in sorted(before.keys() - after.keys()):
            reasons["major"].append(f"table {table} removed")
        for table in sorted(after.keys() - before.keys()):
            reasons["minor"].append(f"table {table} added")
        for table in sorted(before.keys() & after.keys()):
            old = {name: (type_, nullable) for name, type_, nullable in before[table]}
            new = {name: (type_, nullable) for name, type_, nullable in after[table]}
            for column in sorted(old.keys() - new.keys()):
                reasons["major"].append(f"column {table}.{column} removed")
            for column in sorted(new.keys() - old.keys()):
                reasons["minor"].append(f"column {table}.{column} added")
            for column in sorted(old.keys() & new.keys()):
                if old[column][0] != new[column][0]:
                    reasons["major"].append(
                        f"column {table}.{column} type {old[column][0]} -> {new[column][0]}"
                    )
    for name in SCHEMA_FILES:
        old_schema, new_schema = _source_schema(root, previous, name), _source_schema(root, None, name)
        old_props = set(old_schema.get("properties") or {})
        new_props = set(new_schema.get("properties") or {})
        reasons["major"].extend(f"source field {name}.{p} removed" for p in sorted(old_props - new_props))
        reasons["minor"].extend(f"source field {name}.{p} added" for p in sorted(new_props - old_props))
        old_enums, new_enums = dict(_schema_enums(old_schema)), dict(_schema_enums(new_schema))
        for path in sorted(old_enums.keys() & new_enums.keys()):
            removed = sorted(set(old_enums[path]) - set(new_enums[path]))
            added = sorted(set(new_enums[path]) - set(old_enums[path]))
            if removed:
                reasons["major"].append(f"enum {name}.{path} values removed: {', '.join(removed)}")
            if added:
                reasons["minor"].append(f"enum {name}.{path} values added: {', '.join(added)}")
    return reasons


def plan_release(root: Path | None = None, previous: str | None = None) -> Plan:
    """Compare the working tree with the last release and choose the next level."""
    root = root or project_root()
    previous = previous or latest_release_tag(root)
    if previous is None:
        return Plan(None, "none", {"major": ["no previous vX.Y.Z tag"]}, None, [])
    paths = changed_paths(root, previous)
    if not paths:
        return Plan(previous, "none", {}, None, [])
    with tempfile.TemporaryDirectory() as tmp:
        before = Snapshot.load(extract_sources(root, previous, Path(tmp)))
    diff = data_diff(before, Snapshot.load(root))
    reasons = schema_changes(root, previous)
    for dataset in ("countries", "intblocks", "blocktypes"):
        removed = diff[dataset]["removed"]
        if removed:
            reasons["major"].append(f"{dataset} removed: {', '.join(removed)}")
        added = diff[dataset]["added"]
        if added:
            reasons["minor"].append(f"{dataset} added: {', '.join(added)}")
    level = "major" if reasons["major"] else "minor" if reasons["minor"] else "patch"
    return Plan(previous, level, reasons, diff, paths)


def _limited(items: list[str], limit: int = 20) -> str:
    shown = ", ".join(f"`{item}`" for item in items[:limit])
    return shown + (f" and {len(items) - limit} more" if len(items) > limit else "")


def render_summary(plan: Plan) -> str:
    """Markdown summary of a plan, used for the CHANGELOG entry and the release PR."""
    lines: list[str] = []
    if plan.diff:
        diff = plan.diff
        for dataset in ("countries", "intblocks", "blocktypes"):
            d = diff[dataset]
            parts = [f"{d['count'][0]} → {d['count'][1]} records"]
            if d["added"]:
                parts.append(f"added {_limited(d['added'])}")
            if d["removed"]:
                parts.append(f"removed {_limited(d['removed'])}")
            if d["changed"]:
                parts.append(f"{len(d['changed'])} changed")
            lines.append(f"- {dataset.capitalize()}: " + "; ".join(parts))
        m = diff["memberships"]
        lines.append(
            f"- Membership edges: {m['count'][0]} → {m['count'][1]}; {len(m['added'])} added, "
            f"{len(m['removed'])} removed, {len(m['changed'])} changed"
        )
        for name, value in diff["aliases"].items():
            if value["added"]:
                lines.append(f"- New {name} aliases: {_limited(value['added'])}")
    for level in ("major", "minor"):
        for reason in plan.reasons.get(level, []):
            if not any(reason.startswith(f"{d} ") for d in ("countries", "intblocks", "blocktypes")):
                lines.append(f"- Schema ({level}): {reason}")
    return "\n".join(lines)


def apply_version(root: Path, version: str, released: date, summary: str) -> list[Path]:
    """Write ``version`` everywhere the release gate checks it and date the CHANGELOG entry."""
    changelog = root / "CHANGELOG.md"
    text = changelog.read_text(encoding="utf-8")
    head, sep, rest = text.partition("## [Unreleased]\n")
    if not sep:
        raise ValueError("CHANGELOG.md has no '## [Unreleased]' section")
    body, nxt, tail = rest.partition("\n## [")
    entry = body.strip("\n")
    data = f"### Data changes since the previous release\n\n{summary}\n" if summary else ""
    section = f"## [{version}] - {released.isoformat()}\n\n" + (f"{entry}\n\n" if entry else "") + data
    changelog.write_text(f"{head}## [Unreleased]\n\n{section}{nxt}{tail}", encoding="utf-8")

    replacements = {
        "pyproject.toml": (r'(?m)^version = "[^"]+"', f'version = "{version}"'),
        "internacia_builder/__init__.py": (r'(?m)^__version__ = "[^"]+"', f'__version__ = "{version}"'),
        "CITATION.cff": (r"(?m)^version: .+$", f"version: {version}"),
        "uv.lock": (r'(name = "internacia-builder"\nversion = )"[^"]+"', rf'\g<1>"{version}"'),
    }
    written = [changelog]
    for rel, (pattern, replacement) in replacements.items():
        path = root / rel
        if not path.exists():
            continue
        new_text, count = re.subn(pattern, replacement, path.read_text(encoding="utf-8"), count=1)
        if count != 1:
            raise ValueError(f"version not found in {rel}")
        if rel == "CITATION.cff":
            new_text = re.sub(r"(?m)^date-released: .+$", f"date-released: {released.isoformat()}", new_text)
        path.write_text(new_text, encoding="utf-8")
        written.append(path)
    return written
