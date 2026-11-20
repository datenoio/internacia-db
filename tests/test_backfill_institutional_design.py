"""Tests for the reviewed intblock institutional_design backfill."""

import shutil
from pathlib import Path

import backfill_institutional_design as backfill
import pytest
import yaml

from internacia_builder.paths import project_root

DESIGN = {"mandate": "security", "decision_rule": "consensus", "enforcement": ["none"], "mutual_defence": True}
EVIDENCE = {"source": "Founding treaty", "url": "https://example.org/treaty", "retrieved_at": "2026-11-20"}


def _project(tmp_path: Path) -> Path:
    schemas = tmp_path / "data" / "schemas"
    schemas.mkdir(parents=True)
    shutil.copy(project_root() / "data" / "schemas" / "intblocks.schema.json", schemas)
    return tmp_path


def _write_record(root: Path, record_id: str, *, scope: str = "igo", extra: str = "") -> Path:
    path = root / "data" / "intblocks" / "military" / f"{record_id}.yaml"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        f"id: {record_id}\nstatus: formal\nscope_category: {scope}\nname: Example {record_id}\n"
        f"includes:\n- id: AA\n  status: member\n{extra}",
        encoding="utf-8",
    )
    return path


def _write_manifest(root: Path, records: dict, *, expected: int | None = None) -> Path:
    path = root / "manifest.yaml"
    payload = {
        "version": 1,
        "change_id": "add-intblock-institutional-design",
        "expected_count": len(records) if expected is None else expected,
        "records": records,
    }
    path.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")
    return path


def _entry(design=None, evidence=None):
    return {"institutional_design": dict(design or DESIGN), "evidence": evidence or dict(EVIDENCE)}


def test_reviewed_pilot_manifest_is_valid():
    records, metadata = backfill.load_manifest(backfill.DEFAULT_MANIFEST, project_root())
    assert metadata["change_id"] == "add-intblock-institutional-design"
    assert len(records) == metadata["expected_count"] == 55
    assert not set(records) & set(metadata["deferred"])


def test_dry_run_writes_nothing(tmp_path):
    root = _project(tmp_path)
    path = _write_record(root, "EXAMPLE")
    before = path.read_text(encoding="utf-8")
    manifest = _write_manifest(root, {"EXAMPLE": _entry()})

    report = backfill.execute_backfill(root, manifest, mode="dry-run")

    assert (report.pending, report.applied, report.conflicts) == (1, 0, 0)
    assert path.read_text(encoding="utf-8") == before


def test_apply_inserts_block_and_provenance_surgically(tmp_path):
    root = _project(tmp_path)
    path = _write_record(root, "EXAMPLE", extra="provenance:\n- field: includes\n  source: Example\n  retrieved_at: '2026-01-01'\n")
    manifest = _write_manifest(root, {"EXAMPLE": _entry()})

    report = backfill.execute_backfill(root, manifest, mode="apply")

    assert report.applied == 1
    text = path.read_text(encoding="utf-8")
    assert text.startswith("id: EXAMPLE\nstatus: formal\nscope_category: igo\ninstitutional_design:\n  mandate: security\n")
    record = yaml.safe_load(text)
    assert record["institutional_design"] == DESIGN
    assert [p["field"] for p in record["provenance"]] == ["institutional_design", "includes"]
    assert record["includes"] == [{"id": "AA", "status": "member"}]


def test_subfields_follow_schema_order(tmp_path):
    root = _project(tmp_path)
    path = _write_record(root, "EXAMPLE")
    shuffled = {"mutual_defence": True, "enforcement": ["none"], "mandate": "security"}
    backfill.execute_backfill(root, _write_manifest(root, {"EXAMPLE": _entry(shuffled)}), mode="apply")
    keys = list(yaml.safe_load(path.read_text(encoding="utf-8"))["institutional_design"])
    assert keys == ["mandate", "enforcement", "mutual_defence"]


