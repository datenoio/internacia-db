"""Per-source enrichment pull requests: split, review gate, CLI."""

import copy
import json
import shutil
from datetime import date
from pathlib import Path

import enrichment_split
import yaml
from typer.testing import CliRunner

from internacia_builder import enrichment, freshness
from internacia_builder import enrichment_sources as es
from internacia_builder.yaml_io import safe_load

ROOT = Path(__file__).resolve().parents[1]
FR = "data/countries/FR.yaml"
TODAY = date.today()


def _fr():
    return safe_load((ROOT / FR).read_text(encoding="utf-8"))


def _enriched(record):
    after = copy.deepcopy(record)
    after["population"] = dict(after["population"], value=int(after["population"]["value"] * 1.01), year=TODAY.year)
    after["region"] = {"id": "XXX", "value": "Somewhere"}
    after["timezones"] = [*after["timezones"], "Europe/Monaco"]
    after["provenance"] = [
        dict(p, retrieved_at=TODAY.isoformat()) if p.get("field") == "population" else p
        for p in after.get("provenance") or []
    ]
    return after


def test_split_puts_each_field_in_its_source():
    policy = es.load_policy(ROOT)
    before = _fr()
    parts = es.split({FR: before}, {FR: _enriched(before)}, policy)
    assert set(parts) == {"wb-indicators", "wb-classifications", "iana-timezones"}
    indicators = parts["wb-indicators"][FR]
    assert indicators["population"]["year"] == TODAY.year
    assert indicators["region"] == before["region"] and indicators["timezones"] == before["timezones"]
    prov = {p["field"]: p for p in indicators["provenance"]}
    assert prov["population"]["retrieved_at"] == TODAY.isoformat()
    assert list(indicators) == list(before)
    assert parts["iana-timezones"][FR]["population"] == before["population"]


def test_review_gate():
    policy = es.load_policy(ROOT)
    before = _fr()
    parts = es.split({FR: before}, {FR: _enriched(before)}, policy)
    base = {FR: before}
    assert es.review_reasons("wb-indicators", base, parts["wb-indicators"], policy) == []
    assert es.review_reasons("iana-timezones", base, parts["iana-timezones"], policy) == []
    assert es.review_reasons("wb-classifications", base, parts["wb-classifications"], policy)

    jump = copy.deepcopy(before)
    jump["population"]["value"] = before["population"]["value"] * 2
    reasons = es.review_reasons("wb-indicators", base, {FR: jump}, policy)
    assert len(reasons) == 1 and "exceeds ±10%" in reasons[0]

    shrink = copy.deepcopy(before)
    shrink["timezones"] = []
    assert es.review_reasons("iana-timezones", base, {FR: shrink}, policy) == ["FR.timezones: value removed"]

    renamed = copy.deepcopy(before)
    renamed["wikidata_id"] = "Q1"
    assert es.review_reasons("wikidata-countries", base, {FR: renamed}, policy) == ["FR.wikidata_id: existing value replaced"]


def test_unlisted_fields_and_new_records_go_to_other():
    policy = es.load_policy(ROOT)
    before = _fr()
    after = dict(before, borders=["ZZZ"])
    parts = es.split({FR: before}, {FR: after, "data/countries/ZZ.yaml": {"code": "ZZ"}}, policy)
    assert set(parts) == {"other"}
    assert set(parts["other"]) == {FR, "data/countries/ZZ.yaml"}
    assert es.review_reasons("other", {FR: before}, parts["other"], policy)


def test_metadata_only_changes_do_not_need_last_verified():
    rel = "data/intblocks/x/AB.yaml"
    before = {"id": "AB", "includes": [{"id": "FR"}], "description": "Old"}
    metadata = dict(before, description="New", other_names=["Ab"], provenance=[{"field": "description"}])
    assert freshness.check_changed_records([(rel, metadata)], {rel: before}, "origin/main") == []
    roster = dict(before, includes=[{"id": "FR"}, {"id": "DE"}])
    assert freshness.check_changed_records([(rel, roster)], {rel: before}, "origin/main")


def test_apply_cli(tmp_path, monkeypatch):
    shutil.copytree(ROOT / "data/schemas", tmp_path / "data/schemas")
    (tmp_path / "data/countries").mkdir(parents=True)
    before = _fr()
    (tmp_path / FR).write_text(yaml.safe_dump(before, allow_unicode=True, sort_keys=False), encoding="utf-8")
    snapshot = tmp_path / "enrichment.json"
    snapshot.write_text(json.dumps({"base": {FR: before}, "enriched": {FR: _enriched(before)}}))
    monkeypatch.setattr(enrichment_split, "project_root", lambda: tmp_path)
    monkeypatch.setattr(enrichment, "project_root", lambda: tmp_path)
    out = tmp_path / "gh-output"
    monkeypatch.setenv("GITHUB_OUTPUT", str(out))

    result = CliRunner().invoke(
        enrichment_split.app,
        ["apply", str(snapshot), "--source", "wb-indicators", "--pr-body", str(tmp_path / "body.md")],
    )

    assert result.exit_code == 0, result.output
    written = safe_load((tmp_path / FR).read_text(encoding="utf-8"))
    assert written["population"]["year"] == TODAY.year and written["region"] == before["region"]
    assert "auto_merge=true" in out.read_text()
    assert "merges automatically" in (tmp_path / "body.md").read_text()
