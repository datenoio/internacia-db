"""Tests for the reviewed includes[].role backfill."""

import shutil
from pathlib import Path

import backfill_include_roles as backfill
import pytest
import yaml

from internacia_builder.paths import project_root

EVIDENCE = [{"source": "Operator", "url": "https://example.org/route", "retrieved_at": "2026-11-20"}]
PIPE_ROLES = {"AZ": "origin", "GE": "transit", "TR": "destination"}


def _project(tmp_path: Path) -> Path:
    schemas = tmp_path / "data" / "schemas"
    schemas.mkdir(parents=True)
    shutil.copy(project_root() / "data" / "schemas" / "include_roles.yaml", schemas)
    return tmp_path


def _write(root: Path, record_id: str, blocktype: str = "gaspipeline", extra: str = "", countries=("AZ", "GE", "TR")) -> Path:
    path = root / "data" / "intblocks" / blocktype / f"{record_id}.yaml"
    path.parent.mkdir(parents=True, exist_ok=True)
    includes = "".join(f"- id: {c}\n  name: Country {c}\n  type: country\n  status: member\n" for c in countries)
    path.write_text(
        f"id: {record_id}\nblocktype:\n- {blocktype}\nstatus: de-facto\nname: Example\nincludes:\n{includes}"
        f"description: Example route.\n{extra}",
        encoding="utf-8",
    )
    return path


def _manifest(root: Path, records: dict) -> Path:
    path = root / "manifest.yaml"
    path.write_text(yaml.safe_dump({"version": 1, "expected_count": len(records), "records": records}, sort_keys=False), encoding="utf-8")
    return path


def _entry(roles=None, **extra):
    return {"roles": dict(roles or PIPE_ROLES), "evidence": list(EVIDENCE), **extra}


def test_reviewed_manifest_is_consistent():
    records, metadata = backfill.load_manifest(backfill.DEFAULT_MANIFEST)
    assert len(records) == metadata["expected_count"]
    assert not set(records) & set(metadata.get("deferred") or {})


def test_dry_run_writes_nothing(tmp_path):
    root = _project(tmp_path)
    path = _write(root, "PIPE")
    before = path.read_text(encoding="utf-8")
    report = backfill.execute_backfill(root, _manifest(root, {"PIPE": _entry()}), mode="dry-run")
    assert (report.pending, report.applied) == (1, 0)
    assert path.read_text(encoding="utf-8") == before


def test_apply_adds_roles_and_provenance_only(tmp_path):
    root = _project(tmp_path)
    path = _write(root, "PIPE", extra="provenance:\n- field: wikidata_id\n  source: Wikidata\n  retrieved_at: '2026-01-01'\n")
    before = yaml.safe_load(path.read_text(encoding="utf-8"))
    backfill.execute_backfill(root, _manifest(root, {"PIPE": _entry()}), mode="apply")
    after = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert {i["id"]: i["role"] for i in after["includes"]} == PIPE_ROLES
    assert [p["field"] for p in after["provenance"]] == ["includes", "wikidata_id"]
    for key in before:
        if key not in ("includes", "provenance"):
            assert after[key] == before[key]


def test_corridor_blocktype_is_appended(tmp_path):
    root = _project(tmp_path)
    path = _write(root, "RAIL", blocktype="project", countries=("CN", "KG", "UZ"))
    roles = {"CN": "terminal", "KG": "transit", "UZ": "terminal"}
    backfill.execute_backfill(root, _manifest(root, {"RAIL": _entry(roles, add_blocktypes=["corridor"])}), mode="apply")
    after = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert after["blocktype"] == ["project", "corridor"]
    assert {i["id"]: i["role"] for i in after["includes"]} == roles


def test_second_apply_is_idempotent(tmp_path):
    root = _project(tmp_path)
    path = _write(root, "PIPE")
    manifest = _manifest(root, {"PIPE": _entry()})
    backfill.execute_backfill(root, manifest, mode="apply")
    first = path.read_text(encoding="utf-8")
    report = backfill.execute_backfill(root, manifest, mode="apply")
    assert (report.already_set, report.applied) == (1, 0)
    assert path.read_text(encoding="utf-8") == first


def test_conflicting_role_blocks_apply(tmp_path):
    root = _project(tmp_path)
    clean = _write(root, "CLEAN")
    taken = _write(root, "TAKEN")
    taken.write_text(taken.read_text().replace("- id: GE\n  name: Country GE\n  type: country\n  status: member\n",
                                               "- id: GE\n  name: Country GE\n  type: country\n  status: member\n  role: destination\n"))
    before = clean.read_text(encoding="utf-8")
    manifest = _manifest(root, {"CLEAN": _entry(), "TAKEN": _entry()})
    assert backfill.execute_backfill(root, manifest, mode="dry-run").conflicts == 1
    with pytest.raises(backfill.BackfillValidationError, match="TAKEN"):
        backfill.execute_backfill(root, manifest, mode="apply")
    assert clean.read_text(encoding="utf-8") == before


@pytest.mark.parametrize(
    "entry,message",
    [
        (_entry({"AZ": "origin", "GE": "transit"}), "cover exactly"),
        (_entry({"AZ": "origin", "GE": "transit", "TR": "transit"}), "at least 1 'destination'"),
        (_entry({"AZ": "terminal", "GE": "transit", "TR": "terminal"}), "not valid for a pipeline"),
    ],
)
def test_invalid_roles_rejected(tmp_path, entry, message):
    root = _project(tmp_path)
    _write(root, "PIPE")
    with pytest.raises(backfill.BackfillValidationError, match=message):
        backfill.execute_backfill(root, _manifest(root, {"PIPE": entry}), mode="dry-run")


def test_non_infrastructure_record_rejected(tmp_path):
    root = _project(tmp_path)
    _write(root, "ORG", blocktype="political")
    with pytest.raises(backfill.BackfillValidationError, match="role-bearing blocktype"):
        backfill.execute_backfill(root, _manifest(root, {"ORG": _entry()}), mode="dry-run")


def test_unknown_manifest_id(tmp_path):
    root = _project(tmp_path)
    _write(root, "PIPE")
    with pytest.raises(backfill.BackfillValidationError, match="MISSING"):
        backfill.execute_backfill(root, _manifest(root, {"PIPE": _entry(), "MISSING": _entry()}), mode="dry-run")


def test_changed_record_gets_verified_on(tmp_path):
    root = _project(tmp_path)
    path = _write(root, "PIPE", extra="last_verified: '2026-01-01'\n")
    manifest = root / "manifest.yaml"
    manifest.write_text(yaml.safe_dump({"version": 1, "expected_count": 1, "verified_on": "2026-11-20",
                                        "records": {"PIPE": _entry()}}, sort_keys=False), encoding="utf-8")
    backfill.execute_backfill(root, manifest, mode="apply")
    assert yaml.safe_load(path.read_text(encoding="utf-8"))["last_verified"] == "2026-11-20"