def test_several_sources_become_several_provenance_entries(tmp_path):
    root = _project(tmp_path)
    path = _write_record(root, "EXAMPLE")
    second = {"source": "Rules of procedure", "url": "https://example.org/rules", "retrieved_at": "2026-11-20"}
    manifest = _write_manifest(root, {"EXAMPLE": _entry(evidence=[dict(EVIDENCE), second])})

    backfill.execute_backfill(root, manifest, mode="apply")

    provenance = yaml.safe_load(path.read_text(encoding="utf-8"))["provenance"]
    assert [p["url"] for p in provenance] == [EVIDENCE["url"], second["url"]]


def test_second_apply_is_idempotent(tmp_path):
    root = _project(tmp_path)
    path = _write_record(root, "EXAMPLE")
    manifest = _write_manifest(root, {"EXAMPLE": _entry()})
    backfill.execute_backfill(root, manifest, mode="apply")
    after_first = path.read_text(encoding="utf-8")

    report = backfill.execute_backfill(root, manifest, mode="apply")

    assert (report.already_set, report.pending, report.applied) == (1, 0, 0)
    assert path.read_text(encoding="utf-8") == after_first


def test_conflict_blocks_whole_apply(tmp_path):
    root = _project(tmp_path)
    clean = _write_record(root, "CLEAN")
    _write_record(root, "TAKEN", extra="institutional_design:\n  mandate: economic\n")
    clean_before = clean.read_text(encoding="utf-8")
    manifest = _write_manifest(root, {"CLEAN": _entry(), "TAKEN": _entry()})

    report = backfill.execute_backfill(root, manifest, mode="dry-run")
    assert report.conflicts == 1
    with pytest.raises(backfill.BackfillValidationError, match="TAKEN"):
        backfill.execute_backfill(root, manifest, mode="apply")
    assert clean.read_text(encoding="utf-8") == clean_before


def test_unknown_manifest_id_fails_before_writing(tmp_path):
    root = _project(tmp_path)
    path = _write_record(root, "EXAMPLE")
    before = path.read_text(encoding="utf-8")
    manifest = _write_manifest(root, {"EXAMPLE": _entry(), "MISSING": _entry()})

    with pytest.raises(backfill.BackfillValidationError, match="MISSING"):
        backfill.execute_backfill(root, manifest, mode="apply")
    assert path.read_text(encoding="utf-8") == before


@pytest.mark.parametrize(
    "records,expected,message",
    [
        ({"EXAMPLE": _entry({"decision_rule": "majority"})}, None, "invalid"),
        ({"EXAMPLE": {"institutional_design": dict(DESIGN), "evidence": {"source": "x"}}}, None, "missing fields"),
        ({"EXAMPLE": _entry()}, 2, "expected_count"),
    ],
)
def test_invalid_manifest_is_rejected(tmp_path, records, expected, message):
    root = _project(tmp_path)
    _write_record(root, "EXAMPLE")
    manifest = _write_manifest(root, records, expected=expected)
    with pytest.raises(backfill.BackfillValidationError, match=message):
        backfill.execute_backfill(root, manifest, mode="dry-run")


def test_disallowed_scope_category_is_rejected(tmp_path):
    root = _project(tmp_path)
    _write_record(root, "EXAMPLE", scope="reference_enumeration")
    with pytest.raises(backfill.BackfillValidationError, match="scope_category"):
        backfill.execute_backfill(root, _write_manifest(root, {"EXAMPLE": _entry()}), mode="dry-run")


def test_inline_provenance_is_refused(tmp_path):
    root = _project(tmp_path)
    _write_record(root, "EXAMPLE", extra="provenance: []\n")
    with pytest.raises(backfill.BackfillValidationError, match="block list"):
        backfill.execute_backfill(root, _write_manifest(root, {"EXAMPLE": _entry()}), mode="dry-run")
