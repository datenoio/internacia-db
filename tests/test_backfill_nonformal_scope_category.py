"""Regression tests for staged non-formal scope-category backfill."""

from __future__ import annotations

import csv
import hashlib
from pathlib import Path

import backfill_nonformal_scope_category as migration
import pytest
import yaml
from backfill_scope_category import BackfillValidationError
from typer.testing import CliRunner

RUNNER = CliRunner()
ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = {
    "source": "Official description of the entity",
    "url": "https://example.org/primary",
    "retrieved_at": "2026-09-30",
}


def _fixture(root: Path, *, second_reviewed: bool = False) -> tuple[Path, dict[str, Path]]:
    paths = {}
    records = {}
    for record_id, status in (("HIST", "historical"), ("INFORMAL", "informal")):
        path = root / "data/intblocks/test" / f"{record_id}.yaml"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            f"id: {record_id}\nstatus: {status}\nname: Example {record_id}\n"
            "includes:\n- id: AA\n  name: Example\n  type: country\n  status: participant\n"
            "provenance:\n- field: name\n  source: Earlier source\n"
            "  retrieved_at: '2026-01-01'\n"
            "last_verified: '2026-01-01'\n",
            encoding="utf-8",
        )
        paths[record_id] = path
        reviewed = record_id == "HIST" or second_reviewed
        entry = {
            "path": str(path.relative_to(root)),
            "expected_status": status,
            "category": "treaty_body" if record_id == "HIST" else "reference_enumeration",
            "source_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            "review_state": "source_reviewed" if reviewed else "pending_review",
        }
        if reviewed:
            entry["evidence"] = dict(EVIDENCE)
        records[record_id] = entry
    manifest = root / "cohort.yaml"
    manifest.write_text(
        yaml.safe_dump(
            {
                "version": 1,
                "cohort_id": "nonformal_candidates_30",
                "expected_count": 2,
                "records": records,
            },
            sort_keys=False,
        ),
        encoding="utf-8",
    )
    return manifest, paths


def test_curated_manifest_exactly_matches_30_candidate_rows():
    manifest = migration.load_manifest(migration.DEFAULT_MANIFEST)
    with (ROOT / "outputs/nonformal-scope-audit-2026-09-30.csv").open(encoding="utf-8") as handle:
        expected = {
            row["id"]: (row["scope_category_candidate"], row["status"], row["confidence"])
            for row in csv.DictReader(handle)
            if row["scope_category_candidate"]
        }
    assert len(manifest) == len(expected) == 30
    assert {d.record_id: (d.category, d.expected_status) for d in manifest} == {
        rid: pair[:2] for rid, pair in expected.items()
    }
    individually_approved = {"ARABW", "BALTICSTATES", "HISPAM", "MIDAMERICA", "SLAVISPHERE", "CMA"}
    assert sum(d.review_state == "source_reviewed" for d in manifest) == 18
    assert sum(d.review_state == "pending_review" for d in manifest) == 12
    assert all(
        (d.review_state == "source_reviewed")
        == (expected[d.record_id][2] == "high" or d.record_id in individually_approved)
        for d in manifest
    )


def test_dry_run_does_not_write_and_reports_blockers(tmp_path: Path):
    manifest, paths = _fixture(tmp_path)
    original = {record_id: path.read_bytes() for record_id, path in paths.items()}

    result = migration.execute_backfill(tmp_path, manifest, mode="dry-run")

    assert (result.assignments, result.ready, result.blocked, result.pending, result.applied) == (2, 1, 1, 1, 0)
    assert {record_id: path.read_bytes() for record_id, path in paths.items()} == original


def test_apply_refuses_entire_cohort_until_each_entry_reviewed(tmp_path: Path):
    manifest, paths = _fixture(tmp_path)
    original = {record_id: path.read_bytes() for record_id, path in paths.items()}

    with pytest.raises(BackfillValidationError, match="refusing partial apply"):
        migration.execute_backfill(tmp_path, manifest, mode="apply")

    assert {record_id: path.read_bytes() for record_id, path in paths.items()} == original


def test_fully_reviewed_apply_preserves_other_fields_and_is_idempotent(tmp_path: Path):
    manifest, paths = _fixture(tmp_path, second_reviewed=True)
    before = {rid: yaml.safe_load(path.read_text(encoding="utf-8")) for rid, path in paths.items()}

    first = migration.execute_backfill(tmp_path, manifest, mode="apply")
    second = migration.execute_backfill(tmp_path, manifest, mode="apply")
    check = RUNNER.invoke(migration.app, ["--root", str(tmp_path), "--manifest", str(manifest), "--check"])

    assert first.applied == 2
    assert second.applied == 0 and second.already_set == 2
    assert check.exit_code == 0 and "already_set=2" in check.output
    for rid, path in paths.items():
        after = yaml.safe_load(path.read_text(encoding="utf-8"))
        assert after["scope_category"] == ("treaty_body" if rid == "HIST" else "reference_enumeration")
        assert after["includes"] == before[rid]["includes"]
        assert after["provenance"][:-1] == before[rid]["provenance"]
        assert after["provenance"][-1] == {"field": "scope_category", **EVIDENCE}


