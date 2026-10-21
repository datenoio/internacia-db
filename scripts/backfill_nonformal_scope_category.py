#!/usr/bin/env python3
"""Stage 30 non-formal scope decisions without silently approving candidates.

The default dry-run reports every assignment. ``--apply`` writes *none* of the
records until all 30 manifest entries have record-specific evidence and are
marked ``source_reviewed``. It never reclassifies formal intblocks, invents
country membership, or regenerates datasets.
"""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import asdict, dataclass
from datetime import date
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import typer
import yaml
from backfill_scope_category import (
    VALID_CATEGORIES,
    BackfillValidationError,
    discover_records,
    reconcile_text,
)

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = ROOT / "data/schemas/scope_category_nonformal_30.yaml"
VALID_STATUSES = {"informal", "de-facto", "historical"}
VALID_REVIEW_STATES = {"source_reviewed", "pending_review"}
ID_PATTERN = re.compile(r"^[A-Z0-9_-]+$")
DIGEST_PATTERN = re.compile(r"^[0-9a-f]{64}$")
app = typer.Typer(add_completion=False, help="Preview or safely apply the 30 non-formal scope decisions.")


@dataclass(frozen=True)
class Decision:
    """One manifest decision, reviewed or awaiting evidence."""

    record_id: str
    path: str
    category: str
    expected_status: str
    source_sha256: str
    review_state: str
    evidence: dict[str, str] | None


@dataclass(frozen=True)
class PlannedChange:
    """One source file's proposed update, block, or conflict."""

    record_id: str
    path: str
    category: str
    review_state: str
    action: str
    reason: str = ""


@dataclass
class Report:
    """Machine-readable dry-run/check/apply result."""

    mode: str
    manifest: str
    expected_count: int
    assignments: int
    ready: int
    blocked: int
    pending: int
    already_set: int
    conflicts: int
    applied: int
    changes: list[PlannedChange]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _evidence(value: Any, record_id: str) -> dict[str, str] | None:
    if value is None:
        return None
    if not isinstance(value, dict):
        raise BackfillValidationError(f"{record_id}: evidence must be a mapping")
    required = {"source", "url", "retrieved_at"}
    if not required.issubset(value) or not all(isinstance(value[k], str) and value[k].strip() for k in required):
        raise BackfillValidationError(f"{record_id}: evidence requires source, url, retrieved_at")
    parsed = urlparse(value["url"])
    if parsed.scheme != "https" or not parsed.netloc:
        raise BackfillValidationError(f"{record_id}: evidence url must be HTTPS")
    try:
        date.fromisoformat(value["retrieved_at"])
    except ValueError as exc:
        raise BackfillValidationError(f"{record_id}: invalid evidence retrieved_at") from exc
    return {key: value[key] for key in required}


def load_manifest(path: Path) -> list[Decision]:
    """Validate all manifest entries before touching the repository."""
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict) or type(raw.get("version")) is not int or raw["version"] != 1:
        raise BackfillValidationError("manifest requires version: 1")
    if raw.get("cohort_id") != "nonformal_candidates_30":
        raise BackfillValidationError("unexpected cohort_id")
    entries = raw.get("records")
    if not isinstance(entries, dict) or not entries:
        raise BackfillValidationError("manifest records must be a non-empty ID mapping")
    expected_count = raw.get("expected_count")
    if type(expected_count) is not int or expected_count != len(entries):
        raise BackfillValidationError("expected_count does not match manifest records")
    if path.resolve() == DEFAULT_MANIFEST.resolve() and expected_count != 30:
        raise BackfillValidationError("default non-formal cohort must contain exactly 30 records")

    decisions = []
    for record_id, entry in entries.items():
        if not isinstance(record_id, str) or not ID_PATTERN.fullmatch(record_id):
            raise BackfillValidationError(f"invalid record id: {record_id!r}")
        if not isinstance(entry, dict):
            raise BackfillValidationError(f"{record_id}: record decision must be a mapping")
        category, status = entry.get("category"), entry.get("expected_status")
        if category not in VALID_CATEGORIES or status not in VALID_STATUSES:
            raise BackfillValidationError(f"{record_id}: invalid category or non-formal status")
        relpath = entry.get("path")
        if (
            not isinstance(relpath, str)
            or Path(relpath).is_absolute()
            or ".." in Path(relpath).parts
            or not re.fullmatch(r"data/intblocks/[^/]+/" + re.escape(record_id) + r"\.yaml", relpath)
        ):
            raise BackfillValidationError(f"{record_id}: unsafe or mismatching source path")
        digest = entry.get("source_sha256")
        if not isinstance(digest, str) or not DIGEST_PATTERN.fullmatch(digest):
            raise BackfillValidationError(f"{record_id}: source_sha256 must be a 64-character hex digest")
        review = entry.get("review_state")
        if review not in VALID_REVIEW_STATES:
            raise BackfillValidationError(f"{record_id}: invalid review_state")
        evidence = _evidence(entry.get("evidence"), record_id)
        if review == "source_reviewed" and evidence is None:
            raise BackfillValidationError(f"{record_id}: reviewed assignment needs record-specific evidence")
        decisions.append(Decision(record_id, relpath, category, status, digest, review, evidence))
    return sorted(decisions, key=lambda decision: decision.record_id)


