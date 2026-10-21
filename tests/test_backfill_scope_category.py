"""Tests for the reviewed intblock scope-category backfill."""

from pathlib import Path

import backfill_scope_category as backfill
import pytest
import yaml


def _write_record(root: Path, record_id: str, scope_category: str | None = None) -> Path:
    path = root / "data" / "intblocks" / "economic" / f"{record_id}.yaml"
    path.parent.mkdir(parents=True, exist_ok=True)
    scope_line = f"scope_category: {scope_category}\n" if scope_category else ""
    path.write_text(
        f"id: {record_id}\nstatus: formal\n{scope_line}name: Example {record_id}\n",
        encoding="utf-8",
    )
    return path


def _write_manifest(
    root: Path,
    categories: dict[str, list[str]],
    *,
    evidence: dict | None = None,
    require_evidence: bool = False,
) -> Path:
    path = root / "manifest.yaml"
    count = sum(len(ids) for ids in categories.values())
    payload = {
        "version": 1,
        "change_id": "complete-intblock-scope-taxonomy",
        "cohort_id": "test",
        "expected_count": count,
        "categories": categories,
    }
    if evidence is not None:
        payload["evidence"] = evidence
    if require_evidence:
        payload["require_evidence"] = True
    path.write_text(
        yaml.safe_dump(payload, sort_keys=False),
        encoding="utf-8",
    )
    return path


def test_reviewed_manifest_has_expected_81_assignments():
    assignments, metadata = backfill.load_assignments(backfill.DEFAULT_MANIFEST)

    assert metadata["change_id"] == "complete-intblock-scope-taxonomy"
    assert len(assignments) == 81
    assert list(assignments.values()).count("igo") == 55
    assert list(assignments.values()).count("treaty_body") == 13
    assert list(assignments.values()).count("policy_forum") == 7
    assert list(assignments.values()).count("reference_enumeration") == 6


def test_reconcile_inserts_after_status_without_reserializing_yaml():
    text = "id: EXAMPLE\nstatus: formal\nname: Example\nincludes:\n- id: AA\n"

    updated, action, conflict = backfill.reconcile_text(text, "igo")

    assert updated == (
        "id: EXAMPLE\nstatus: formal\nscope_category: igo\n"
        "name: Example\nincludes:\n- id: AA\n"
    )
    assert action == "pending"
    assert conflict is None


def test_reconcile_is_idempotent_for_matching_value():
    text = "id: EXAMPLE\nstatus: formal\nscope_category: igo\nname: Example\n"

    updated, action, conflict = backfill.reconcile_text(text, "igo")

    assert updated == text
    assert action == "already_set"
    assert conflict is None


def test_reconcile_reports_different_existing_value_as_conflict():
    text = "id: EXAMPLE\nstatus: formal\nscope_category: policy_forum\nname: Example\n"

    updated, action, conflict = backfill.reconcile_text(text, "igo")

    assert updated == text
    assert action == "conflict"
    assert conflict == "policy_forum"


def test_reconcile_adds_scope_provenance_before_following_top_level_key():
    text = """id: EXAMPLE
status: formal
name: Example
provenance:
- field: name
  source: Existing source
  retrieved_at: '2026-01-01'
acronyms:
- lang: en
  value: EX
"""
    evidence = {
        "source": "Official charter",
        "url": "https://example.test/charter",
        "retrieved_at": "2026-09-30",
    }

    updated, action, conflict = backfill.reconcile_text(text, "igo", evidence)
    record = yaml.safe_load(updated)

    assert action == "pending"
    assert conflict is None
    assert record["scope_category"] == "igo"
    assert record["provenance"][-1] == {"field": "scope_category", **evidence}
    assert updated.index("- field: scope_category") < updated.index("acronyms:")


def test_reconcile_with_matching_scope_provenance_is_idempotent():
    evidence = {
        "source": "Official charter",
        "url": "https://example.test/charter",
        "retrieved_at": "2026-09-30",
    }
    text = """id: EXAMPLE
status: formal
scope_category: igo
name: Example
provenance:
- field: scope_category
  source: Official charter
  retrieved_at: '2026-09-30'
  url: https://example.test/charter
"""

    updated, action, conflict = backfill.reconcile_text(text, "igo", evidence)

    assert updated == text
    assert action == "already_set"
    assert conflict is None


def test_reconcile_rejects_different_scope_provenance():
    evidence = {
        "source": "New source",
        "url": "https://example.test/new",
        "retrieved_at": "2026-09-30",
    }
    text = """id: EXAMPLE
status: formal
scope_category: igo
provenance:
- field: scope_category
  source: Old source
  retrieved_at: '2026-01-01'
  url: https://example.test/old
"""

    updated, action, conflict = backfill.reconcile_text(text, "igo", evidence)

    assert updated == text
    assert action == "conflict"
    assert conflict == "scope_category provenance differs"


def test_dry_run_reports_pending_without_writing(tmp_path: Path):
    record = _write_record(tmp_path, "EXAMPLE")
    manifest = _write_manifest(tmp_path, {"igo": ["EXAMPLE"]})
    original = record.read_text(encoding="utf-8")

    report = backfill.execute_backfill(tmp_path, manifest, mode="dry-run")

    assert report.pending == 1
    assert report.applied == 0
    assert record.read_text(encoding="utf-8") == original


def test_apply_is_idempotent(tmp_path: Path):
    record = _write_record(tmp_path, "EXAMPLE")
    manifest = _write_manifest(tmp_path, {"igo": ["EXAMPLE"]})

    first = backfill.execute_backfill(tmp_path, manifest, mode="apply")
    second = backfill.execute_backfill(tmp_path, manifest, mode="apply")

    assert first.applied == 1
    assert second.applied == 0
    assert second.already_set == 1
    assert yaml.safe_load(record.read_text(encoding="utf-8"))["scope_category"] == "igo"


def test_apply_refuses_all_writes_when_any_conflict_exists(tmp_path: Path):
    pending = _write_record(tmp_path, "PENDING")
    _write_record(tmp_path, "CONFLICT", scope_category="policy_forum")
    manifest = _write_manifest(tmp_path, {"igo": ["PENDING", "CONFLICT"]})
    original = pending.read_text(encoding="utf-8")

    with pytest.raises(backfill.BackfillValidationError, match="refusing partial apply"):
        backfill.execute_backfill(tmp_path, manifest, mode="apply")

    assert pending.read_text(encoding="utf-8") == original


def test_manifest_missing_repository_id_is_rejected(tmp_path: Path):
    manifest = _write_manifest(tmp_path, {"igo": ["MISSING"]})
    (tmp_path / "data" / "intblocks").mkdir(parents=True)

    with pytest.raises(backfill.BackfillValidationError, match="missing from repository"):
        backfill.plan_backfill(tmp_path, manifest)


def test_manifest_can_require_evidence_for_every_assignment(tmp_path: Path):
    manifest = _write_manifest(
        tmp_path,
        {"igo": ["EXAMPLE"]},
        evidence={},
        require_evidence=True,
    )

    with pytest.raises(backfill.BackfillValidationError, match="requires evidence"):
        backfill.load_assignments(manifest)
