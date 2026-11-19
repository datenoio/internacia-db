"""Unit tests for builder.clean_data normalization."""

import pytest

from internacia_builder import build as builder


def test_yaml_booleans_in_text_fields_fail_instead_of_becoming_yes_or_no():
    cases = [
        ({"id": "X", "languages": ["en", False, "sv"]}, "intblocks", "X: languages"),
        ({"id": "X", "includes": [{"id": False, "type": "country", "status": "member"}]}, "intblocks", "X: includes.id"),
        ({"id": "X", "name": True}, "intblocks", "X: name"),
        ({"id": "intorg", "name": False}, "blocktypes", "intorg: name"),
    ]
    for record, dataset, message in cases:
        with pytest.raises(ValueError, match=message):
            builder.clean_data([record], dataset)


def test_coordinates_are_never_fabricated():
    country = builder.clean_data([{"code": "AA", "capital_city": {"name": "A", "lat": "12.5"}}], "countries")[0]
    assert country["capital_city"] == {"name": "A", "lat": 12.5, "lng": None}
    with pytest.raises(ValueError, match="AA: capital_city.lat is not a number"):
        builder.clean_data([{"code": "AA", "capital_city": {"name": "A", "lat": "north", "lng": 1}}], "countries")
    block = builder.clean_data([{"id": "X", "headquarters": {"coordinates": {"lat": None, "lng": 3.0}}}], "intblocks")[0]
    assert block["headquarters"]["coordinates"] == {"lat": None, "lng": 3.0}


def test_intblocks_partof_string_becomes_list():
    data = [{"id": "X", "partof": "AFUNION"}]
    out = builder.clean_data(data, "intblocks")
    assert out[0]["partof"] == ["AFUNION"]


def test_intblocks_partof_none_becomes_empty_list():
    data = [{"id": "X", "partof": None}]
    out = builder.clean_data(data, "intblocks")
    assert out[0]["partof"] == []


def test_intblocks_none_string_fields_become_empty():
    data = [{"id": "X", "description": None, "status": None}]
    out = builder.clean_data(data, "intblocks")
    assert out[0]["description"] == ""
    assert out[0]["status"] == ""


def test_intblocks_includes_values_stringified():
    data = [{"id": "X", "includes": [{"id": "NO", "name": None, "type": "country", "status": "member"}]}]
    out = builder.clean_data(data, "intblocks")
    assert out[0]["includes"][0]["name"] == ""
    assert out[0]["includes"][0]["id"] == "NO"


def test_countries_missing_year_exports_as_none():
    data = [{"code": "AA", "population": {"value": 100, "source": "Wikidata", "source_id": "P1082"}}]
    out = builder.clean_data(data, "countries")
    assert out[0]["population"]["year"] is None


def test_countries_zero_year_exports_as_none():
    data = [{"code": "AA", "area": {"value": 1.0, "year": 0, "source": "x", "source_id": ""}}]
    out = builder.clean_data(data, "countries")
    assert out[0]["area"]["year"] is None


def test_countries_real_year_preserved():
    data = [{"code": "AA", "population": {"value": 100, "year": 2024, "source": "WB", "source_id": "S"}}]
    out = builder.clean_data(data, "countries")
    assert out[0]["population"]["year"] == 2024


def test_countries_legacy_numeric_population_struct():
    data = [{"code": "AA", "population": 12345}]
    out = builder.clean_data(data, "countries")
    assert out[0]["population"] == {
        "value": 12345,
        "year": None,
        "source": "legacy",
        "source_id": "",
    }


def test_countries_none_borders_become_empty_list():
    data = [{"code": "AA", "borders": None}]
    out = builder.clean_data(data, "countries")
    assert out[0]["borders"] == []


def test_countries_whitespace_stripped():
    data = [{"code": "AA", "subregion": " Northern Europe ", "region": {"id": "X", "value": " Europe "}}]
    out = builder.clean_data(data, "countries")
    assert out[0]["subregion"] == "Northern Europe"
    assert out[0]["region"]["value"] == "Europe"
