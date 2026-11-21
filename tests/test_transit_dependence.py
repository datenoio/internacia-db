"""Transit dependence layer: include roles, border crossing status, exports and the view."""

import copy
import json

import duckdb
import pyarrow as pa
import pytest

from internacia_builder import contract
from internacia_builder.export import build_membership_rows, load_border_status, save_border_status
from internacia_builder.paths import project_root
from internacia_builder.schemas import get_border_status_schema, get_memberships_schema
from internacia_builder.validate import border_rules, intblock_rules, registry
from internacia_builder.yaml_io import safe_load

SCHEMAS = project_root() / "data" / "schemas"
INTBLOCK_SCHEMA = json.loads((SCHEMAS / "intblocks.schema.json").read_text(encoding="utf-8"))
BORDER_SCHEMA = json.loads((SCHEMAS / "border_status.schema.json").read_text(encoding="utf-8"))
ROLES = safe_load((SCHEMAS / "include_roles.yaml").read_text(encoding="utf-8"))

PROVENANCE = [{"field": "includes", "source": "Operator", "url": "https://example.org", "retrieved_at": "2026-11-20"}]
PIPELINE = {
    "id": "TESTPIPE",
    "name": "Test pipeline",
    "blocktype": ["gaspipeline"],
    "status": "de-facto",
    "description": "A test pipeline.",
    "includes": [
        {"id": "AZ", "name": "Azerbaijan", "type": "country", "status": "member", "role": "origin"},
        {"id": "GE", "name": "Georgia", "type": "country", "status": "member", "role": "transit"},
        {"id": "TR", "name": "Türkiye", "type": "country", "status": "member", "role": "destination"},
    ],
    "provenance": PROVENANCE,
}
CORRIDOR = {
    "id": "TESTCORR",
    "name": "Test corridor",
    "blocktype": ["project", "corridor"],
    "status": "formal",
    "scope_category": "policy_forum",
    "description": "A test corridor.",
    "includes": [
        {"id": "CN", "name": "China", "type": "country", "status": "member", "role": "terminal"},
        {"id": "KG", "name": "Kyrgyzstan", "type": "country", "status": "member", "role": "transit"},
        {"id": "UZ", "name": "Uzbekistan", "type": "country", "status": "member", "role": "terminal"},
    ],
    "provenance": PROVENANCE,
}


def _types(issues):
    return sorted(issue["issue_type"] for issue in issues)


def _with_roles(record, **roles):
    out = copy.deepcopy(record)
    for inc in out["includes"]:
        if inc["id"] in roles:
            if roles[inc["id"]] is None:
                inc.pop("role", None)
            else:
                inc["role"] = roles[inc["id"]]
    return out


# --- include roles ------------------------------------------------------------


def test_role_catalog_matches_schema():
    enum = set(INTBLOCK_SCHEMA["properties"]["includes"]["items"]["properties"]["role"]["enum"])
    assert set(ROLES["roles"]) == enum
    used = {role for kind in ROLES["kinds"].values() for role in kind["roles"]}
    assert used == enum


def test_role_kinds_name_existing_blocktypes():
    blocktypes = {b["id"] for b in safe_load((project_root() / "data" / "blocktypes" / "blocktypes.yaml").read_text())}
    for kind in ROLES["kinds"].values():
        assert set(kind["blocktypes"]) <= blocktypes


@pytest.mark.parametrize("record", [PIPELINE, CORRIDOR])
def test_valid_routes_pass(record):
    assert intblock_rules.check_intblock_schema(record, INTBLOCK_SCHEMA) == []
    assert intblock_rules.check_intblock_include_roles(record, ROLES) == []


def test_oilpipeline_uses_pipeline_roles():
    record = copy.deepcopy(PIPELINE)
    record["blocktype"] = ["oilpipeline"]
    assert intblock_rules.check_intblock_include_roles(record, ROLES) == []


def test_record_without_roles_passes():
    record = copy.deepcopy(PIPELINE)
    for inc in record["includes"]:
        inc.pop("role")
    assert intblock_rules.check_intblock_include_roles(record, ROLES) == []


def test_unknown_role_fails_schema():
    record = _with_roles(PIPELINE, GE="supplier")
    assert intblock_rules.check_intblock_schema(record, INTBLOCK_SCHEMA)


def test_role_on_non_infrastructure_record():
    record = copy.deepcopy(PIPELINE)
    record["blocktype"] = ["political"]
    assert _types(intblock_rules.check_intblock_include_roles(record, ROLES)) == ["INCLUDE_ROLE_NOT_ALLOWED"]


