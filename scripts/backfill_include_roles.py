#!/usr/bin/env python3
"""Safely backfill reviewed route roles (``includes[].role``) on infrastructure intblocks.

The default mode is a non-mutating dry run. ``--apply`` performs surgical text edits only
after the complete manifest and repository inventory pass validation. A different existing
role is a conflict and blocks the whole apply; a record that already matches is left
byte-for-byte unchanged.

Roles come only from the reviewed manifest (``data/schemas/include_roles_pilot.yaml``).
A manifest entry must give a role for every current country entry of the record, and may
add blocktypes (for example ``corridor``) that make the record eligible for roles. The edit
changes only ``blocktype`` (appended values), ``includes[].role``, ``provenance`` and
``last_verified``. Roles must cover exactly the record's current country entries and come from a
source that states the route, so a changed record has had its roster checked: ``last_verified``
is set to the manifest's ``verified_on`` date.
"""

from __future__ import annotations

import copy
import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import _checkout  # noqa: F401  (this checkout's internacia_builder, not an installed one)
import typer
import yaml

from internacia_builder.yaml_io import safe_load

app = typer.Typer(add_completion=False, help="Validate or apply reviewed includes[].role values.")

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = ROOT / "data" / "schemas" / "include_roles_pilot.yaml"
CATALOG = ROOT / "data" / "schemas" / "include_roles.yaml"
EVIDENCE_FIELDS = ("source", "url", "retrieved_at")
TOP_KEY = re.compile(r"^[A-Za-z_][A-Za-z0-9_-]*:")


class BackfillValidationError(ValueError):
    """Raised when the manifest or repository inventory is unsafe to apply."""


@dataclass(frozen=True)
class PlannedChange:
    record_id: str
    path: str
    action: str
    current: str | None = None


@dataclass
class BackfillReport:
    mode: str
    manifest: str
    expected_count: int
    records: int
    pending: int
    already_set: int
    conflicts: int
    applied: int
    changes: list[PlannedChange]

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["changes"] = [asdict(change) for change in self.changes]
        return payload


def _current_countries(record: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        inc for inc in record.get("includes") or []
        if isinstance(inc, dict) and (inc.get("type") or "country") == "country" and not inc.get("left")
    ]


def _kind(blocktypes: list[str], catalog: dict[str, Any]) -> tuple[str, dict[str, Any]] | None:
    present = set(blocktypes)
    for name, kind in (catalog.get("kinds") or {}).items():
        if present & set(kind.get("blocktypes") or []):
            return str(name), kind
    return None


def load_manifest(path: Path) -> tuple[dict[str, dict[str, Any]], dict[str, Any]]:
    raw = safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict) or not isinstance(raw.get("records"), dict) or not raw["records"]:
        raise BackfillValidationError("manifest must have a non-empty records mapping")
    expected = raw.get("expected_count")
    if not isinstance(expected, int) or expected != len(raw["records"]):
        raise BackfillValidationError(f"manifest expected_count={expected} but contains {len(raw['records'])} records")
    for record_id, entry in raw["records"].items():
        if not isinstance(entry, dict) or not isinstance(entry.get("roles"), dict) or not entry["roles"]:
            raise BackfillValidationError(f"{record_id}: roles must be a non-empty mapping")
        evidence = entry.get("evidence")
        if not isinstance(evidence, list) or not evidence:
            raise BackfillValidationError(f"{record_id}: evidence must be a non-empty list")
        for item in evidence:
            missing = [k for k in EVIDENCE_FIELDS if not (isinstance(item, dict) and item.get(k))]
            if missing:
                raise BackfillValidationError(f"{record_id}: evidence is missing fields: {missing}")
    return raw["records"], raw


def _include_id(line: str) -> str | None:
    match = re.match(r"^- id:\s*(.+?)\s*$", line)
    if not match:
        return None
    return str(safe_load(match.group(1)))


