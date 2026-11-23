"""Preference schemes in the trade agreements registry: party roles, sub-schemes and WTO PTA ids.

OpenSpec change ``add-preference-scheme-rosters``.
"""

import json

import duckdb
import pytest

from internacia_builder.paths import datasets_dir, project_root
from internacia_builder.trade_agreements import build_trade_agreement_rows, load_trade_agreement_records
from internacia_builder.validate import trade_agreement_rules

ROOT = project_root()
SCHEMA = json.loads((ROOT / "data" / "schemas" / "trade_agreements.schema.json").read_text(encoding="utf-8"))
COUNTRIES = {"AM", "GE", "BD", "KH", "VU", "PK", "FR", "US", "AO", "NP"}
PROVENANCE = [{"field": "parties", "source": "WTO Preferential Trade Arrangements Database",
               "retrieved_at": "2026-11-23"}]
INTBLOCKS = [
    {"id": "EU", "name": "European Union", "includes": [{"id": "FR", "type": "country", "status": "founding_member"}]},
    {"id": "EAEU", "name": "Eurasian Economic Union", "includes": [{"id": "AM", "type": "country", "status": "member"}]},
    {"id": "GSP", "name": "Generalized System of Preferences", "includes": [
        {"id": "EU", "type": "organization", "status": "contributor"},
        {"id": "AM", "type": "country", "status": "contributor"},
        {"id": "US", "type": "country", "status": "contributor"},
    ]},
    {"id": "AGOA", "name": "African Growth and Opportunity Act", "includes": [
        {"id": "US", "type": "country", "status": "contributor"},
        {"id": "AO", "type": "country", "status": "recipient"},
        {"id": "GE", "type": "country", "status": "recipient"},
    ]},
    {"id": "SPARTECA", "name": "SPARTECA", "includes": [
        {"id": "AM", "type": "country", "status": "contributor"},
        {"id": "GE", "type": "country", "status": "member"},
        {"id": "VU", "type": "country", "status": "recipient"},
    ]},
]


def _scheme(rid="EU-GSP", beneficiaries=("BD", "KH", "PK"), grantor=("EU", "intblock"), **fields):
    record = {
        "id": rid,
        "name": f"Scheme {rid}",
        "agreement_type": "preference_scheme",
        "status": "in_force",
        "in_force": "1971-07-01",
        "parties": [{"id": grantor[0], "type": grantor[1], "role": "grantor"}]
        + [{"id": c, "type": "country", "role": "beneficiary"} for c in beneficiaries],
        "verification": "catalogue",
        "last_verified": "2026-11-23",
        "provenance": PROVENANCE,
    }
    record.update(fields)
    return {k: v for k, v in record.items() if v is not None}


def _linked(rid, **fields):
    record = {"id": rid, "intblock": rid, "agreement_type": "preference_scheme", "status": "in_force",
              "verification": "official", "last_verified": "2026-11-23", "provenance": PROVENANCE}
    record.update(fields)
    return record


def _issues(records):
    paths = [f"data/trade_agreements/{r.get('id')}.yaml" for r in records]
    return trade_agreement_rules.check_preference_schemes(records, paths, INTBLOCKS)


def _types(records):
    return sorted(i["issue_type"] for i in _issues(records))


def test_valid_scheme():
    assert _types([_scheme()]) == []
    paths = ["data/trade_agreements/EU-GSP.yaml"]
    assert trade_agreement_rules.check_trade_agreements(
        [_scheme()], paths, SCHEMA, INTBLOCKS, COUNTRIES) == []


def test_role_value_is_checked_by_the_schema():
    record = _scheme()
    record["parties"][1]["role"] = "donor"
    issues = trade_agreement_rules.check_trade_agreements(
        [record], ["data/trade_agreements/EU-GSP.yaml"], SCHEMA, INTBLOCKS, COUNTRIES)
    assert [i["issue_type"] for i in issues] == ["SCHEMA_ERROR"]


