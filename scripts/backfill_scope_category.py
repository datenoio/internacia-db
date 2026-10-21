#!/usr/bin/env python3
"""Safely backfill reviewed ``scope_category`` assignments on intblock YAML.

The default mode is a non-mutating dry run. ``--apply`` performs surgical text
edits only after the complete manifest and repository inventory pass validation.
Existing, different values are conflicts and are never overwritten.
"""

from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import typer
import yaml

app = typer.Typer(
    add_completion=False,
    help="Validate or apply reviewed intblock scope_category assignments.",
)

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = ROOT / "data" / "schemas" / "scope_category_backfill.yaml"
VALID_CATEGORIES = {
    "igo",
    "treaty_body",
    "policy_forum",
    "reference_enumeration",
    "intergovernmental_body",
    "non_state_organization",
}


class BackfillValidationError(ValueError):
    """Raised when the manifest or repository inventory is unsafe to apply."""


@dataclass(frozen=True)
class PlannedChange:
    """One reviewed assignment and its current state."""

    record_id: str
    category: str
    path: str
    action: str
    current: str | None = None


@dataclass
class BackfillReport:
    """Machine-readable result for dry-run, check, and apply modes."""

    mode: str
    manifest: str
    expected_count: int
    assignments: int
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


def load_assignments(manifest_path: Path) -> tuple[dict[str, str], dict[str, Any]]:
    """Load and validate the explicit ID-to-category manifest."""
    raw = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise BackfillValidationError("manifest must contain a YAML mapping")

    categories = raw.get("categories")
    if not isinstance(categories, dict) or not categories:
        raise BackfillValidationError("manifest categories must be a non-empty mapping")

    assignments: dict[str, str] = {}
    for category, record_ids in categories.items():
        category = str(category)
        if category not in VALID_CATEGORIES:
            raise BackfillValidationError(f"unknown scope category in manifest: {category}")
        if not isinstance(record_ids, list):
            raise BackfillValidationError(f"category {category} must contain a list of ids")
        for raw_id in record_ids:
            record_id = str(raw_id)
            if record_id in assignments:
                raise BackfillValidationError(f"duplicate manifest id: {record_id}")
            assignments[record_id] = category

    expected_count = raw.get("expected_count")
    if not isinstance(expected_count, int) or expected_count <= 0:
        raise BackfillValidationError("manifest expected_count must be a positive integer")
    if expected_count != len(assignments):
        raise BackfillValidationError(
            f"manifest expected_count={expected_count} but contains {len(assignments)} assignments"
        )

    evidence = raw.get("evidence") or {}
    if not isinstance(evidence, dict):
        raise BackfillValidationError("manifest evidence must be a mapping")
    unknown_evidence = sorted(set(evidence) - set(assignments))
    if unknown_evidence:
        raise BackfillValidationError(
            f"manifest evidence references unknown assignment ids: {unknown_evidence}"
        )
    required_fields = {"source", "url", "retrieved_at"}
    for record_id, entry in evidence.items():
        if not isinstance(entry, dict):
            raise BackfillValidationError(f"evidence for {record_id} must be a mapping")
        missing_fields = sorted(required_fields - set(entry))
        if missing_fields:
            raise BackfillValidationError(
                f"evidence for {record_id} is missing fields: {missing_fields}"
            )
    if raw.get("require_evidence") is True:
        missing_evidence = sorted(set(assignments) - set(evidence))
        if missing_evidence:
            raise BackfillValidationError(
                f"manifest requires evidence for every assignment; missing: {missing_evidence}"
            )
    return assignments, raw


def _format_provenance_entry(evidence: dict[str, Any]) -> str:
    """Format one YAML-list provenance entry with safely quoted scalar values."""
    lines = [
        "- field: scope_category",
        f"  source: {json.dumps(str(evidence['source']), ensure_ascii=False)}",
        f"  retrieved_at: {json.dumps(str(evidence['retrieved_at']))}",
        f"  url: {json.dumps(str(evidence['url']), ensure_ascii=False)}",
    ]
    if evidence.get("license"):
        lines.append(f"  license: {json.dumps(str(evidence['license']), ensure_ascii=False)}")
    return "\n".join(lines) + "\n"


def _insert_scope_provenance(text: str, evidence: dict[str, Any]) -> str:
    """Insert a scope_category provenance item without reserializing the record."""
    entry = _format_provenance_entry(evidence)
    match = re.search(r"^provenance:\s*$", text, flags=re.MULTILINE)
    if match is None:
        separator = "" if text.endswith("\n") else "\n"
        return text + separator + "provenance:\n" + entry

    next_key = re.search(
        r"^[A-Za-z_][A-Za-z0-9_-]*:\s*.*$",
        text[match.end() :],
        flags=re.MULTILINE,
    )
    if next_key is None:
        separator = "" if text.endswith("\n") else "\n"
        return text + separator + entry

    insert_at = match.end() + next_key.start()
    return text[:insert_at] + entry + text[insert_at:]


