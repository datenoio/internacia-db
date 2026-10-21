"""Reviewed final formal scope cohort and its consumer-facing export contract."""

import duckdb
import yaml

from internacia_builder.paths import project_root

ROOT = project_root()
COUNTRY_PARTICIPANTS = set(
    "AO AR AT BE BR CA CN DK FI FR DE IN IE IT JP KR KW LU NL NO PT SA ES SE CH TR AE GB US".split()
)
SIGNATURE_ONLY = {"AM", "AZ", "ID", "KZ"}
COVERED_NOT_IN_TREATY = {"MY", "SG"}


def _record(directory: str, rid: str) -> dict:
    return yaml.safe_load(
        (ROOT / "data" / "intblocks" / directory / f"{rid}.yaml").read_text(encoding="utf-8")
    )


def _provenance_fields(record: dict) -> set[str]:
    return {str(p["field"]) for p in record["provenance"]}


def test_afdf_is_independent_igo_with_only_verified_state_participants():
    afdf = _record("fund", "AFDF")
    assert afdf["scope_category"] == "igo"
    assert afdf["membership_count"] == len(afdf["includes"]) == 29
    assert {inc["id"] for inc in afdf["includes"]} == COUNTRY_PARTICIPANTS
    assert {inc["status"] for inc in afdf["includes"]} == {"member"}
    assert "partof" not in afdf
    assert {"scope_category", "includes", "membership_count", "notes", "legal_status"} <= _provenance_fields(afdf)


def test_cif_partnership_and_tar_platform_have_no_false_country_memberships():
    for directory, rid, scope in (
        ("fund", "CIF", "intergovernmental_body"),
        ("project", "TAR", "policy_forum"),
    ):
        record = _record(directory, rid)
        assert record["scope_category"] == scope
        assert record["membership_applicability"] == "not_applicable"
        assert "includes" not in record and "membership_count" not in record
        assert {"scope_category", "membership_applicability", "notes"} <= _provenance_fields(record)
        assert "includes" not in _provenance_fields(record)
        assert "membership_count" not in _provenance_fields(record)
    assert "partof" not in _record("fund", "CIF")
    assert _record("project", "TAR")["wikidata_id"] == "Q842463"


def test_separate_trans_asian_railway_treaty_has_22_depositary_parties():
    treaty = _record("transport", "TARAGREEMENT")
    network = _record("project", "TAR")
    assert treaty["name"] == "Intergovernmental Agreement on the Trans-Asian Railway Network"
    assert treaty["scope_category"] == "treaty_body"
    assert treaty["membership_count"] == len(treaty["includes"]) == 22
    ids = {inc["id"] for inc in treaty["includes"]}
    assert ids.isdisjoint(SIGNATURE_ONLY | COVERED_NOT_IN_TREATY)
    assert all(inc["status"] == "member" and inc.get("joined") for inc in treaty["includes"])
    assert treaty["active_period"]["start"] == "2009-06-11"
    assert "wikidata_id" not in treaty and treaty.get("partof") is None
    assert network["wikidata_id"] == "Q842463"
    assert {"scope_category", "includes", "membership_count", "active_period"} <= _provenance_fields(treaty)
    exclusions = yaml.safe_load((ROOT / "data" / "schemas" / "wikidata_exclusions.yaml").read_text())
    assert "TARAGREEMENT" in {row["id"] for row in exclusions["exclusions"]}


def test_retired_telesur_has_no_false_alias_or_source_record():
    assert not (ROOT / "data" / "intblocks" / "telecom" / "TELESUR.yaml").exists()
    aliases = yaml.safe_load((ROOT / "data" / "intblocks_aliases.yaml").read_text())
    assert "TELESUR" not in {row["alias"] for row in aliases}
    assert (ROOT / "docs" / "retired-intblock-ids.md").exists()


def test_exported_memberships_match_the_new_entity_boundaries():
    db = ROOT / "data" / "datasets" / "internacia.duckdb"
    with duckdb.connect(str(db), read_only=True) as con:
        assert con.execute("SELECT count(*) FROM intblocks").fetchone()[0] == 1278
        assert con.execute("SELECT count(*) FROM memberships").fetchone()[0] == 59569
        exported = con.execute(
            "SELECT id, scope_category FROM intblocks WHERE id IN ('AFDF','CIF','TAR','TARAGREEMENT','TELESUR')"
        ).fetchall()
        assert dict(exported) == {
            "AFDF": "igo", "CIF": "intergovernmental_body",
            "TAR": "policy_forum", "TARAGREEMENT": "treaty_body",
        }
        rows = dict(con.execute(
            "SELECT intblock_id, count(*) FROM memberships "
            "WHERE intblock_id IN ('AFDF','CIF','TAR','TARAGREEMENT','TELESUR') "
            "GROUP BY 1"
        ).fetchall())
        assert rows == {"AFDF": 29, "TARAGREEMENT": 22}
