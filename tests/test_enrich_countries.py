"""Regressions for provider refreshes and honest source dates (offline)."""

from copy import deepcopy

import enrich_countries as ec
import pytest

from internacia_builder.enrichment import write_enriched_yaml
from internacia_builder.paths import project_root
from internacia_builder.validate.country_rules import check_country_indicator_years
from internacia_builder.yaml_io import safe_load


def country(source="World Bank"):
    return {
        "code": "ZZ", "iso3code": "ZZZ",
        "population": {"value": 100, "year": 2020, "source": source, "source_id": "SP.POP.TOTL"},
        "provenance": [{"field": "population", "source": source, "retrieved_at": "2020-01-01"}],
    }


def enrich(record, observation=None, **kwargs):
    wb = {"population": {"ZZZ": observation} if observation else {}, "area": {}, "gini": {}}
    return ec.enrich_record(record, wb, {}, {}, **kwargs)


def test_newer_provider_observation_refreshes_value_and_its_provenance():
    result = enrich(country(), {"value": 200, "year": 2025})
    assert result["population"]["value"] == 200
    assert result["population"]["year"] == 2025
    assert result["provenance"][0]["retrieved_at"] == ec.date.today().isoformat()


@pytest.mark.parametrize("observation", [None, {"value": 100, "year": 2020}, {"value": 80, "year": 2019}])
def test_failed_unchanged_or_older_observation_preserves_value_and_retrieval(observation):
    original = country()
    result = enrich(deepcopy(original), observation)
    assert result["population"] == original["population"]
    assert result["provenance"] == original["provenance"]


def test_provider_refresh_preserves_curated_source_unless_forced():
    original = country("National statistics")
    result = enrich(deepcopy(original), {"value": 200, "year": 2025})
    assert result["population"] == original["population"]
    assert result["provenance"] == original["provenance"]
    assert enrich(original, {"value": 200, "year": 2025}, force=True)["population"]["value"] == 200


def test_forced_failed_fetch_does_not_renew_existing_provenance():
    original = country()
    result = enrich(deepcopy(original), force=True)
    assert result["population"] == original["population"]
    assert result["provenance"] == original["provenance"]


def test_wikidata_fallback_omits_unknown_observation_year():
    record = {"code": "ZZ", "iso3code": "ZZZ", "wikidata_id": "Q1"}
    entity = {"claims": {"P1082": [{"mainsnak": {"datavalue": {"value": {"amount": "+100"}}}}]}}
    result = ec.enrich_record(record, {}, {}, {"Q1": entity})
    assert result["population"]["value"] == 100
    assert "year" not in result["population"]
    assert check_country_indicator_years(result) == []


def test_provenance_backfill_cannot_invent_retrieval_dates():
    original = country()
    result = deepcopy(original)
    ec.sync_provenance_from_record(result)
    assert result == original


def test_partial_paginated_fetch_is_reported_as_failure(monkeypatch):
    responses = iter([[{"pages": 2}, [{"countryiso3code": "USA", "date": "2025", "value": 1}]]])

    def fetch(_url):
        try:
            return next(responses)
        except StopIteration as exc:
            raise OSError("provider unavailable") from exc

    monkeypatch.setattr(ec, "fetch_json", fetch)
    monkeypatch.setattr(ec.time, "sleep", lambda _: None)
    with pytest.raises(RuntimeError, match="page 2"):
        ec.fetch_world_bank("SP.POP.TOTL")


def test_invalid_enrichment_preserves_original_file(tmp_path):
    path = tmp_path / "US.yaml"
    path.write_text("original source\n")
    with pytest.raises(ValueError, match="Refusing invalid enrichment"):
        write_enriched_yaml(path, {"code": "US", "population": {"value": 1, "year": 0}}, "countries")
    assert path.read_text() == "original source\n"


def test_valid_enrichment_replaces_content_preserving_permissions(tmp_path):
    record = safe_load((project_root() / "data/countries/US.yaml").read_text())
    path = tmp_path / "US.yaml"
    path.write_text("old source\n")
    path.chmod(0o640)
    write_enriched_yaml(path, record, "countries")
    assert safe_load(path.read_text()) == record
    assert path.stat().st_mode & 0o777 == 0o640
    assert list(tmp_path.iterdir()) == [path]


def test_failed_atomic_replacement_preserves_source_and_removes_temporary_file(tmp_path, monkeypatch):
    record = safe_load((project_root() / "data/countries/US.yaml").read_text())
    path = tmp_path / "US.yaml"
    path.write_text("old source\n")

    def unavailable(*_args):
        raise OSError("replacement unavailable")

    monkeypatch.setattr("internacia_builder.enrichment.os.replace", unavailable)
    with pytest.raises(OSError, match="replacement unavailable"):
        write_enriched_yaml(path, record, "countries")
    assert path.read_text() == "old source\n"
    assert list(tmp_path.iterdir()) == [path]
