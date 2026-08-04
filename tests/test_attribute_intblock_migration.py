"""Tests for attribute-partition → country field migration."""

from __future__ import annotations

from pathlib import Path

import yaml

from internacia_builder.build import (
    get_countries_schema,
    load_attribute_intblock_migrations,
    save_attribute_intblock_migrations,
)
from internacia_builder.validate.country_rules import check_country_attribute_fields
from internacia_builder.validate.cross_rules import validate_attribute_intblock_migrations

ROOT = Path(__file__).resolve().parents[1]


def test_attribute_vocabs_exist():
    vocabs = ROOT / "data" / "vocabs"
    for name in (
        "writing_directions",
        "writing_systems",
        "dvd_regions",
        "broadcast_systems",
        "legal_systems",
        "rail_gauges",
        "government_forms",
    ):
        assert (vocabs / f"{name}.yaml").exists()


def test_retired_attribute_dirs_gone():
    for name in (
        "dvdregion",
        "govform",
        "lawsystem",
        "railgauge",
        "teleregion",
        "traffichand",
        "writingdirection",
        "writingsystem",
    ):
        assert not (ROOT / "data" / "intblocks" / name).exists()


def test_blocktypes_drop_attribute_ids():
    data = yaml.safe_load((ROOT / "data" / "blocktypes" / "blocktypes.yaml").read_text())
    ids = {e["id"] for e in data}
    for bid in (
        "dvdregion",
        "govform",
        "lawsystem",
        "railgauge",
        "teleregion",
        "traffichand",
        "writingdirection",
        "writingsystem",
    ):
        assert bid not in ids


def test_migration_artifact_covers_retired_ids():
    migrations = yaml.safe_load((ROOT / "data" / "attribute_intblock_migrations.yaml").read_text())
    retired = {m["retired_id"] for m in migrations}
    for rid in ("RHTRAFFIC", "LHTRAFFIC", "DVD_1", "WDLTR", "LSCOMMONLAW", "ABSMON"):
        assert rid in retired
    issues = validate_attribute_intblock_migrations(migrations, known_intblock_ids=set())
    assert issues == []


def test_migration_rejects_live_intblock():
    issues = validate_attribute_intblock_migrations(
        [{"retired_id": "NATO", "country_field": "car_side", "country_value": "left", "since": "x"}],
        known_intblock_ids={"NATO"},
    )
    assert any(i["issue_type"] == "ATTRIBUTE_MIGRATION_ERROR" for i in issues)


def test_check_attribute_fields_vocab_and_primary():
    issues = check_country_attribute_fields(
        {"writing_directions": [{"id": "ltr", "primary": True}, {"id": "rtl", "primary": True}]}
    )
    assert any("primary" in i["suggested_action"] for i in issues)

    issues = check_country_attribute_fields({"writing_systems": [{"id": "not_a_script"}]})
    assert any("vocab" in i["suggested_action"] for i in issues)

    issues = check_country_attribute_fields({"dvd_region": 9})
    assert issues

    issues = check_country_attribute_fields(
        {
            "writing_directions": [{"id": "ltr", "primary": True}],
            "dvd_region": 1,
            "broadcast_systems": [{"id": "ntsc"}],
            "car_side": "right",
        }
    )
    assert issues == []


def test_us_has_migrated_attributes():
    us = yaml.safe_load((ROOT / "data" / "countries" / "US.yaml").read_text())
    assert us.get("car_side") == "right"
    assert us.get("dvd_region") == 1
    assert {x["id"] for x in us.get("broadcast_systems") or []} >= {"atsc", "ntsc"}
    assert any(x["id"] == "ltr" for x in us.get("writing_directions") or [])


def test_countries_schema_includes_attribute_fields():
    names = {f.name for f in get_countries_schema()}
    for field in (
        "writing_directions",
        "writing_systems",
        "dvd_region",
        "broadcast_systems",
        "legal_systems",
        "rail_gauges",
        "car_side",
    ):
        assert field in names


def test_save_attribute_migrations(tmp_path):
    # Point loader at repo source via cwd-independent load then save
    rows = load_attribute_intblock_migrations(ROOT)
    assert len(rows) >= 40
    save_attribute_intblock_migrations(rows, tmp_path, write_parquet=True)
    assert (tmp_path / "attribute_intblock_migrations.json").exists()
    assert (tmp_path / "attribute_intblock_migrations.parquet").exists()
