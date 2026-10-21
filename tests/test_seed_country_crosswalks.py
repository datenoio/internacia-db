"""Tests for the curated country crosswalk pipeline."""

import pytest
import seed_country_crosswalks as crosswalks
import yaml

SOURCES = {
    field: {
        "source": f"Source for {field}",
        "url": "https://example.test/source",
        "retrieved_at": "2026-09-29",
        "license": "CC-BY-4.0",
    }
    for field in crosswalks.FIELDS
}


def test_reconcile_adds_value_and_field_provenance():
    text = """code: AA
name: Example
wikidata_id: Q1
provenance:
- field: name
  source: Example
  url: https://example.test/name
  retrieved_at: '2026-01-01'
centroid:
  lat: 0
  lng: 0
"""
    updated, actions, conflicts = crosswalks.reconcile_text(
        text,
        {"geonames_id": "123"},
        SOURCES,
        ("geonames_id",),
    )

    record = yaml.safe_load(updated)
    assert record["geonames_id"] == "123"
    assert any(p["field"] == "geonames_id" for p in record["provenance"])
    assert record["centroid"] == {"lat": 0, "lng": 0}
    assert [a["action"] for a in actions] == ["added", "provenance_added"]
    assert conflicts == []


def test_reconcile_adds_missing_provenance_to_existing_value():
    text = """code: AA
geonames_id: '123'
provenance: []
"""
    updated, actions, conflicts = crosswalks.reconcile_text(
        text,
        {"geonames_id": "123"},
        SOURCES,
        ("geonames_id",),
    )

    assert yaml.safe_load(updated)["provenance"][0]["field"] == "geonames_id"
    assert [a["action"] for a in actions] == ["provenance_added"]
    assert conflicts == []


def test_reconcile_is_idempotent_after_first_pass():
    text = "code: AA\nprovenance: []\n"
    first, _, _ = crosswalks.reconcile_text(
        text, {"ioc_code": "AAA"}, SOURCES, ("ioc_code",)
    )
    second, actions, conflicts = crosswalks.reconcile_text(
        first, {"ioc_code": "AAA"}, SOURCES, ("ioc_code",)
    )

    assert second == first
    assert actions == []
    assert conflicts == []


def test_explicit_refresh_replaces_existing_provenance():
    text = """code: AA
geonames_id: "123"
provenance:
- field: geonames_id
  source: "Old source"
  url: "https://old.example.test"
  retrieved_at: "2020-01-01"
"""
    updated, actions, conflicts = crosswalks.reconcile_text(
        text,
        {"geonames_id": "123"},
        SOURCES,
        ("geonames_id",),
        refresh_provenance=True,
    )

    entry = yaml.safe_load(updated)["provenance"][0]
    assert entry["source"] == "Source for geonames_id"
    assert entry["retrieved_at"] == "2026-09-29"
    assert [a["action"] for a in actions] == ["provenance_refreshed"]
    assert conflicts == []


def test_existing_only_does_not_add_new_value():
    text = "code: AA\nprovenance: []\n"
    updated, actions, conflicts = crosswalks.reconcile_text(
        text,
        {"geonames_id": "123"},
        SOURCES,
        ("geonames_id",),
        existing_only=True,
    )

    assert updated == text
    assert actions == []
    assert conflicts == []


def test_reconcile_reports_conflict_without_overwrite():
    text = "code: AA\nfifa_code: \"OLD\"\nprovenance: []\n"
    updated, actions, conflicts = crosswalks.reconcile_text(
        text, {"fifa_code": "NEW"}, SOURCES, ("fifa_code",)
    )

    assert updated == text
    assert actions == []
    assert conflicts[0]["current"] == "OLD"
    assert conflicts[0]["target"] == "NEW"


def test_reconcile_allows_explicit_overwrite():
    text = "code: AA\nfifa_code: \"OLD\"\nprovenance: []\n"
    updated, actions, conflicts = crosswalks.reconcile_text(
        text,
        {"fifa_code": "NEW"},
        SOURCES,
        ("fifa_code",),
        allow_overwrite=True,
    )

    assert yaml.safe_load(updated)["fifa_code"] == "NEW"
    assert [a["action"] for a in actions] == ["updated", "provenance_added"]
    assert conflicts == []


def test_seed_validation_rejects_duplicate_external_id():
    rows = {
        "AA": {"geonames_id": "123"},
        "BB": {"geonames_id": "123"},
    }
    with pytest.raises(crosswalks.SeedValidationError, match="duplicate geonames_id"):
        crosswalks.validate_seed_values(rows)


def test_seed_validation_rejects_bad_format():
    rows = {"AA": {"ioc_code": "aa"}}
    with pytest.raises(crosswalks.SeedValidationError, match="invalid ioc_code"):
        crosswalks.validate_seed_values(rows)
