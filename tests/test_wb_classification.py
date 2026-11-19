"""World Bank classification refresh, legacy recoding, and wbgroup roster checks (offline)."""

from copy import deepcopy

import enrich_countries as ec
import pytest

from internacia_builder import wb_classification as wbc
from internacia_builder.paths import project_root
from internacia_builder.validate import registry

TODAY = "2026-11-18"


def wb_row(iso2, iso3, region, admin, income, lending):
    def obj(code, value):
        return {"id": code, "iso2code": "", "value": value}

    return {
        "id": iso3,
        "iso2Code": iso2,
        "region": obj(region, wbc.LABELS["region"].get(region, "") + " "),  # the API pads some labels
        "adminregion": obj(admin, wbc.LABELS["adminregion"].get(admin, "")),
        "incomeLevel": obj(income, wbc.LABELS["incomeLevel"].get(income, "")),
        "lendingType": obj(lending, wbc.LABELS["lendingType"].get(lending, "")),
    }


PAYLOAD = [
    {"page": 1, "pages": 1, "per_page": "1000", "total": 4},
    [
        wb_row("DE", "DEU", "ECS", "", "HIC", "LNX"),
        wb_row("PK", "PAK", "MEA", "MNA", "LMC", "IDB"),
        wb_row("CN", "CHN", "EAS", "EAP", "UMC", "IBD"),
        {
            "id": "WLD",
            "iso2Code": "1W",
            "region": {"id": "NA", "value": "Aggregates"},
            "adminregion": {"id": ""},
            "incomeLevel": {"id": "NA"},
            "lendingType": {"id": ""},
        },
    ],
]


def legacy_country(code="DE", iso3="DEU"):
    return {
        "code": code,
        "iso3code": iso3,
        "name": code,
        "region": {"id": "ECS", "value": "Europe & Central Asia (all income levels)"},
        "adminregion": {"id": "ECA", "value": "Europe & Central Asia (developing only)"},
        "incomeLevel": {"id": "OEC", "value": "High income: OECD"},
        "lendingType": {"id": "NC", "value": "Not classified"},
        "provenance": [
            {
                "field": f,
                "source": "World Bank",
                "retrieved_at": "2026-06-15",
                "url": "https://data.worldbank.org/country",
            }
            for f in ("region", "incomeLevel", "lendingType")
        ]
        + [{"field": "adminregion", "source": "World Bank regional complement", "retrieved_at": "2026-06-15"}],
    }


def test_parse_skips_aggregates_trims_labels_and_nulls_empty_fields():
    parsed = wbc.parse_country_classifications(PAYLOAD)
    assert set(parsed) == {"DE", "PK", "CN"}
    assert parsed["DE"]["region"] == {"id": "ECS", "value": "Europe & Central Asia"}
    assert parsed["DE"]["adminregion"] is None
    assert parsed["PK"]["wb_id"] == "PAK"


def test_parse_refuses_a_paginated_response():
    with pytest.raises(ValueError, match="paginated"):
        wbc.parse_country_classifications([{"pages": 2}, []])


def test_apply_replaces_legacy_codes_and_drops_adminregion_for_high_income():
    record = legacy_country()
    entry = wbc.parse_country_classifications(PAYLOAD)["DE"]
    changed = wbc.apply_world_bank_classification(record, entry, retrieved_at=TODAY)
    assert changed == set(wbc.CLASSIFICATION_FIELDS)
    assert record["incomeLevel"] == {"id": "HIC", "value": "High income"}
    assert record["lendingType"] == {"id": "LNX", "value": "Not classified"}
    assert "adminregion" not in record
    fields = [p["field"] for p in record["provenance"]]
    assert fields == ["region", "incomeLevel", "lendingType"]  # order kept, adminregion entry gone
    assert all(
        p["url"] == "https://api.worldbank.org/v2/country/DEU" and p["retrieved_at"] == TODAY
        for p in record["provenance"]
    )
    assert wbc.apply_world_bank_classification(record, entry, retrieved_at="2027-01-01") == set()
    assert record["provenance"][0]["retrieved_at"] == TODAY  # unchanged values keep their date


def test_refresh_moves_reclassified_economy_and_adds_missing_adminregion():
    record = legacy_country("PK", "PAK")
    record["region"] = {"id": "SAS", "value": "South Asia"}
    del record["adminregion"]
    ec.refresh_classification(record, wbc.parse_country_classifications(PAYLOAD))
    assert record["region"]["id"] == "MEA"
    assert record["adminregion"] == {"id": "MNA", "value": wbc.LABELS["adminregion"]["MNA"]}
    assert wbc.is_wb_classified(record, "adminregion")


def test_modernize_recodes_an_unclassified_entity_and_marks_old_bank_provenance_historical():
    record = legacy_country("AN", "ANT")
    record["incomeLevel"] = {"id": "NOC", "value": "High income: nonOECD"}
    changed = ec.refresh_classification(record, wbc.parse_country_classifications(PAYLOAD))
    assert changed == set(wbc.CLASSIFICATION_FIELDS)
    assert record["region"] == {"id": "ECS", "value": "Europe & Central Asia"}
    assert record["incomeLevel"] == {"id": "HIC", "value": "High income"}
    assert record["lendingType"]["id"] == "LNX"
    assert "adminregion" not in record
    assert {p["source"] for p in record["provenance"]} == {wbc.WB_HISTORICAL_SOURCE}
    assert not wbc.is_wb_classified(record, "incomeLevel")
    assert wbc.modernize_classification(deepcopy(record)) == set()