def test_role_on_organization_entry():
    record = copy.deepcopy(PIPELINE)
    record["includes"].append({"id": "EU", "type": "organization", "status": "member", "role": "transit"})
    assert "INCLUDE_ROLE_NOT_ALLOWED" in _types(intblock_rules.check_intblock_include_roles(record, ROLES))


@pytest.mark.parametrize(
    "record,roles",
    [(PIPELINE, {"GE": "terminal"}), (CORRIDOR, {"CN": "origin"})],
)
def test_role_value_must_match_kind(record, roles):
    issues = intblock_rules.check_intblock_include_roles(_with_roles(record, **roles), ROLES)
    assert "INVALID_INCLUDE_ROLE" in _types(issues)


def test_partial_roles():
    issues = intblock_rules.check_intblock_include_roles(_with_roles(PIPELINE, GE=None), ROLES)
    assert _types(issues) == ["INCOMPLETE_INCLUDE_ROLES"]
    assert issues[0]["current_value"] == "GE"


def test_former_member_needs_no_role():
    record = copy.deepcopy(PIPELINE)
    record["includes"].append({"id": "IR", "type": "country", "status": "former_member", "left": "2010"})
    assert intblock_rules.check_intblock_include_roles(record, ROLES) == []


@pytest.mark.parametrize(
    "record,roles",
    [(PIPELINE, {"TR": "transit"}), (CORRIDOR, {"UZ": "transit"})],
)
def test_missing_endpoint(record, roles):
    issues = intblock_rules.check_intblock_include_roles(_with_roles(record, **roles), ROLES)
    assert _types(issues) == ["MISSING_ROUTE_ENDPOINT"]


def test_missing_route_provenance():
    record = copy.deepcopy(PIPELINE)
    record["provenance"] = [{"field": "wikidata_id", "source": "Wikidata", "retrieved_at": "2026-11-20"}]
    assert _types(intblock_rules.check_intblock_include_roles(record, ROLES)) == ["MISSING_ROLE_PROVENANCE"]


def test_role_rule_registered():
    rules = {rule.name: rule for rule in registry.RULES[registry.INTBLOCKS]}
    assert rules["include roles"].severity == "error"


def test_memberships_carry_role():
    rows = build_membership_rows([PIPELINE])
    assert {row["country_code"]: row["role"] for row in rows} == {"AZ": "origin", "GE": "transit", "TR": "destination"}
    assert get_memberships_schema().names[-1] == "role"


def test_contract_lists_role_enums():
    enums = {(e["table"], e["column"]): e for e in contract.build_contract("0.0.0")["enums"]}
    for key in (("intblocks", "includes[].role"), ("memberships", "role"), ("current_memberships", "role")):
        assert enums[key]["open"] is True
        assert set(enums[key]["values"]) == set(ROLES["roles"])


# --- border status --------------------------------------------------------------

COUNTRIES = [
    {"code": "AM", "iso3code": "ARM", "borders": ["AZE", "GEO", "IRN", "TUR"]},
    {"code": "AZ", "iso3code": "AZE", "borders": ["ARM", "GEO", "IRN", "RUS", "TUR"]},
    {"code": "TR", "iso3code": "TUR", "borders": ["ARM", "AZE", "GEO"]},
    {"code": "GE", "iso3code": "GEO", "borders": ["ARM", "AZE", "TUR"]},
    {"code": "FR", "iso3code": "FRA", "borders": []},
]
SOURCE = [{"source": "Government", "url": "https://example.org", "retrieved_at": "2026-11-20"}]


def _entry(countries=("ARM", "TUR"), **extra):
    return {"countries": list(countries), "status": "closed", "last_verified": "2026-11-20", "provenance": SOURCE, **extra}


def _check(*entries):
    return border_rules.check_border_status({"entries": list(entries)}, BORDER_SCHEMA, COUNTRIES)


def test_repository_border_status_is_valid():
    path = project_root() / "data" / "borders" / "border_status.yaml"
    document = safe_load(path.read_text(encoding="utf-8"))
    countries = [safe_load(p.read_text(encoding="utf-8")) for p in (project_root() / "data" / "countries").glob("*.yaml")]
    assert border_rules.check_border_status(document, BORDER_SCHEMA, countries) == []


def test_valid_current_and_ended_entries():
    assert _check(_entry()) == []
    assert _check(_entry(since="1990", until="1992")) == []


@pytest.mark.parametrize(
    "entry",
    [
        _entry(status="partially_open"),
        {k: v for k, v in _entry().items() if k != "provenance"},
        _entry(provenance=[]),
        _entry(extra_field=True),
    ],
)
def test_schema_rejects(entry):
    assert _types(_check(entry)) == ["SCHEMA_ERROR"]