def test_source_drift_blocks_apply_without_touching_other_record(tmp_path: Path):
    manifest, paths = _fixture(tmp_path, second_reviewed=True)
    paths["INFORMAL"].write_text(
        paths["INFORMAL"].read_text(encoding="utf-8") + "notes: Changed after review\n",
        encoding="utf-8",
    )
    before = paths["HIST"].read_bytes()
    report = migration.execute_backfill(tmp_path, manifest, mode="dry-run")

    assert report.conflicts == 1
    assert any(c.reason == "source SHA-256 changed" for c in report.changes)
    with pytest.raises(BackfillValidationError, match="refusing partial apply"):
        migration.execute_backfill(tmp_path, manifest, mode="apply")
    assert paths["HIST"].read_bytes() == before


def test_status_drift_and_existing_category_are_rejected(tmp_path: Path):
    manifest, paths = _fixture(tmp_path, second_reviewed=True)
    source = paths["HIST"]
    source.write_text(
        source.read_text(encoding="utf-8").replace("status: historical", "status: formal"), encoding="utf-8"
    )
    with pytest.raises(BackfillValidationError, match="status drifted"):
        migration.plan_backfill(tmp_path, manifest)
    source.write_text(
        source.read_text(encoding="utf-8").replace("status: formal", "status: historical"), encoding="utf-8"
    )
    source.write_text(source.read_text(encoding="utf-8") + "scope_category: igo\n", encoding="utf-8")
    report = migration.execute_backfill(tmp_path, manifest, mode="dry-run")
    assert report.conflicts == 1
    assert "existing category: igo" in [c.reason for c in report.changes]


def test_reviewed_decision_without_evidence_is_rejected(tmp_path: Path):
    manifest, _ = _fixture(tmp_path)
    payload = yaml.safe_load(manifest.read_text(encoding="utf-8"))
    del payload["records"]["HIST"]["evidence"]
    manifest.write_text(yaml.safe_dump(payload), encoding="utf-8")
    with pytest.raises(BackfillValidationError, match="needs record-specific evidence"):
        migration.load_manifest(manifest)


def test_manifest_rejects_formal_status_and_unsafe_path(tmp_path: Path):
    manifest, _ = _fixture(tmp_path)
    payload = yaml.safe_load(manifest.read_text(encoding="utf-8"))
    payload["records"]["HIST"]["expected_status"] = "formal"
    manifest.write_text(yaml.safe_dump(payload), encoding="utf-8")
    with pytest.raises(BackfillValidationError, match="invalid category or non-formal status"):
        migration.load_manifest(manifest)
    payload["records"]["HIST"]["expected_status"] = "historical"
    payload["records"]["HIST"]["path"] = "../outside/HIST.yaml"
    manifest.write_text(yaml.safe_dump(payload), encoding="utf-8")
    with pytest.raises(BackfillValidationError, match="unsafe or mismatching source path"):
        migration.load_manifest(manifest)


def test_existing_provenance_difference_is_a_conflict(tmp_path: Path):
    manifest, paths = _fixture(tmp_path, second_reviewed=True)
    migration.execute_backfill(tmp_path, manifest, mode="apply")
    source = paths["HIST"]
    source.write_text(
        source.read_text(encoding="utf-8").replace("https://example.org/primary", "https://example.org/different"),
        encoding="utf-8",
    )
    report = migration.execute_backfill(tmp_path, manifest, mode="dry-run")
    assert report.conflicts == 1
    assert "scope_category provenance differs" in [c.reason for c in report.changes]


def test_cli_json_report_and_check_return_code(tmp_path: Path):
    manifest, paths = _fixture(tmp_path)
    output = tmp_path / "report.json"
    result = RUNNER.invoke(
        migration.app,
        ["--root", str(tmp_path), "--manifest", str(manifest), "--report-json", str(output)],
    )
    assert result.exit_code == 0, result.output
    assert "blocked=1" in result.output
    assert output.exists()
    check = RUNNER.invoke(migration.app, ["--root", str(tmp_path), "--manifest", str(manifest), "--check"])
    assert check.exit_code == 1
    assert "scope_category:" not in paths["HIST"].read_text(encoding="utf-8")