def _edit_text(text: str, roles: dict[str, str], add_blocktypes: list[str], evidence: list[dict[str, Any]],
               existing_role_urls: set[str]) -> str:
    lines = text.splitlines(keepends=True)
    out: list[str] = []
    section: str | None = None
    current_id: str | None = None
    pending_role: str | None = None
    blocktype_done = False

    def flush_role() -> None:
        nonlocal pending_role
        if pending_role is not None:
            out.append(f"  role: {pending_role}\n")
            pending_role = None

    for line in lines:
        if TOP_KEY.match(line):
            flush_role()
            if section == "blocktype" and not blocktype_done:
                out.extend(f"- {value}\n" for value in add_blocktypes)
                blocktype_done = True
            section = line.split(":", 1)[0]
            current_id = None
            out.append(line)
            continue
        if section == "includes" and line.startswith("- "):
            flush_role()
            current_id = _include_id(line)
            if current_id in roles:
                pending_role = roles[current_id]
        out.append(line)
    flush_role()
    if section == "blocktype" and not blocktype_done:
        out.extend(f"- {value}\n" for value in add_blocktypes)
    text = "".join(out)

    new_evidence = [e for e in evidence if str(e["url"]) not in existing_role_urls]
    if new_evidence:
        entry = "".join(
            "- field: includes\n"
            f"  source: {json.dumps(str(e['source']), ensure_ascii=False)}\n"
            f"  retrieved_at: {json.dumps(str(e['retrieved_at']))}\n"
            f"  url: {json.dumps(str(e['url']), ensure_ascii=False)}\n"
            for e in new_evidence
        )
        match = re.search(r"^provenance:[ \t]*\n", text, flags=re.MULTILINE)
        if match is None and re.search(r"^provenance:", text, flags=re.MULTILINE):
            raise BackfillValidationError("provenance is not a block list; edit the record by hand")
        if match is None:
            text = text + ("" if text.endswith("\n") else "\n") + "provenance:\n" + entry
        else:
            text = text[: match.end()] + entry + text[match.end():]
    return text


def _set_last_verified(text: str, verified_on: str) -> str:
    line = f"last_verified: '{verified_on}'\n"
    match = re.search(r"^last_verified:.*\n", text, flags=re.MULTILINE)
    if match:
        return text[: match.start()] + line + text[match.end():]
    anchor = re.search(r"^provenance:", text, flags=re.MULTILINE)
    if anchor:
        return text[: anchor.start()] + line + text[anchor.start():]
    return text + ("" if text.endswith("\n") else "\n") + line


def reconcile(text: str, entry: dict[str, Any], catalog: dict[str, Any],
              verified_on: str | None = None) -> tuple[str, str, str | None]:
    record = safe_load(text)
    if not isinstance(record, dict):
        raise BackfillValidationError("intblock YAML must contain a mapping")
    roles = {str(k): str(v) for k, v in entry["roles"].items()}
    add = [str(b) for b in entry.get("add_blocktypes") or [] if str(b) not in (record.get("blocktype") or [])]
    kind = _kind(list(record.get("blocktype") or []) + add, catalog)
    if kind is None:
        raise BackfillValidationError("record has no role-bearing blocktype (gaspipeline, oilpipeline or corridor)")
    kind_name, spec = kind
    allowed = set(spec.get("roles") or [])
    bad = sorted(f"{k}={v}" for k, v in roles.items() if v not in allowed)
    if bad:
        raise BackfillValidationError(f"roles not valid for a {kind_name}: {bad}")
    current = {str(inc.get("id")): inc for inc in _current_countries(record)}
    if set(roles) != set(current):
        raise BackfillValidationError(
            f"roles must cover exactly the current country entries; missing {sorted(set(current) - set(roles))}, "
            f"extra {sorted(set(roles) - set(current))}"
        )
    counts: dict[str, int] = {}
    for value in roles.values():
        counts[value] = counts.get(value, 0) + 1
    for role, minimum in (spec.get("requires") or {}).items():
        if counts.get(str(role), 0) < int(minimum):
            raise BackfillValidationError(f"a {kind_name} needs at least {minimum} '{role}'")

    conflicts = sorted(
        f"{cid}={inc['role']}" for cid, inc in current.items() if inc.get("role") and inc["role"] != roles[cid]
    )
    if conflicts:
        return text, "conflict", ",".join(conflicts)
    role_urls = {
        str(p.get("url")) for p in record.get("provenance") or []
        if isinstance(p, dict) and p.get("field") == "includes" and p.get("url")
    }
    evidence = list(entry["evidence"])
    if all(inc.get("role") == roles[cid] for cid, inc in current.items()) and not add \
            and all(str(e["url"]) in role_urls for e in evidence):
        return text, "already_set", None

    pending_roles = {cid: role for cid, role in roles.items() if current[cid].get("role") != role}
    updated = _edit_text(text, pending_roles, add, evidence, role_urls)
    if verified_on and pending_roles:
        updated = _set_last_verified(updated, verified_on)
    parsed = safe_load(updated)
    expected = copy.deepcopy(record)
    if verified_on and pending_roles:
        expected["last_verified"] = verified_on
    expected["blocktype"] = list(record.get("blocktype") or []) + add
    for inc in expected.get("includes") or []:
        if isinstance(inc, dict) and str(inc.get("id")) in pending_roles and inc in _current_countries(expected):
            inc["role"] = pending_roles[str(inc.get("id"))]
    if {k: v for k, v in parsed.items() if k != "provenance"} != {k: v for k, v in expected.items() if k != "provenance"}:
        raise BackfillValidationError("surgical edit changed more than blocktype and includes[].role")
    return updated, "pending", None


