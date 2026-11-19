"""Reviewed final formal scope cohort and its consumer-facing export contract.

These tests pin the reviewed entity boundaries (what each record is and which kind of rows it
may carry), not the rosters themselves: those change with sourced updates and are checked by
validation, provenance and ``last_verified``."""

import json

import duckdb
import yaml

from internacia_builder.paths import datasets_dir, project_root

ROOT = project_root()


def _record(directory: str, rid: str) -> dict:
    return yaml.safe_load(
        (ROOT / "data" / "intblocks" / directory / f"{rid}.yaml").read_text(encoding="utf-8")
    )


def _provenance_fields(record: dict) -> set[str]:
    return {str(p["field"]) for p in record["provenance"]}


def test_afdf_is_independent_igo_with_only_verified_state_participants():
    afdf = _record("fund", "AFDF")
    assert afdf["scope_category"] == "igo"
    assert afdf["includes"] and afdf["membership_count"] == len(afdf["includes"])
    assert {(inc["type"], inc["status"]) for inc in afdf["includes"]} == {("country", "member")}
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


def test_separate_trans_asian_railway_treaty_lists_dated_parties():
    treaty = _record("transport", "TARAGREEMENT")
    network = _record("project", "TAR")
    assert treaty["name"] == "Intergovernmental Agreement on the Trans-Asian Railway Network"
    assert treaty["scope_category"] == "treaty_body"
    assert treaty["includes"] and treaty["membership_count"] == len(treaty["includes"])
    assert all(inc["status"] == "member" and inc.get("joined") for inc in treaty["includes"])
    assert treaty["active_period"]["start"] == "2009-06-11"
    assert "wikidata_id" not in treaty and treaty.get("partof") is None
    assert network["wikidata_id"] == "Q842463"
    assert {"scope_category", "includes", "membership_count", "active_period"} <= _provenance_fields(treaty)
    exclusions = yaml.safe_load((ROOT / "data" / "schemas" / "wikidata_exclusions.yaml").read_text())
    assert "TARAGREEMENT" in {row["id"] for row in exclusions["exclusions"]}


def test_retired_telesur_has_retired_alias_without_target():
    assert not (ROOT / "data" / "intblocks" / "telecom" / "TELESUR.yaml").exists()
    aliases = {row["alias"]: row for row in yaml.safe_load((ROOT / "data" / "intblocks_aliases.yaml").read_text())}
    assert aliases["TELESUR"]["reason"] == "retired"
    assert not aliases["TELESUR"].get("target")
    exported = json.loads((ROOT / "data" / "datasets" / "intblocks_aliases.json").read_text())
    assert {"alias": "TELESUR", "target": None, "reason": "retired"}.items() <= next(
        row for row in exported if row["alias"] == "TELESUR"
    ).items()
    assert (ROOT / "docs" / "retired-intblock-ids.md").exists()


def test_exported_memberships_match_the_new_entity_boundaries():
    db = datasets_dir() / "internacia.duckdb"
    with duckdb.connect(str(db), read_only=True) as con:
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
        expected = {rid: len(_record(d, rid)["includes"]) for d, rid in (("fund", "AFDF"), ("transport", "TARAGREEMENT"))}
        assert rows == expected