def test_missing_role_on_a_preference_scheme():
    record = _scheme("CN-LDC", grantor=("US", "country"))
    del record["parties"][1]["role"]
    assert _types([record]) == ["TRADE_AGREEMENT_PARTY_ROLE"]


def test_role_on_a_reciprocal_agreement():
    record = _scheme("AMGE", agreement_type="fta", parties=[
        {"id": "AM", "type": "country", "role": "grantor"}, {"id": "GE", "type": "country"}])
    assert _types([record]) == ["TRADE_AGREEMENT_PARTY_ROLE"]


def test_scheme_without_a_beneficiary():
    assert _types([_scheme("IN-DFTP", beneficiaries=())]) == ["TRADE_AGREEMENT_PARTY_ROLE"]


def test_framework_parent_needs_no_beneficiary():
    framework = _scheme("FRAMEWORK", beneficiaries=())
    child = _scheme("EU-GSP", parent="FRAMEWORK")
    assert _types([framework, child]) == []


def test_linked_intblock_with_a_member_status():
    assert _types([_linked("SPARTECA")]) == ["TRADE_AGREEMENT_PARTY_ROLE"]


def test_valid_sub_scheme():
    parent = _scheme("EU-GSP", beneficiaries=("BD", "KH", "PK"))
    child = _scheme("EU-GSP-EBA", beneficiaries=("BD", "KH"), parent="EU-GSP")
    assert _types([parent, child]) == []


def test_beneficiary_outside_the_parent():
    parent = _scheme("EU-GSP", beneficiaries=("BD", "KH"))
    child = _scheme("EU-GSP-EBA", beneficiaries=("BD", "VU"), parent="EU-GSP")
    issues = _issues([parent, child])
    assert [i["issue_type"] for i in issues] == ["TRADE_AGREEMENT_PARENT"]
    assert "VU" in issues[0]["suggested_action"]


def test_former_beneficiary_is_not_checked_against_the_parent():
    parent = _scheme("EU-GSP", beneficiaries=("BD",))
    child = _scheme("EU-GSP-EBA", beneficiaries=("BD",), parent="EU-GSP")
    child["parties"].append({"id": "VU", "type": "country", "role": "beneficiary", "left": "2020-12-04"})
    assert _types([parent, child]) == []


def test_sub_scheme_with_another_grantor():
    parent = _scheme("EU-GSP")
    child = _scheme("EU-GSP-EBA", beneficiaries=("BD",), grantor=("US", "country"), parent="EU-GSP")
    assert _types([parent, child]) == ["TRADE_AGREEMENT_PARENT"]


def test_framework_parent_skips_the_grantor_check():
    child = _scheme("EAEU-GSP", grantor=("EAEU", "intblock"), parent="GSP")
    assert _types([_linked("GSP"), child]) == []


def test_sub_scheme_of_a_linked_scheme():
    child = _scheme("AGOA-APPAREL", beneficiaries=("AO",), grantor=("US", "country"), parent="AGOA")
    assert _types([_linked("AGOA"), child]) == []
    outside = _scheme("AGOA-APPAREL", beneficiaries=("NP",), grantor=("US", "country"), parent="AGOA")
    assert _types([_linked("AGOA"), outside]) == ["TRADE_AGREEMENT_PARENT"]


def test_unresolved_parent():
    assert _types([_scheme(parent="XX-GSP")]) == ["TRADE_AGREEMENT_PARENT"]


def test_parent_must_be_a_preference_scheme():
    fta = _scheme("AMGE", agreement_type="fta", parties=[{"id": "AM", "type": "country"}, {"id": "GE", "type": "country"}])
    assert _types([fta, _scheme(parent="AMGE")]) == ["TRADE_AGREEMENT_PARENT"]


def test_parent_on_a_reciprocal_agreement():
    fta = _scheme("AMGE", agreement_type="fta", parent="EU-GSP",
                  parties=[{"id": "AM", "type": "country"}, {"id": "GE", "type": "country"}])
    assert _types([_scheme(), fta]) == ["TRADE_AGREEMENT_PARENT"]


