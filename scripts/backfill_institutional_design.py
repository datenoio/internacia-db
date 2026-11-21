#!/usr/bin/env python3
"""Safely backfill reviewed ``institutional_design`` values on intblock YAML.

The default mode is a non-mutating dry run. ``--apply`` performs surgical text edits
only after the complete manifest and repository inventory pass validation. A record
that already has a different ``institutional_design`` is a conflict and blocks the
whole apply; a record that already matches is left byte-for-byte unchanged.

Values come only from the explicit, reviewed manifest
(``data/schemas/institutional_design_pilot.yaml``). Nothing is inferred from
``blocktype``, directory, or ``topics``.
"""

from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import _checkout  # noqa: F401  (this checkout's internacia_builder, not an installed one)
import jsonschema
import typer
import yaml

from internacia_builder.yaml_io import safe_load

app = typer.Typer(
    add_completion=False,
    help="Validate or apply reviewed intblock institutional_design values.",
)

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = ROOT / "data" / "schemas" / "institutional_design_pilot.yaml"
FIELD = "institutional_design"
ALLOWED_SCOPES = {"igo", "treaty_body", "policy_forum", "intergovernmental_body"}
EVIDENCE_FIELDS = ("source", "url", "retrieved_at")


class BackfillValidationError(ValueError):
    """Raised when the manifest or repository inventory is unsafe to apply."""


@dataclass(frozen=True)
class PlannedChange:
    """One reviewed record and its current state."""

    record_id: str
    path: str
    action: str
    current: str | None = None


@dataclass
class BackfillReport:
    """Machine-readable result for dry-run, check, and apply modes."""

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
        """Return a JSON-serializable report."""
        payload = asdict(self)
        payload["changes"] = [asdict(change) for change in self.changes]
        return payload


def _design_schema(root: Path) -> dict[str, Any]:
    schema = json.loads((root / "data" / "schemas" / "intblocks.schema.json").read_text(encoding="utf-8"))
    return schema["properties"][FIELD]