def _preserved_fields(before: dict[str, Any], after: dict[str, Any], record_id: str) -> None:
    """Prevent a surgical edit from silently changing unrelated YAML fields."""
    old = dict(before)
    new = dict(after)
    old.pop("scope_category", None)
    new.pop("scope_category", None)
    old_prov = old.pop("provenance", []) or []
    new_prov = new.pop("provenance", []) or []
    if old != new:
        raise BackfillValidationError(f"{record_id}: edit changed fields other than scope_category")
    if [p for p in new_prov if p.get("field") != "scope_category"] != [
        p for p in old_prov if p.get("field") != "scope_category"
    ]:
        raise BackfillValidationError(f"{record_id}: edit changed unrelated provenance")


def plan_backfill(root: Path, manifest: Path) -> tuple[list[PlannedChange], dict[Path, str]]:
    """Preflight all 30 records, including unreviewed and already-applied ones."""
    root = root.resolve()
    decisions = load_manifest(manifest)
    inventory = discover_records(root)
    missing = sorted({d.record_id for d in decisions} - set(inventory))
    if missing:
        raise BackfillValidationError(f"manifest ids missing from source inventory: {missing}")
    changes: list[PlannedChange] = []
    edits: dict[Path, str] = {}
    for d in decisions:
        source = inventory[d.record_id]
        if source.is_symlink() or source.resolve() != (root / d.path).resolve():
            raise BackfillValidationError(f"{d.record_id}: source path moved or is a symlink")
        text = source.read_text(encoding="utf-8")
        record = yaml.safe_load(text)
        if not isinstance(record, dict) or record.get("id") != d.record_id:
            raise BackfillValidationError(f"{d.record_id}: source record ID changed")
        if record.get("status") != d.expected_status:
            raise BackfillValidationError(f"{d.record_id}: status drifted from {d.expected_status}")
        if "scope_category" in record and record["scope_category"] is None:
            raise BackfillValidationError(f"{d.record_id}: explicit null scope_category needs manual review")
        provenance = record.get("provenance") or []
        if not isinstance(provenance, list) or any(not isinstance(p, dict) for p in provenance):
            raise BackfillValidationError(f"{d.record_id}: invalid provenance entries")
        if sum(p.get("field") == "scope_category" for p in provenance) > 1:
            raise BackfillValidationError(f"{d.record_id}: invalid or duplicate scope provenance")

        current = record.get("scope_category")
        digest = hashlib.sha256(source.read_bytes()).hexdigest()
        if current is None and digest != d.source_sha256:
            changes.append(
                PlannedChange(d.record_id, d.path, d.category, d.review_state, "conflict", "source SHA-256 changed")
            )
            continue
        if current is not None and current != d.category:
            changes.append(
                PlannedChange(
                    d.record_id, d.path, d.category, d.review_state, "conflict", f"existing category: {current}"
                )
            )
            continue
        if current is not None and not any(
            p.get("field") == "scope_category" for p in provenance if isinstance(p, dict)
        ):
            changes.append(
                PlannedChange(
                    d.record_id,
                    d.path,
                    d.category,
                    d.review_state,
                    "conflict",
                    "category already set without provenance",
                )
            )
            continue

        updated, action, conflict = reconcile_text(text, d.category, d.evidence)
        if action == "conflict":
            changes.append(PlannedChange(d.record_id, d.path, d.category, d.review_state, "conflict", str(conflict)))
            continue
        if action == "pending" and current is not None:
            changes.append(
                PlannedChange(
                    d.record_id, d.path, d.category, d.review_state, "conflict", "unexpected provenance-only change"
                )
            )
            continue
        if action == "pending":
            _preserved_fields(record, yaml.safe_load(updated), d.record_id)
        if d.review_state == "pending_review":
            changes.append(
                PlannedChange(
                    d.record_id,
                    d.path,
                    d.category,
                    d.review_state,
                    "blocked",
                    "record-specific review and evidence required",
                )
            )
        else:
            changes.append(PlannedChange(d.record_id, d.path, d.category, d.review_state, action))
            if action == "pending":
                edits[source] = updated
    return changes, edits