def discover_records(root: Path) -> dict[str, Path]:
    records: dict[str, Path] = {}
    for path in sorted((root / "data" / "intblocks").glob("*/*.yaml")):
        record = safe_load(path.read_text(encoding="utf-8"))
        if isinstance(record, dict) and record.get("id"):
            if str(record["id"]) in records:
                raise BackfillValidationError(f"duplicate intblock id {record['id']}")
            records[str(record["id"])] = path
    return records


def execute_backfill(root: Path, manifest_path: Path, *, mode: str, catalog_path: Path | None = None) -> BackfillReport:
    if mode not in {"dry-run", "check", "apply"}:
        raise BackfillValidationError(f"unknown mode: {mode}")
    catalog = safe_load((catalog_path or root / "data" / "schemas" / "include_roles.yaml").read_text(encoding="utf-8"))
    entries, metadata = load_manifest(manifest_path)
    records = discover_records(root)
    missing = sorted(set(entries) - set(records))
    if missing:
        raise BackfillValidationError(f"manifest ids missing from repository: {missing}")
    changes: list[PlannedChange] = []
    updated: dict[Path, str] = {}
    for record_id in sorted(entries):
        path = records[record_id]
        try:
            text, action, current = reconcile(path.read_text(encoding="utf-8"), entries[record_id], catalog,
                                              None if metadata.get("verified_on") is None else str(metadata["verified_on"]))
        except BackfillValidationError as exc:
            raise BackfillValidationError(f"{record_id}: {exc}") from exc
        changes.append(PlannedChange(record_id, str(path.relative_to(root)), action, current))
        if action == "pending":
            updated[path] = text
    conflicts = [c for c in changes if c.action == "conflict"]
    if conflicts and mode == "apply":
        raise BackfillValidationError(f"refusing partial apply because conflicting roles exist: {[c.record_id for c in conflicts]}")
    applied = 0
    if mode == "apply":
        for path, text in updated.items():
            path.write_text(text, encoding="utf-8")
            applied += 1
    return BackfillReport(
        mode=mode, manifest=str(manifest_path), expected_count=int(metadata["expected_count"]), records=len(changes),
        pending=sum(c.action == "pending" for c in changes), already_set=sum(c.action == "already_set" for c in changes),
        conflicts=len(conflicts), applied=applied, changes=changes,
    )


@app.command()
def main(
    root: Path = typer.Option(ROOT, help="Repository root containing data/intblocks."),
    manifest: Path = typer.Option(DEFAULT_MANIFEST, help="Reviewed include-roles manifest."),
    apply: bool = typer.Option(False, "--apply", help="Write all pending records after complete validation."),
    check: bool = typer.Option(False, "--check", help="Exit non-zero when pending records remain; never write."),
    report_json: Path | None = typer.Option(None, help="Optional path for a machine-readable report."),
) -> None:
    """Dry-run by default."""
    if apply and check:
        typer.echo("--apply and --check are mutually exclusive", err=True)
        raise typer.Exit(code=2)
    mode = "apply" if apply else "check" if check else "dry-run"
    try:
        report = execute_backfill(root.resolve(), manifest.resolve(), mode=mode)
    except (BackfillValidationError, OSError, yaml.YAMLError) as exc:
        typer.echo(f"ERROR: {exc}", err=True)
        raise typer.Exit(code=2) from exc
    payload = report.to_dict()
    typer.echo("mode={mode} records={records} pending={pending} already_set={already_set} "
               "conflicts={conflicts} applied={applied}".format(**payload))
    if report_json is not None:
        report_json.parent.mkdir(parents=True, exist_ok=True)
        report_json.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if report.conflicts:
        raise typer.Exit(code=2)
    if mode == "check" and report.pending:
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