def load_manifest(manifest_path: Path, root: Path) -> tuple[dict[str, dict[str, Any]], dict[str, Any]]:
    """Load and validate the reviewed manifest: ``{id: {institutional_design, evidence}}``."""
    raw = safe_load(manifest_path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise BackfillValidationError("manifest must contain a YAML mapping")
    records = raw.get("records")
    if not isinstance(records, dict) or not records:
        raise BackfillValidationError("manifest records must be a non-empty mapping")

    expected_count = raw.get("expected_count")
    if not isinstance(expected_count, int) or expected_count <= 0:
        raise BackfillValidationError("manifest expected_count must be a positive integer")
    if expected_count != len(records):
        raise BackfillValidationError(
            f"manifest expected_count={expected_count} but contains {len(records)} records"
        )

    design_schema = _design_schema(root)
    validator = jsonschema.validators.validator_for(design_schema)(design_schema)
    for record_id, entry in records.items():
        if not isinstance(entry, dict):
            raise BackfillValidationError(f"{record_id}: manifest entry must be a mapping")
        design = entry.get(FIELD)
        if not isinstance(design, dict) or not design:
            raise BackfillValidationError(f"{record_id}: {FIELD} must be a non-empty mapping")
        errors = sorted(validator.iter_errors(design), key=lambda e: list(e.path))
        if errors:
            raise BackfillValidationError(f"{record_id}: {FIELD} is invalid: {errors[0].message}")
        for evidence in evidence_list(entry.get("evidence"), record_id):
            missing = [key for key in EVIDENCE_FIELDS if not evidence.get(key)]
            if missing:
                raise BackfillValidationError(f"{record_id}: evidence is missing fields: {missing}")
    return records, raw


def evidence_list(raw: Any, record_id: str) -> list[dict[str, Any]]:
    """Normalize manifest evidence (one mapping or a non-empty list of mappings) to a list."""
    items = [raw] if isinstance(raw, dict) else raw
    if not isinstance(items, list) or not items or not all(isinstance(e, dict) for e in items):
        raise BackfillValidationError(f"{record_id}: evidence must be a mapping or a non-empty list of mappings")
    return items


def _ordered_design(design: dict[str, Any], root: Path) -> dict[str, Any]:
    """Subfields in JSON Schema order, so every record serializes the same way."""
    order = list(_design_schema(root)["properties"])
    return {key: design[key] for key in order if key in design}


def _format_design_block(design: dict[str, Any]) -> str:
    return yaml.safe_dump(
        {FIELD: design}, allow_unicode=True, default_flow_style=False, sort_keys=False
    )


def _format_provenance_entry(evidence: dict[str, Any]) -> str:
    lines = [
        f"- field: {FIELD}",
        f"  source: {json.dumps(str(evidence['source']), ensure_ascii=False)}",
        f"  retrieved_at: {json.dumps(str(evidence['retrieved_at']))}",
        f"  url: {json.dumps(str(evidence['url']), ensure_ascii=False)}",
    ]
    if evidence.get("license"):
        lines.append(f"  license: {json.dumps(str(evidence['license']), ensure_ascii=False)}")
    return "\n".join(lines) + "\n"


def _insert_provenance(text: str, evidence: list[dict[str, Any]]) -> str:
    """Prepend provenance items to the top-level list, or start the list."""
    entry = "".join(_format_provenance_entry(item) for item in evidence)
    match = re.search(r"^provenance:[ \t]*\n", text, flags=re.MULTILINE)
    if match is None and re.search(r"^provenance:", text, flags=re.MULTILINE):
        raise BackfillValidationError("provenance is not a block list; edit the record by hand")
    if match is None:
        separator = "" if text.endswith("\n") else "\n"
        return text + separator + "provenance:\n" + entry
    return text[: match.end()] + entry + text[match.end() :]


def _source_key(entry: dict[str, Any]) -> tuple[str, ...]:
    return tuple(str(entry.get(key, "")) for key in EVIDENCE_FIELDS)


def reconcile_text(
    text: str,
    design: dict[str, Any],
    evidence: list[dict[str, Any]],
) -> tuple[str, str, str | None]:
    """Return updated text, the action, and any conflicting current value."""
    record = safe_load(text)
    if not isinstance(record, dict):
        raise BackfillValidationError("intblock YAML must contain a mapping")

    current = record.get(FIELD)
    if current is not None and current != design:
        return text, "conflict", json.dumps(current, sort_keys=True)

    design_provenance = [
        entry
        for entry in (record.get("provenance") or [])
        if isinstance(entry, dict) and str(entry.get("field") or "") == FIELD
    ]
    if design_provenance and sorted(map(_source_key, design_provenance)) != sorted(map(_source_key, evidence)):
        return text, "conflict", f"{FIELD} provenance differs"

    if current == design and design_provenance:
        return text, "already_set", None

    updated = text
    if current is None:
        anchor = re.search(r"^scope_category:[^\n]*\n", updated, flags=re.MULTILINE)
        if anchor is None:
            raise BackfillValidationError("cannot find scope_category anchor for surgical edit")
        updated = updated[: anchor.end()] + _format_design_block(design) + updated[anchor.end() :]
    if not design_provenance:
        updated = _insert_provenance(updated, evidence)

    parsed = safe_load(updated)
    if not isinstance(parsed, dict) or parsed.get(FIELD) != design:
        raise BackfillValidationError(f"surgical {FIELD} insertion failed validation")
    stripped = {k: v for k, v in parsed.items() if k not in (FIELD, "provenance")}
    original = {k: v for k, v in record.items() if k not in (FIELD, "provenance")}
    if stripped != original:
        raise BackfillValidationError(f"surgical {FIELD} insertion changed another field")
    if len([e for e in parsed.get("provenance") or [] if isinstance(e, dict) and e.get("field") == FIELD]) != len(evidence):
        raise BackfillValidationError(f"{FIELD} provenance insertion failed validation")
    return updated, "pending", None


def discover_records(root: Path) -> dict[str, Path]:
    """Index all intblock source files and reject duplicate ids."""
    records: dict[str, Path] = {}
    for path in sorted((root / "data" / "intblocks").glob("*/*.yaml")):
        record = safe_load(path.read_text(encoding="utf-8"))
        if not isinstance(record, dict) or not record.get("id"):
            continue
        record_id = str(record["id"])
        if record_id in records:
            raise BackfillValidationError(f"duplicate intblock id {record_id}: {records[record_id]} and {path}")
        records[record_id] = path
    return records


def plan_backfill(root: Path, manifest_path: Path) -> tuple[list[PlannedChange], dict[Path, str], dict[str, Any]]:
    """Validate the whole cohort and prepare every edit without writing files."""
    entries, metadata = load_manifest(manifest_path, root)
    records = discover_records(root)
    missing_ids = sorted(set(entries) - set(records))
    if missing_ids:
        raise BackfillValidationError(f"manifest ids missing from repository: {missing_ids}")

    changes: list[PlannedChange] = []
    updated_text: dict[Path, str] = {}
    for record_id in sorted(entries):
        path = records[record_id]
        text = path.read_text(encoding="utf-8")
        record = safe_load(text)
        category = record.get("scope_category")
        if category not in ALLOWED_SCOPES:
            raise BackfillValidationError(
                f"{record_id} has scope_category={category!r}; {FIELD} needs one of {sorted(ALLOWED_SCOPES)}"
            )
        design = _ordered_design(entries[record_id][FIELD], root)
        evidence = evidence_list(entries[record_id]["evidence"], record_id)
        updated, action, current = reconcile_text(text, design, evidence)
        changes.append(PlannedChange(record_id, str(path.relative_to(root)), action, current))
        if action == "pending":
            updated_text[path] = updated
    return changes, updated_text, metadata


def execute_backfill(root: Path, manifest_path: Path, *, mode: str) -> BackfillReport:
    """Plan the cohort and, in apply mode, write every edit only if nothing conflicts."""
    if mode not in {"dry-run", "check", "apply"}:
        raise BackfillValidationError(f"unknown mode: {mode}")
    changes, updated_text, metadata = plan_backfill(root, manifest_path)
    conflicts = [change for change in changes if change.action == "conflict"]
    if conflicts and mode == "apply":
        raise BackfillValidationError(
            f"refusing partial apply because conflicting values exist: {[c.record_id for c in conflicts]}"
        )
    applied = 0
    if mode == "apply":
        for path, text in updated_text.items():
            path.write_text(text, encoding="utf-8")
            applied += 1
    return BackfillReport(
        mode=mode,
        manifest=str(manifest_path),
        expected_count=int(metadata["expected_count"]),
        records=len(changes),
        pending=sum(change.action == "pending" for change in changes),
        already_set=sum(change.action == "already_set" for change in changes),
        conflicts=len(conflicts),
        applied=applied,
        changes=changes,
    )


@app.command()
def main(
    root: Path = typer.Option(ROOT, help="Repository root containing data/intblocks."),
    manifest: Path = typer.Option(DEFAULT_MANIFEST, help="Reviewed institutional_design manifest."),
    apply: bool = typer.Option(False, "--apply", help="Write all pending records after complete validation."),
    check: bool = typer.Option(False, "--check", help="Exit non-zero when pending records remain; never write."),
    report_json: Path | None = typer.Option(None, help="Optional path for a machine-readable report."),
) -> None:
    """Dry-run by default."""
    if apply and check:
        typer.echo("--apply and --check are mutually exclusive", err=True)
        raise typer.Exit(code=2)
    mode = "apply" if apply else "check" if check else "dry-run"
    root = root.resolve()
    manifest = manifest.resolve()
    try:
        report = execute_backfill(root, manifest, mode=mode)
    except (BackfillValidationError, OSError, yaml.YAMLError) as exc:
        typer.echo(f"ERROR: {exc}", err=True)
        raise typer.Exit(code=2) from exc

    payload = report.to_dict()
    typer.echo(
        "mode={mode} records={records} pending={pending} already_set={already_set} "
        "conflicts={conflicts} applied={applied}".format(**payload)
    )
    if report_json is not None:
        report_json = report_json.resolve()
        report_json.parent.mkdir(parents=True, exist_ok=True)
        report_json.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if report.conflicts:
        raise typer.Exit(code=2)
    if mode == "check" and report.pending:
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