def execute_backfill(root: Path, manifest: Path, *, mode: str) -> Report:
    """Apply only after complete preflight and review of the entire cohort."""
    if mode not in {"dry-run", "check", "apply"}:
        raise BackfillValidationError(f"unsupported mode: {mode}")
    changes, edits = plan_backfill(root, manifest)
    blocked = [change.record_id for change in changes if change.action == "blocked"]
    conflicts = [change.record_id for change in changes if change.action == "conflict"]
    if mode == "apply" and (blocked or conflicts):
        raise BackfillValidationError(f"refusing partial apply: pending review={blocked}; conflicts={conflicts}")
    if mode == "apply":
        for path, updated in edits.items():
            path.write_text(updated, encoding="utf-8")
    return Report(
        mode=mode,
        manifest=str(manifest),
        expected_count=len(changes),
        assignments=len(changes),
        ready=sum(c.action in {"pending", "already_set"} for c in changes),
        blocked=len(blocked),
        pending=sum(c.action == "pending" for c in changes),
        already_set=sum(c.action == "already_set" for c in changes),
        conflicts=len(conflicts),
        applied=len(edits) if mode == "apply" else 0,
        changes=changes,
    )


@app.command()
def main(
    root: Path = typer.Option(ROOT, help="Repository root."),
    manifest: Path = typer.Option(DEFAULT_MANIFEST, help="Curated 30-ID manifest."),
    apply: bool = typer.Option(False, "--apply", help="Apply only when all 30 are reviewed."),
    check: bool = typer.Option(False, "--check", help="Exit 1 if any assignment is pending/blocked."),
    report_json: Path | None = typer.Option(None, help="Write machine-readable report."),
) -> None:
    """Default to read-only dry-run; never apply a provisional subset."""
    if apply and check:
        typer.echo("--apply and --check are mutually exclusive", err=True)
        raise typer.Exit(code=2)
    mode = "apply" if apply else "check" if check else "dry-run"
    try:
        result = execute_backfill(root.resolve(), manifest.resolve(), mode=mode)
    except (BackfillValidationError, OSError, yaml.YAMLError) as exc:
        typer.echo(f"ERROR: {exc}", err=True)
        raise typer.Exit(code=2) from exc
    typer.echo(
        f"mode={mode} assignments={result.assignments} ready={result.ready} "
        f"blocked={result.blocked} conflicts={result.conflicts} "
        f"pending={result.pending} already_set={result.already_set} applied={result.applied}"
    )
    if report_json is not None:
        report_json.parent.mkdir(parents=True, exist_ok=True)
        report_json.write_text(json.dumps(result.to_dict(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if mode == "check" and (result.pending or result.blocked or result.conflicts):
        raise typer.Exit(code=1 if not result.conflicts else 2)


if __name__ == "__main__":
    app()
