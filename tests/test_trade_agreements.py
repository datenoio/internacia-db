"""Trade agreements registry: schema, validation rules, derived parties and the country view."""

import json

import duckdb
import pytest

from internacia_builder.paths import datasets_dir, project_root
from internacia_builder.trade_agreements import build_trade_agreement_rows, load_trade_agreement_records
from internacia_builder.validate import cross_rules, trade_agreement_rules

ROOT = project_root()
SCHEMA = json.loads((ROOT / "data" / "schemas" / "trade_agreements.schema.json").read_text(encoding="utf-8"))
COUNTRIES = {"AM", "GE", "JP", "SG", "KR", "CN", "FR"}
PROVENANCE = [{"field": "parties", "source": "Treaty text", "retrieved_at": "2026-11-22"}]
INTBLOCKS = [
    {"id": "EU", "name": "European Union", "includes": [
        {"id": "FR", "type": "country", "status": "founding_member"},
        {"id": "GB", "type": "country", "status": "former_member", "left": "2020-01-31"},
    ]},
    {"id": "RCEP", "name": "Regional Comprehensive Economic Partnership", "founded": "2020-11-15",
     "active_period": {"start": "2022-01-01"}, "includes": [
         {"id": "JP", "type": "country", "status": "founding_member", "joined": "2020-11-15"},
         {"id": "KR", "type": "country", "status": "founding_member", "joined": "2020-11-15"},
         {"id": "CN", "type": "country", "status": "founding_member", "joined": "2020-11-15"},
         {"id": "SG", "type": "country", "status": "observer"},
     ]},
    {"id": "PAIR", "name": "Two-party block", "includes": [
        {"id": "JP", "type": "country", "status": "member"},
        {"id": "SG", "type": "country", "status": "member"},
    ]},
]


def _record(**fields):
    record = {
        "id": "AMGE",
        "name": "Armenia-Georgia Free Trade Agreement",
        "agreement_type": "fta",
        "status": "in_force",
        "signed": "1995-08-14",
        "in_force": "1998-11-11",
        "parties": [{"id": "AM", "type": "country"}, {"id": "GE", "type": "country"}],
        "verification": "official",
        "last_verified": "2026-11-22",
        "provenance": PROVENANCE,
    }
    record.update(fields)
    return {k: v for k, v in record.items() if v is not None}


def _types(records, aliases=None):
    paths = [f"data/trade_agreements/{r.get('id')}.yaml" for r in records]
    issues = trade_agreement_rules.check_trade_agreements(records, paths, SCHEMA, INTBLOCKS, COUNTRIES, aliases)
    return sorted(i["issue_type"] for i in issues)


def test_valid_bilateral_record():
    assert _types([_record()]) == []


def test_unknown_status_is_a_schema_error():
    assert _types([_record(status="ratified")]) == ["SCHEMA_ERROR"]


def test_numeric_trade_field_is_rejected():
    assert _types([_record(trade_value_usd=1000)]) == ["SCHEMA_ERROR"]


def test_in_force_without_date():
    assert _types([_record(in_force=None)]) == ["TRADE_AGREEMENT_STATUS_DATE"]


def test_retroactive_entry_into_force_is_allowed():
    """ANZCERTA was signed on 28 March 1983 and applied from 1 January 1983."""
    assert _types([_record(signed="1983-03-28", in_force="1983-01-01")]) == []


def test_applied_provisionally_without_in_force():
    record = _record(in_force=None, provisional_application="2021-01-01")
    assert _types([record]) == []
    agreements, _ = build_trade_agreement_rows([record], INTBLOCKS)
    assert agreements[0]["in_force"] is None
    assert agreements[0]["provisional_application"] == "2021-01-01"


def test_provisional_date_contradicts_signed_status():
    record = _record(status="signed", in_force=None, provisional_application="2024-01-01")
    assert _types([record]) == ["TRADE_AGREEMENT_STATUS_DATE"]


def test_ended_before_provisional_application():
    record = _record(status="terminated", provisional_application="1999-01-01", ended="1998-12-31",
                     in_force=None)
    assert _types([record]) == ["TRADE_AGREEMENT_STATUS_DATE"]


def test_party_joins_on_provisional_application():
    """Norway applied the UK-EEA EFTA agreement from 1 December 2021; it entered into force on 1 September 2022."""
    record = _record(parties=[
        {"id": "AM", "type": "country", "provisional_application": "2021-12-01", "in_force": "2022-09-01"},
        {"id": "GE", "type": "country", "in_force": "2022-09-01"},
    ])
    _, parties = build_trade_agreement_rows([record], INTBLOCKS)
    joined = {p["party_id"]: (p["joined"], p["provisional_application"]) for p in parties}
    assert joined == {"AM": ("2021-12-01", "2021-12-01"), "GE": ("2022-09-01", None)}


def test_linked_record_applied_provisionally_drops_intblock_start():
    record = {"id": "RCEP", "intblock": "RCEP", "agreement_type": "fta", "status": "in_force",
              "provisional_application": "2022-01-01", "verification": "official",
              "last_verified": "2026-11-22", "provenance": PROVENANCE}
    assert _types([record]) == []
    agreements, _ = build_trade_agreement_rows([record], INTBLOCKS)
    assert agreements[0]["in_force"] is None
    assert agreements[0]["provisional_application"] == "2022-01-01"