@pytest.mark.parametrize("pair", [("TUR", "ARM"), ("ARM", "ARM"), ("ARM", "ZZZ")])
def test_unresolved_pair(pair):
    assert _types(_check(_entry(pair))) == ["UNRESOLVED_BORDER_STATUS_PAIR"]


def test_not_adjacent():
    assert _types(_check(_entry(("ARM", "FRA")))) == ["BORDER_STATUS_NOT_ADJACENT"]


@pytest.mark.parametrize(
    "entries",
    [
        (_entry(), _entry(status="restricted")),  # two entries for one border
        (_entry(since="2000", until="2010"), _entry(since="2005", until="2015")),  # overlap
        (_entry(until="2010"),),  # until without since
        (_entry(since="2012", until="2010"),),  # since after until
        (_entry(), _entry(since="1990", until="1992")),  # history without a dated current entry
    ],
)
def test_period_conflicts(entries):
    assert set(_types(_check(*entries))) == {"BORDER_STATUS_PERIOD_CONFLICT"}


def test_staleness_warning():
    stale = {"entries": [_entry(last_verified="2020-01-01")]}
    assert _types(border_rules.check_border_status_freshness(stale, 12)) == ["STALE_BORDER_STATUS"]
    assert border_rules.check_border_status_freshness(stale, 0) == []


def test_border_rules_registered():
    rules = {rule.name: rule for rule in registry.RULES[registry.COUNTRIES]}
    assert rules["border status"].severity == "error"
    assert rules["border status freshness"].severity == "warning"


def test_country_records_gain_no_border_status_field():
    schema = json.loads((SCHEMAS / "countries.schema.json").read_text(encoding="utf-8"))
    assert not any("status" in name and "border" in name for name in schema["properties"])


# --- export and view -----------------------------------------------------------


def test_border_status_export_round_trip(tmp_path):
    rows = load_border_status(project_root())
    assert rows and all(r["country_a"] < r["country_b"] for r in rows)
    save_border_status(rows, tmp_path)
    assert json.loads((tmp_path / "border_status.json").read_text()) == rows
    con = duckdb.connect()
    try:
        con.execute(f"CREATE TABLE border_status AS SELECT * FROM read_parquet('{tmp_path / 'border_status.parquet'}')")
        countries = pa.Table.from_pylist([
            {"code": c["code"], "iso3code": c["iso3code"], "borders": c["borders"]} for c in COUNTRIES
        ])
        con.register("countries", countries)
        view = next(v for v in contract.VIEWS if v["name"] == "country_borders")
        got = con.execute(f"SELECT * FROM ({view['sql']}) WHERE country_code = 'AM'").fetchall()
    finally:
        con.close()
    assert got == [("AM", "ARM", "AZE", "closed"), ("AM", "ARM", "GEO", None),
                   ("AM", "ARM", "IRN", None), ("AM", "ARM", "TUR", "closed")]


def test_ended_closure_is_not_current(tmp_path):
    rows = [{**r, "since": "1990", "until": "1999"} for r in load_border_status(project_root()) if r["country_a"] == "ARM"]
    save_border_status(rows, tmp_path)
    con = duckdb.connect()
    try:
        con.execute(f"CREATE TABLE border_status AS SELECT * FROM read_parquet('{tmp_path / 'border_status.parquet'}')")
        con.register("countries", pa.Table.from_pylist([{"code": "AM", "iso3code": "ARM", "borders": ["AZE", "TUR"]}]))
        view = next(v for v in contract.VIEWS if v["name"] == "country_borders")
        statuses = {row[3] for row in con.execute(view["sql"]).fetchall()}
    finally:
        con.close()
    assert statuses == {None}


def test_contract_has_border_status_table_and_view():
    built = contract.build_contract("0.0.0")
    tables = {t["name"]: t for t in built["tables"]}
    assert tables["border_status"]["primary_key"] == ["country_a", "country_b"]
    assert {fk["references"]["columns"][0] for fk in tables["border_status"]["foreign_keys"]} == {"iso3code"}
    assert tables["country_borders"]["kind"] == "view"
    enums = {(e["table"], e["column"]): e["values"] for e in built["enums"]}
    assert set(enums[("border_status", "status")]) == {"closed", "restricted"}
    assert set(enums[("country_borders", "current_status")]) == {"closed", "restricted"}
    assert get_border_status_schema().names[:2] == ["country_a", "country_b"]
