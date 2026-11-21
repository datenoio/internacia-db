#!/usr/bin/env python3
"""Safely backfill reviewed membership start dates (``includes[].joined``) on intblocks.

The default mode is a non-mutating dry run. ``--apply`` performs surgical text edits only after
the complete manifest and repository inventory pass validation. A different existing ``joined``
value is a conflict and blocks the whole apply; an entry that already matches is left unchanged.

Dates come only from the reviewed manifest (``data/schemas/includes_joined_tier1.yaml`` by
default). Each manifest record maps ``includes[].id`` to a date with the precision its source
gives (``YYYY``, ``YYYY-MM`` or ``YYYY-MM-DD``) and lists the evidence it was read from. The edit
adds a ``joined:`` line after the entry's ``status:`` line and appends the evidence as
``provenance`` entries with ``field: includes``. The dates are read from the official roster, so
the roster has been checked: ``last_verified`` is set to the manifest's ``verified_on`` date.
Nothing else changes.
"""

from __future__ import annotations

import copy
import json
import re
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

import typer
import yaml

app = typer.Typer(add_completion=False, help="Validate or apply reviewed includes[].joined dates.")

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = ROOT / "data" / "schemas" / "includes_joined_tier1.yaml"
EVIDENCE_FIELDS = ("source", "url", "retrieved_at")
DATE = re.compile(r"^\d{4}(-(0[1-9]|1[0-2])(-(0[1-9]|[12]\d|3[01]))?)?$")
TOP_KEY = re.compile(r"^[A-Za-z_][A-Za-z0-9_-]*:")


class BackfillValidationError(ValueError):
    """Raised when the manifest or repository inventory is unsafe to apply."""


@dataclass(frozen=True)
class PlannedChange:
    record_id: str
    path: str
    action: str
    dates: int = 0
    detail: str | None = None


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
    changes: list[PlannedChange] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["changes"] = [asdict(change) for change in self.changes]
        return payload


def load_manifest(path: Path) -> tuple[dict[str, dict[str, Any]], dict[str, Any]]:
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict) or not isinstance(raw.get("records"), dict) or not raw["records"]:
        raise BackfillValidationError("manifest must have a non-empty records mapping")
    expected = raw.get("expected_count")
    if not isinstance(expected, int) or expected != len(raw["records"]):
        raise BackfillValidationError(f"manifest expected_count={expected} but contains {len(raw['records'])} records")
    for record_id, entry in raw["records"].items():
        joined = entry.get("joined") if isinstance(entry, dict) else None
        if not isinstance(joined, dict) or not joined:
            raise BackfillValidationError(f"{record_id}: joined must be a non-empty mapping")
        bad = sorted(f"{k}={v!r}" for k, v in joined.items() if not (isinstance(v, str) and DATE.match(v)))
        if bad:
            raise BackfillValidationError(f"{record_id}: joined values must be quoted YYYY[-MM[-DD]] strings: {bad}")
        evidence = entry.get("evidence")
        if not isinstance(evidence, list) or not evidence:
            raise BackfillValidationError(f"{record_id}: evidence must be a non-empty list")
        for item in evidence:
            missing = [k for k in EVIDENCE_FIELDS if not (isinstance(item, dict) and item.get(k))]
            if missing:
                raise BackfillValidationError(f"{record_id}: evidence is missing fields: {missing}")
    return raw["records"], raw


def _targets(record: dict[str, Any], joined: dict[str, str]) -> tuple[dict[int, str], int, list[str]]:
    """Map include indices to the date they need; count entries already set; list conflicts."""
    includes = [inc for inc in record.get("includes") or [] if isinstance(inc, dict)]
    targets: dict[int, str] = {}
    already = 0
    conflicts: list[str] = []
    for include_id, value in joined.items():
        matches = [i for i, inc in enumerate(includes) if str(inc.get("id")) == str(include_id)]
        if not matches:
            raise BackfillValidationError(f"manifest id {include_id} is not in includes")
        set_values = {str(includes[i]["joined"]) for i in matches if includes[i].get("joined")}
        open_slots = [i for i in matches if not includes[i].get("joined")]
        if value in set_values and not open_slots:
            already += 1
        elif set_values and not open_slots:
            conflicts.append(f"{include_id}={sorted(set_values)}")
        elif len(open_slots) > 1:
            raise BackfillValidationError(f"{include_id} has {len(open_slots)} undated includes entries; edit by hand")
        else:
            targets[open_slots[0]] = value
    return targets, already, conflicts