def test_parent_cycle():
    first = _scheme("A-GSP", parent="B-GSP")
    second = _scheme("B-GSP", parent="A-GSP")
    assert "TRADE_AGREEMENT_PARENT" in _types([first, second])


def test_pta_id_used_twice():
    first = _linked("AGOA", wto_pta_ids=[37])
    second = _scheme("US-AGOA", grantor=("US", "country"), beneficiaries=("AO",), wto_pta_ids=[37])
    assert _types([first, second]) == ["DUPLICATE_WTO_PTA_ID"]


def test_pta_ids_must_be_integers():
    issues = trade_agreement_rules.check_trade_agreements(
        [_scheme(wto_pta_ids=["36"])], ["data/trade_agreements/EU-GSP.yaml"], SCHEMA, INTBLOCKS, COUNTRIES)
    assert [i["issue_type"] for i in issues] == ["SCHEMA_ERROR"]


def test_preference_scheme_is_not_an_intblock_candidate():
    record = _scheme("JP-GSP", grantor=("US", "country"), beneficiaries=("BD", "KH", "PK", "NP"))
    assert trade_agreement_rules.check_intblock_candidates([record], ["data/trade_agreements/JP-GSP.yaml"]) == []


def test_export_roles_parent_and_pta_ids():
    agreements, parties = build_trade_agreement_rows(
        [_scheme(wto_pta_ids=[36], parent="GSP"), _linked("AGOA"),
         _scheme("AMGE", agreement_type="fta", parties=[{"id": "AM", "type": "country"}, {"id": "GE", "type": "country"}])],
        INTBLOCKS,
    )
    by_id = {a["id"]: a for a in agreements}
    assert by_id["EU-GSP"]["wto_pta_ids"] == [36] and by_id["EU-GSP"]["parent"] == "GSP"
    assert by_id["AMGE"]["wto_pta_ids"] == [] and by_id["AMGE"]["parent"] is None
    roles = {(p["agreement_id"], p["party_id"]): p["role"] for p in parties}
    assert roles[("EU-GSP", "EU")] == "grantor" and roles[("EU-GSP", "BD")] == "beneficiary"
    assert roles[("AGOA", "US")] == "grantor" and roles[("AGOA", "AO")] == "beneficiary"
    assert roles[("AMGE", "AM")] == "party"


def test_source_preference_schemes_have_roles():
    for record in load_trade_agreement_records(ROOT):
        if record.get("agreement_type") == "preference_scheme" and record.get("parties"):
            assert all(p.get("role") for p in record["parties"]), record["id"]


@pytest.fixture(scope="module")
def con():
    with duckdb.connect(str(datasets_dir() / "internacia.duckdb"), read_only=True) as connection:
        yield connection


def test_grantor_bloc_is_expanded_with_its_role(con):
    rows = con.execute(
        "SELECT role, via FROM country_trade_agreements WHERE country_code = 'FR' AND agreement_id = 'EU-GSP'"
    ).fetchall()
    assert rows == [("grantor", "EU")]


def test_beneficiary_row(con):
    rows = con.execute(
        "SELECT role, via FROM country_trade_agreements WHERE country_code = 'BD' AND agreement_id = 'EU-GSP'"
    ).fetchall()
    assert rows == [("beneficiary", None)]


def test_reciprocal_agreement_rows_have_role_party(con):
    roles = {r[0] for r in con.execute("SELECT role FROM trade_agreement_parties WHERE agreement_id = 'EUJP'").fetchall()}
    assert roles == {"party"}


def test_sub_scheme_and_pta_ids_are_exported(con):
    assert con.execute("SELECT parent FROM trade_agreements WHERE id = 'GSPPLUS'").fetchone() == ("EU-GSP",)
    assert con.execute("SELECT wto_pta_ids FROM trade_agreements WHERE id = 'EAEU-GSP'").fetchone() == ([87, 96, 98, 100],)


# ---- add-preference-scheme-beneficiary-history ---------------------------------------------

import importlib.util  # noqa: E402

