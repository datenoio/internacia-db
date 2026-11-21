"""Tests for the reviewed includes[].joined backfill."""

from pathlib import Path

import backfill_includes_joined as backfill
import pytest
import yaml

EVIDENCE = [{"source": "Org - Member states", "url": "https://example.org/members", "retrieved_at": "2026-11-21"}]


def _write(root: Path, record_id: str, includes: str, extra: str = "") -> Path:
    path = root / "data" / "intblocks" / "political" / f"{record_id}.yaml"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        f"id: {record_id}\nblocktype:\n- political\nstatus: formal\nname: Example\nincludes:\n{includes}"
        f"description: Example org.\n{extra}",
        encoding="utf-8",
    )
    return path


def _member(code: str, status: str = "member", tail: str = "") -> str:
    return f"- id: {code}\n  name: Country {code}\n  type: country\n  status: {status}\n{tail}"


def _manifest(root: Path, records: dict, **extra) -> Path:
    path = root / "manifest.yaml"
    doc = {"version": 1, "expected_count": len(records), **extra, "records": records}
    path.write_text(yaml.safe_dump(doc, sort_keys=False), encoding="utf-8")
    return path


def _entry(joined: dict) -> dict:
    return {"joined": dict(joined), "evidence": list(EVIDENCE)}


def test_reviewed_manifest_is_consistent():
    records, metadata = backfill.load_manifest(backfill.DEFAULT_MANIFEST)
    assert len(records) == metadata["expected_count"]


def test_reviewed_manifest_is_applied():
    report = backfill.execute_backfill(backfill.ROOT, backfill.DEFAULT_MANIFEST, mode="check")
    assert (report.pending, report.conflicts) == (0, 0)


def test_dry_run_writes_nothing(tmp_path):
    path = _write(tmp_path, "ORG", _member("FR") + _member("DE"))
    before = path.read_text(encoding="utf-8")
    report = backfill.execute_backfill(tmp_path, _manifest(tmp_path, {"ORG": _entry({"FR": "1949"})}), mode="dry-run")
    assert (report.pending, report.applied) == (1, 0)
    assert path.read_text(encoding="utf-8") == before


def test_apply_adds_joined_after_status_and_provenance_only(tmp_path):
    left = "  left: '2020-01-31'\n  note: Withdrew\n"
    path = _write(tmp_path, "ORG", _member("FR") + _member("GB", "former_member", left),
                  extra="provenance:\n- field: wikidata_id\n  source: Wikidata\n  retrieved_at: '2026-01-01'\n")
    before = yaml.safe_load(path.read_text(encoding="utf-8"))
    joined = {"FR": "1958-01-01", "GB": "1973-01-01"}
    backfill.execute_backfill(tmp_path, _manifest(tmp_path, {"ORG": _entry(joined)}), mode="apply")
    text = path.read_text(encoding="utf-8")
    assert "  status: former_member\n  joined: '1973-01-01'\n  left: '2020-01-31'\n" in text
    after = yaml.safe_load(text)
    assert {i["id"]: i["joined"] for i in after["includes"]} == joined
    assert [p["field"] for p in after["provenance"]] == ["includes", "wikidata_id"]
    for key in before:
        if key not in ("includes", "provenance"):
            assert after[key] == before[key]


def test_apply_sets_last_verified_only_when_dates_are_added(tmp_path):
    changed = _write(tmp_path, "ORG", _member("FR"), extra="last_verified: '2026-01-01'\n")
    unchanged = _write(tmp_path, "DONE", _member("FR", tail="  joined: '1949'\n"),
                       extra="last_verified: '2026-01-01'\nprovenance:\n- field: includes\n  source: Org\n"
                             "  retrieved_at: '2026-11-21'\n  url: https://example.org/members\n")
    before = unchanged.read_text(encoding="utf-8")
    manifest = _manifest(tmp_path, {"ORG": _entry({"FR": "1949"}), "DONE": _entry({"FR": "1949"})},
                         verified_on="2026-11-21")
    backfill.execute_backfill(tmp_path, manifest, mode="apply")
    assert yaml.safe_load(changed.read_text(encoding="utf-8"))["last_verified"] == "2026-11-21"
    assert unchanged.read_text(encoding="utf-8") == before


def test_second_apply_is_a_no_op(tmp_path):
    path = _write(tmp_path, "ORG", _member("FR"))
    manifest = _manifest(tmp_path, {"ORG": _entry({"FR": "1949"})})
    backfill.execute_backfill(tmp_path, manifest, mode="apply")
    once = path.read_text(encoding="utf-8")
    report = backfill.execute_backfill(tmp_path, manifest, mode="apply")
    assert (report.already_set, report.applied) == (1, 0)
    assert path.read_text(encoding="utf-8") == once


def test_different_existing_date_blocks_apply(tmp_path):
    path = _write(tmp_path, "ORG", _member("FR", tail="  joined: '1950'\n") + _member("DE"))
    before = path.read_text(encoding="utf-8")
    manifest = _manifest(tmp_path, {"ORG": _entry({"FR": "1949", "DE": "1955"})})
    assert backfill.execute_backfill(tmp_path, manifest, mode="dry-run").conflicts == 1
    with pytest.raises(backfill.BackfillValidationError, match="conflicting"):
        backfill.execute_backfill(tmp_path, manifest, mode="apply")
    assert path.read_text(encoding="utf-8") == before


def test_unknown_include_id_is_rejected(tmp_path):
    _write(tmp_path, "ORG", _member("FR"))
    with pytest.raises(backfill.BackfillValidationError, match="not in includes"):
        backfill.execute_backfill(tmp_path, _manifest(tmp_path, {"ORG": _entry({"XX": "1949"})}), mode="dry-run")


@pytest.mark.parametrize("value", ["1949-00-00", "1949-13", "49", 1949])
def test_invalid_dates_are_rejected(tmp_path, value):
    _write(tmp_path, "ORG", _member("FR"))
    with pytest.raises(backfill.BackfillValidationError, match="joined values"):
        backfill.execute_backfill(tmp_path, _manifest(tmp_path, {"ORG": _entry({"FR": value})}), mode="dry-run")