def _edit_text(text: str, targets: dict[int, str], evidence: list[dict[str, Any]], known_urls: set[str]) -> str:
    out: list[str] = []
    section: str | None = None
    index = -1
    for line in text.splitlines(keepends=True):
        if TOP_KEY.match(line):
            section = line.split(":", 1)[0]
        elif section == "includes" and line.startswith("- "):
            index += 1
        out.append(line)
        if section == "includes" and index in targets and re.match(r"^  status:", line):
            out.append(f"  joined: '{targets[index]}'\n")
    text = "".join(out)

    new_evidence = [e for e in evidence if str(e["url"]) not in known_urls]
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


def reconcile(text: str, entry: dict[str, Any], verified_on: str | None = None) -> tuple[str, PlannedChange]:
    record = yaml.safe_load(text)
    if not isinstance(record, dict):
        raise BackfillValidationError("intblock YAML must contain a mapping")
    joined = {str(k): str(v) for k, v in entry["joined"].items()}
    targets, already, conflicts = _targets(record, joined)
    rid = str(record.get("id"))
    if conflicts:
        return text, PlannedChange(rid, "", "conflict", detail=",".join(conflicts))
    known_urls = {
        str(p.get("url")) for p in record.get("provenance") or []
        if isinstance(p, dict) and p.get("field") == "includes" and p.get("url")
    }
    evidence = list(entry["evidence"])
    if not targets and all(str(e["url"]) in known_urls for e in evidence):
        return text, PlannedChange(rid, "", "already_set", dates=already)

    updated = _edit_text(text, targets, evidence, known_urls)
    if verified_on and targets:
        updated = _set_last_verified(updated, verified_on)
    parsed = yaml.safe_load(updated)
    expected = copy.deepcopy(record)
    if verified_on and targets:
        expected["last_verified"] = verified_on
    for index, value in targets.items():
        expected["includes"][index]["joined"] = value
    if {k: v for k, v in parsed.items() if k != "provenance"} != {k: v for k, v in expected.items() if k != "provenance"}:
        raise BackfillValidationError("surgical edit changed more than includes[].joined")
    added = [p for p in parsed.get("provenance") or [] if p not in (record.get("provenance") or [])]
    if len(parsed.get("provenance") or []) != len(record.get("provenance") or []) + len(added):
        raise BackfillValidationError("surgical edit removed provenance entries")
    return updated, PlannedChange(rid, "", "pending", dates=len(targets))


def discover_records(root: Path) -> dict[str, Path]:
    records: dict[str, Path] = {}
    for path in sorted((root / "data" / "intblocks").glob("*/*.yaml")):
        record = yaml.safe_load(path.read_text(encoding="utf-8"))
        if isinstance(record, dict) and record.get("id"):
            if str(record["id"]) in records:
                raise BackfillValidationError(f"duplicate intblock id {record['id']}")
            records[str(record["id"])] = path
    return records


def execute_backfill(root: Path, manifest_path: Path, *, mode: str) -> BackfillReport:
    if mode not in {"dry-run", "check", "apply"}:
        raise BackfillValidationError(f"unknown mode: {mode}")
    entries, metadata = load_manifest(manifest_path)
    verified_on = None if metadata.get("verified_on") is None else str(metadata["verified_on"])
    records = discover_records(root)
    missing = sorted(set(entries) - set(records))
    if missing:
        raise BackfillValidationError(f"manifest ids missing from repository: {missing}")
    changes: list[PlannedChange] = []
    updated: dict[Path, str] = {}
    for record_id in sorted(entries):
        path = records[record_id]
        try:
            text, change = reconcile(path.read_text(encoding="utf-8"), entries[record_id], verified_on)
        except BackfillValidationError as exc:
            raise BackfillValidationError(f"{record_id}: {exc}") from exc
        changes.append(PlannedChange(record_id, str(path.relative_to(root)), change.action, change.dates, change.detail))
        if change.action == "pending":
            updated[path] = text
    conflicts = [c for c in changes if c.action == "conflict"]
    if conflicts and mode == "apply":
        raise BackfillValidationError(f"refusing partial apply because conflicting dates exist: {[c.record_id for c in conflicts]}")
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
    manifest: Path = typer.Option(DEFAULT_MANIFEST, help="Reviewed includes-joined manifest."),
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
    for change in report.changes:
        if change.action != "already_set":
            typer.echo(f"  {change.record_id}: {change.action} dates={change.dates}"
                       + (f" {change.detail}" if change.detail else ""))
    if report_json is not None:
        report_json.parent.mkdir(parents=True, exist_ok=True)
        report_json.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if report.conflicts:
        raise typer.Exit(code=2)
    if mode == "check" and report.pending:
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