_SPEC = importlib.util.spec_from_file_location("import_wto_ptadb", ROOT / "scripts" / "oneoff" / "import_wto_ptadb.py")
ptadb = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(ptadb)
CODES = {"050": "BD", "116": "KH", "586": "PK", "548": "VU", "024": "AO"}


def _lists(*versions):
    """``(date, [alpha-2...])`` -> the ``(date, entries)`` shape of PTA Database versions."""
    numeric = {v: k for k, v in CODES.items()}
    return [(d, [[numeric[c], c] for c in ids]) for d, ids in versions]


def _dated(*versions, starts_scheme=False, ended=None):
    parties, stats = ptadb.dated_parties(_lists(*versions), CODES, "EU", starts_scheme, ended)
    return {p["id"]: {k: v for k, v in p.items() if k not in ("id", "type", "role")} for p in parties}, stats


def test_history_beneficiary_added_in_a_later_version():
    dated, _ = _dated(("2011-10-25", ["BD"]), ("2013-06-01", ["BD", "KH"]), ("2017-06-30", ["BD", "KH"]))
    assert dated["KH"] == {"in_force": "2013-06-01"}


def test_history_baseline_beneficiary_has_no_start_date():
    dated, stats = _dated(("2011-12-09", ["BD"]), ("2017-06-29", ["BD"]))
    assert dated["BD"] == {}
    assert stats == {"first": "2011-12-09", "last": "2017-06-29", "lists": 2, "former": 0}


def test_history_graduated_beneficiary():
    dated, stats = _dated(("2011-12-09", ["BD", "PK"]), ("2014-01-01", ["BD"]), ("2017-06-29", ["BD"]))
    assert dated["PK"] == {"left": "2014-01-01"}
    assert stats["former"] == 1


def test_history_suspended_and_reinstated_beneficiary():
    dated, _ = _dated(
        ("2011-10-25", ["BD", "AO"]), ("2015-01-01", ["BD"]), ("2018-06-01", ["BD", "AO"]), ("2025-03-21", ["BD", "AO"])
    )
    assert dated["AO"] == {"in_force": "2018-06-01", "note": "Also a beneficiary until 2015-01-01 (listed from 2011-10-25)."}


def test_history_scheme_that_starts_in_the_database():
    dated, _ = _dated(("2023-06-19", ["BD", "KH"]), ("2026-01-01", ["BD", "KH"]), starts_scheme=True)
    assert dated["BD"] == {"in_force": "2023-06-19"}


def test_history_left_after_the_scheme_ended_is_clamped():
    dated, _ = _dated(("2017-01-01", ["BD", "VU"]), ("2022-02-02", ["BD"]), ended="2020-12-31")
    assert dated["VU"] == {"left": "2020-12-31"}


def _dates_types(record):
    return sorted(i["issue_type"] for i in trade_agreement_rules.check_party_dates([record], ["x.yaml"]))


def test_party_joins_before_the_agreement():
    record = _scheme("GB-DCTS", in_force="2023-06-19")
    record["parties"][1]["in_force"] = "2021-01-01"
    assert _dates_types(record) == ["TRADE_AGREEMENT_PARTY_DATE"]


def test_party_leaves_after_the_agreement_ended():
    record = _scheme("US-ATPA", status="terminated", in_force="1991-12-04", ended="2013-07-31")
    record["parties"][1]["left"] = "2014-01-01"
    assert _dates_types(record) == ["TRADE_AGREEMENT_PARTY_DATE"]


def test_party_leaves_before_it_joined():
    record = _scheme()
    record["parties"][1].update({"in_force": "2014-01-01", "left": "2014-01-01"})
    assert _dates_types(record) == ["TRADE_AGREEMENT_PARTY_DATE"]


def test_party_dates_at_different_precision():
    record = _scheme(in_force="2014")
    record["parties"][1]["in_force"] = "2014-01-01"
    assert _dates_types(record) == []


def test_source_records_have_consistent_party_dates():
    records = load_trade_agreement_records(ROOT)
    paths = [f"data/trade_agreements/{r.get('id')}.yaml" for r in records]
    assert trade_agreement_rules.check_party_dates(records, paths) == []