def test_modernize_keeps_inferred_middle_income_adminregion_with_current_label():
    record = {
        "code": "EH",
        "adminregion": {"id": "MEA", "value": "Middle East & North Africa (excluding high income)"},
        "incomeLevel": {"id": "LMC", "value": "Lower middle income"},
        "provenance": [{"field": "adminregion", "source": "UN M49 inference", "retrieved_at": "2026-06-15"}],
    }
    wbc.modernize_classification(record)
    assert record["adminregion"] == {"id": "MNA", "value": wbc.LABELS["adminregion"]["MNA"]}
    assert record["provenance"][0]["source"] == "UN M49 inference"


def test_inference_emits_current_codes_and_no_adminregion_for_high_income():
    inferred = ec.infer_wb_classification({"code": "AI", "subregion": "Caribbean", "continents": ["North America"]})
    assert inferred["incomeLevel"] == {"id": "HIC", "value": "High income"}
    assert inferred["lendingType"]["id"] == "LNX"
    assert "adminregion" not in inferred
    eh = ec.infer_wb_classification({"code": "EH", "subregion": "Northern Africa", "continents": ["Africa"]})
    assert eh["adminregion"]["id"] == "MNA"
    assert (
        ec.infer_adminregion_from_region({"code": "AI", "region": {"id": "LCN"}, "incomeLevel": {"id": "HIC"}}) is None
    )


def test_enrich_record_without_a_classification_fetch_leaves_bank_fields_alone():
    record = legacy_country()
    result = ec.enrich_record(deepcopy(record), {"population": {}, "area": {}, "gini": {}}, {}, {})
    assert result["incomeLevel"] == record["incomeLevel"]
    assert {p["source"] for p in result["provenance"] if p["field"] == "region"} == {"World Bank"}


def classified(code, region, income, admin=None):
    record = {
        "code": code,
        "name": f"Country {code}",
        "region": {"id": region},
        "incomeLevel": {"id": income},
        "provenance": [{"field": "region", "source": "World Bank"}, {"field": "incomeLevel", "source": "World Bank"}],
    }
    if admin:
        record["adminregion"] = {"id": admin}
        record["provenance"].append({"field": "adminregion", "source": "World Bank"})
    return record


COUNTRIES = {
    "AA": classified("AA", "SAS", "LIC", "SAS"),
    "BB": classified("BB", "SAS", "HIC"),
    "CC": classified("CC", "ECS", "HIC"),
    "ZZ": {
        "code": "ZZ",
        "region": {"id": "SAS"},
        "incomeLevel": {"id": "HIC"},
        "provenance": [{"field": "region", "source": "UN M49 inference"}],
    },
}


def block(block_id, *codes):
    return {
        "id": block_id,
        "blocktype": ["wbgroup"],
        "membership_count": len(codes),
        "includes": [{"id": c, "name": c, "type": "country", "status": "member"} for c in codes],
    }


def test_group_members_follow_bank_classified_fields_only():
    assert wbc.wb_group_members(COUNTRIES.values(), "SAS") == {"AA", "BB"}
    assert wbc.wb_group_members(COUNTRIES.values(), "HIC") == {"BB", "CC"}
    assert wbc.wb_group_members(COUNTRIES.values(), "LMY") == {"AA"}


def test_sync_rebuilds_a_stale_roster_and_keeps_retained_entries():
    stale = block("HIC", "BB", "DD")
    stale["includes"][0]["name"] = "Old label"
    stale["includes"][0]["joined"] = "1990"
    assert wbc.sync_wb_group_block(stale, COUNTRIES, retrieved_at=TODAY)
    assert [i["id"] for i in stale["includes"]] == ["BB", "CC"]
    assert stale["includes"][0] == {"id": "BB", "name": "Country BB", "type": "country", "status": "member", "joined": "1990"}
    assert stale["includes"][1]["name"] == "Country CC"
    assert stale["membership_count"] == 2
    assert stale["last_verified"] == TODAY
    assert {p["field"]: p["url"] for p in stale["provenance"]} == {
        "includes": "https://api.worldbank.org/v2/country?incomelevel=HIC",
        "membership_count": "https://api.worldbank.org/v2/country?incomelevel=HIC",
    }
    assert not wbc.sync_wb_group_block(stale, COUNTRIES, retrieved_at="2027-01-01")


def test_roster_check_reports_missing_and_extra_members():
    records = [block("SAS", "AA", "CC"), block("HIC", "BB", "CC"), {**block("SAS", "ZZ"), "blocktype": ["geographic"]}]
    issues = wbc.check_wb_group_rosters(records, ["sas.yaml", "hic.yaml", "geo.yaml"], COUNTRIES)
    assert [(i["file_path"], i["current_value"]) for i in issues] == [("sas.yaml", "BB"), ("sas.yaml", "CC")]
    assert "not listed in SAS" in issues[0]["suggested_action"]
    assert "whose World Bank region is 'ECS'" in issues[1]["suggested_action"]
    assert all(i["issue_type"] == "WB_GROUP_ROSTER_MISMATCH" for i in issues)


def test_roster_rule_is_registered_and_the_repository_is_consistent():
    rule = next(r for r in registry.INTBLOCK_RULES if r.name == "World Bank group rosters")
    ctx = registry.load_context(project_root())
    assert rule.check(ctx) == []