def reconcile_text(
    text: str,
    target: str,
    evidence: dict[str, Any] | None = None,
) -> tuple[str, str, str | None]:
    """Return updated text, action, and any conflicting current value."""
    record = yaml.safe_load(text)
    if not isinstance(record, dict):
        raise BackfillValidationError("intblock YAML must contain a mapping")

    current = record.get("scope_category")
    if current is not None:
        current_text = str(current)
        if current_text != target:
            return text, "conflict", current_text

    scope_provenance = [
        entry
        for entry in (record.get("provenance") or [])
        if isinstance(entry, dict) and entry.get("field") == "scope_category"
    ]
    if evidence and scope_provenance:
        existing = scope_provenance[0]
        comparable = ("source", "url", "retrieved_at")
        if any(str(existing.get(key, "")) != str(evidence.get(key, "")) for key in comparable):
            return text, "conflict", "scope_category provenance differs"

    updated = text
    changed = False
    if current is None:
        anchor = re.search(r"^(status:\s*[^\n]+)$", updated, flags=re.MULTILINE)
        if anchor is None:
            anchor = re.search(r"^(id:\s*[^\n]+)$", updated, flags=re.MULTILINE)
        if anchor is None:
            raise BackfillValidationError("cannot find status or id anchor for surgical edit")
        updated = updated[: anchor.end()] + f"\nscope_category: {target}" + updated[anchor.end() :]
        changed = True

    if evidence and not scope_provenance:
        updated = _insert_scope_provenance(updated, evidence)
        changed = True

    parsed = yaml.safe_load(updated)
    if not isinstance(parsed, dict) or parsed.get("scope_category") != target:
        raise BackfillValidationError("surgical scope_category insertion failed validation")
    if evidence:
        parsed_scope_provenance = [
            entry
            for entry in (parsed.get("provenance") or [])
            if isinstance(entry, dict) and entry.get("field") == "scope_category"
        ]
        if len(parsed_scope_provenance) != 1:
            raise BackfillValidationError("scope_category provenance insertion failed validation")
    return updated, "pending" if changed else "already_set", None


def discover_records(root: Path) -> dict[str, Path]:
    """Index all intblock source files and reject duplicate ids."""
    records: dict[str, Path] = {}
    for path in sorted((root / "data" / "intblocks").glob("*/*.yaml")):
        record = yaml.safe_load(path.read_text(encoding="utf-8"))
        if not isinstance(record, dict) or not record.get("id"):
            continue
        record_id = str(record["id"])
        if record_id in records:
            raise BackfillValidationError(
                f"duplicate intblock id {record_id}: {records[record_id]} and {path}"
            )
        records[record_id] = path
    return records


def plan_backfill(
    root: Path,
    manifest_path: Path,
) -> tuple[list[PlannedChange], dict[Path, str], dict[str, Any]]:
    """Validate the full cohort and prepare all edits without writing files."""
    assignments, metadata = load_assignments(manifest_path)
    records = discover_records(root)
    missing_ids = sorted(set(assignments) - set(records))
    if missing_ids:
        raise BackfillValidationError(f"manifest ids missing from repository: {missing_ids}")

    changes: list[PlannedChange] = []
    updated_text: dict[Path, str] = {}
    evidence = metadata.get("evidence") or {}
    for record_id, category in sorted(assignments.items()):
        path = records[record_id]
        text = path.read_text(encoding="utf-8")
        record = yaml.safe_load(text)
        if record.get("status") != "formal":
            raise BackfillValidationError(
                f"{record_id} has status={record.get('status')!r}; direct cohort requires formal"
            )
        updated, action, current = reconcile_text(text, category, evidence.get(record_id))
        changes.append(
            PlannedChange(
                record_id=record_id,
                category=category,
                path=str(path.relative_to(root)),
                action=action,
                current=current,
            )
        )
        if action == "pending":
            updated_text[path] = updated

    return changes, updated_text, metadata


def execute_backfill(
    root: Path,
    manifest_path: Path,
    *,
    mode: str,
) -> BackfillReport:
    """Plan the cohort and optionally apply all safe edits atomically by policy."""
    if mode not in {"dry-run", "check", "apply"}:
        raise BackfillValidationError(f"unknown mode: {mode}")

    changes, updated_text, metadata = plan_backfill(root, manifest_path)
    conflicts = [change for change in changes if change.action == "conflict"]
    if conflicts and mode == "apply":
        conflict_ids = [change.record_id for change in conflicts]
        raise BackfillValidationError(
            f"refusing partial apply because conflicting values exist: {conflict_ids}"
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
        assignments=len(changes),
        pending=sum(change.action == "pending" for change in changes),
        already_set=sum(change.action == "already_set" for change in changes),
        conflicts=len(conflicts),
        applied=applied,
        changes=changes,
    )


def write_json_report(report: BackfillReport, output: Path) -> None:
    """Write the complete machine-readable plan or result."""
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(report.to_dict(), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def print_summary(report: BackfillReport) -> None:
    """Print a compact human-readable summary."""
    typer.echo(
        "mode={mode} assignments={assignments} pending={pending} "
        "already_set={already_set} conflicts={conflicts} applied={applied}".format(
            **report.to_dict()
        )
    )
    by_category: dict[str, int] = {}
    for change in report.changes:
        by_category[change.category] = by_category.get(change.category, 0) + 1
    typer.echo(
        "categories="
        + ", ".join(f"{category}:{count}" for category, count in sorted(by_category.items()))
    )


@app.command()
def main(
    root: Path = typer.Option(ROOT, help="Repository root containing data/intblocks."),
    manifest: Path = typer.Option(
        DEFAULT_MANIFEST,
        help="Reviewed ID-to-scope_category manifest.",
    ),
    apply: bool = typer.Option(
        False,
        "--apply",
        help="Write all pending assignments after complete validation.",
    ),
    check: bool = typer.Option(
        False,
        "--check",
        help="Exit non-zero when pending assignments remain; never write.",
    ),
    report_json: Path | None = typer.Option(
        None,
        help="Optional path for a machine-readable report.",
    ),
) -> None:
    """Dry-run by default; use --apply only after OpenSpec approval."""
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

    print_summary(report)
    if report_json is not None:
        write_json_report(report, report_json.resolve())

    if report.conflicts:
        raise typer.Exit(code=2)
    if mode == "check" and report.pending:
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