def test_parties_and_intblock_together():
    assert _types([_record(id="RCEP", intblock="RCEP", name=None, signed=None, in_force=None)]) == ["SCHEMA_ERROR"]


def test_unresolved_party():
    record = _record(parties=[{"id": "AM", "type": "country"}, {"id": "XZ", "type": "country"}])
    assert _types([record]) == ["UNRESOLVED_TRADE_AGREEMENT_PARTY"]


def test_id_collision_with_unrelated_intblock():
    assert _types([_record(id="RCEP")]) == ["TRADE_AGREEMENT_ID_COLLISION"]


def test_linked_record_must_be_official():
    record = {"id": "RCEP", "intblock": "RCEP", "agreement_type": "fta", "status": "in_force",
              "verification": "catalogue", "last_verified": "2026-11-22", "provenance": PROVENANCE}
    assert _types([record]) == ["TRADE_AGREEMENT_VERIFICATION_CONFLICT"]


def test_two_party_intblock_cannot_be_linked():
    record = {"id": "PAIR", "intblock": "PAIR", "agreement_type": "fta", "status": "proposed",
              "verification": "official", "last_verified": "2026-11-22", "provenance": PROVENANCE}
    assert _types([record]) == ["TRADE_AGREEMENT_PARTY_COUNT"]


def test_derived_parties_skip_observers():
    record = {"id": "RCEP", "intblock": "RCEP", "agreement_type": "fta", "status": "in_force",
              "verification": "official", "last_verified": "2026-11-22", "provenance": PROVENANCE}
    agreements, parties = build_trade_agreement_rows([record], INTBLOCKS)
    assert agreements[0]["name"] == "Regional Comprehensive Economic Partnership"
    assert agreements[0]["signed"] == "2020-11-15" and agreements[0]["in_force"] == "2022-01-01"
    assert agreements[0]["party_count"] == 3
    assert {p["party_id"] for p in parties} == {"CN", "JP", "KR"}
    assert {p["source"] for p in parties} == {"intblock"}


def test_linked_record_dates_override_the_intblock():
    record = {"id": "RCEP", "intblock": "RCEP", "agreement_type": "fta", "status": "in_force",
              "in_force": "2022-02-01", "verification": "official", "last_verified": "2026-11-22",
              "provenance": PROVENANCE}
    agreements, _ = build_trade_agreement_rows([record], INTBLOCKS)
    assert agreements[0]["in_force"] == "2022-02-01"
    assert agreements[0]["signed"] == "2020-11-15"


def test_multilateral_without_intblock_is_an_intblock_candidate():
    record = _record(parties=[{"id": c, "type": "country"} for c in ("JP", "KR", "CN")])
    issues = trade_agreement_rules.check_intblock_candidates([record], ["data/trade_agreements/AMGE.yaml"])
    assert [i["issue_type"] for i in issues] == ["TRADE_AGREEMENT_INTBLOCK_CANDIDATE"]


def test_moved_alias_resolves_to_the_registry():
    aliases = [{"alias": "USKR", "target": "USKR", "target_dataset": "trade_agreements", "reason": "moved"}]
    assert cross_rules.validate_aliases(aliases, {"RCEP"}, {"USKR"}) == []
    assert cross_rules.validate_aliases(aliases, {"RCEP"}, set())[0]["issue_type"] == "ALIAS_INTEGRITY_ERROR"
    wrong = [{"alias": "USKR", "target": "USKR", "reason": "moved"}]
    assert cross_rules.validate_aliases(wrong, {"RCEP"}, {"USKR"})


def test_source_records_validate():
    records = load_trade_agreement_records(ROOT)
    assert records, "data/trade_agreements/ has no records"
    assert all(r.get("verification") == "official" for r in records if r.get("intblock"))


@pytest.fixture(scope="module")
def con():
    with duckdb.connect(str(datasets_dir() / "internacia.duckdb"), read_only=True) as connection:
        yield connection


def test_country_view_expands_the_eu(con):
    rows = con.execute(
        "SELECT via FROM country_trade_agreements WHERE country_code = 'FR' AND agreement_id = 'EUJP'"
    ).fetchall()
    assert rows == [("EU",)]


def test_country_view_drops_former_bloc_members(con):
    rows = con.execute(
        "SELECT agreement_id FROM country_trade_agreements WHERE country_code = 'GB' AND agreement_id = 'EUKR'"
    ).fetchall()
    assert rows == []


def test_moved_ids_are_not_intblocks(con):
    moved = {r[0] for r in con.execute("SELECT alias FROM intblocks_aliases WHERE reason = 'moved'").fetchall()}
    assert "USKR" in moved
    assert con.execute("SELECT count(*) FROM intblocks WHERE id IN (SELECT alias FROM intblocks_aliases WHERE reason = 'moved')").fetchone()[0] == 0
    assert con.execute("SELECT count(*) FROM trade_agreements WHERE id = 'USKR'").fetchone()[0] == 1


def test_unparsable_file_is_reported():
    issues = trade_agreement_rules.check_trade_agreement_files([("data/trade_agreements/BAD.yaml", "YAML parse error")])
    assert [(i["issue_type"], i["record_id"]) for i in issues] == [("SCHEMA_ERROR", "BAD")]
