"""The intblock ``institutional_design`` object: schema, catalog, rules, and exports."""

import copy
import json

import duckdb
import pyarrow as pa
import pyarrow.parquet as pq
import pytest
import yaml

from internacia_builder import contract
from internacia_builder.export import flatten_intblock, save_parquet
from internacia_builder.paths import project_root
from internacia_builder.schemas import get_intblocks_schema
from internacia_builder.validate import intblock_rules

SCHEMAS = project_root() / "data" / "schemas"
INTBLOCK_SCHEMA = json.loads((SCHEMAS / "intblocks.schema.json").read_text(encoding="utf-8"))
CATALOG = yaml.safe_load((SCHEMAS / "institutional_design.yaml").read_text(encoding="utf-8"))
DESIGN_SCHEMA = INTBLOCK_SCHEMA["properties"]["institutional_design"]

BASE_RECORD = {
    "id": "TESTORG",
    "name": "Test Organization",
    "blocktype": ["political"],
    "status": "formal",
    "scope_category": "igo",
    "description": "A test organization.",
    "includes": [
        {"id": "US", "name": "United States", "type": "country", "status": "founding_member"},
        {"id": "FR", "name": "France", "type": "country", "status": "member"},
        {"id": "DE", "name": "Germany", "type": "country", "status": "observer"},
        {"id": "GB", "name": "United Kingdom", "type": "country", "status": "member", "left": "2020-01-31"},
    ],
    "institutional_design": {
        "mandate": "general",
        "decision_rule": "qualified_majority",
        "decision_force": "binding",
        "independent_organs": ["executive", "court"],
        "enforcement": ["suspension"],
        "mutual_defence": False,
        "veto_holders": ["US"],
    },
    "provenance": [
        {
            "field": "institutional_design",
            "source": "Founding treaty",
            "url": "https://example.org/treaty",
            "retrieved_at": "2026-11-20",
        }
    ],
}


def _record(**design_overrides):
    record = copy.deepcopy(BASE_RECORD)
    record["institutional_design"].update(design_overrides)
    return record


def _issue_types(issues):
    return sorted(issue["issue_type"] for issue in issues)


# --- schema -------------------------------------------------------------------


def test_valid_record_passes_schema():
    assert intblock_rules.check_intblock_schema(BASE_RECORD, INTBLOCK_SCHEMA) == []


def test_record_without_object_passes_schema():
    record = copy.deepcopy(BASE_RECORD)
    del record["institutional_design"]
    assert intblock_rules.check_intblock_schema(record, INTBLOCK_SCHEMA) == []


def test_partial_object_passes_schema():
    record = copy.deepcopy(BASE_RECORD)
    record["institutional_design"] = {"mandate": "technical", "decision_force": "partly_binding"}
    assert intblock_rules.check_intblock_schema(record, INTBLOCK_SCHEMA) == []


@pytest.mark.parametrize(
    "design",
    [
        {"mandate": "general", "influence": "high"},  # unknown subfield
        {"decision_rule": "majority"},  # unknown enum value
        {"independent_organs": ["court", "court"]},  # duplicate list value
        {"enforcement": []},  # empty list: use [none]
        {"mutual_defence": "yes"},  # not a boolean
        {"veto_holders": ["USA"]},  # not alpha-2
        {},  # empty object
    ],
)
def test_invalid_object_fails_schema(design):
    record = copy.deepcopy(BASE_RECORD)
    record["institutional_design"] = design
    assert intblock_rules.check_intblock_schema(record, INTBLOCK_SCHEMA)


def test_schema_enums_match_catalog():
    fields = CATALOG["fields"]
    assert set(fields) == set(DESIGN_SCHEMA["properties"])
    for name, spec in DESIGN_SCHEMA["properties"].items():
        enum = spec.get("enum") or (spec.get("items") or {}).get("enum")
        if enum is None:
            assert "values" not in fields[name], name
            continue
        assert set(enum) == set(fields[name]["values"]), name


def test_every_catalog_value_is_described():
    for name, field in CATALOG["fields"].items():
        assert field.get("description"), name
        for value, spec in (field.get("values") or {}).items():
            assert spec.get("name") and spec.get("description"), f"{name}.{value}"


def test_contract_lists_open_design_enums():
    enums = contract.build_contract("0.0.0")["enums"]
    columns = {e["column"]: e for e in enums if e["table"] == "intblocks"}
    for column in (
        "institutional_design.mandate",
        "institutional_design.decision_rule",
        "institutional_design.decision_force",
        "institutional_design.independent_organs[]",
        "institutional_design.enforcement[]",
    ):
        assert column in columns, column
        assert columns[column]["open"] is True


# --- record rules -------------------------------------------------------------


def test_valid_record_passes_rules():
    assert intblock_rules.check_intblock_institutional_design(BASE_RECORD) == []
    assert intblock_rules.check_intblock_veto_under_consensus(BASE_RECORD) == []


def test_record_without_object_passes_rules():
    record = copy.deepcopy(BASE_RECORD)
    del record["institutional_design"]
    assert intblock_rules.check_intblock_institutional_design(record) == []


@pytest.mark.parametrize("category", ["reference_enumeration", "non_state_organization", None])
def test_scope_conflict(category):
    record = copy.deepcopy(BASE_RECORD)
    record["scope_category"] = category
    issues = intblock_rules.check_intblock_institutional_design(record)
    assert _issue_types(issues) == ["INSTITUTIONAL_DESIGN_SCOPE_CONFLICT"]


@pytest.mark.parametrize("category", ["igo", "treaty_body", "policy_forum", "intergovernmental_body"])
def test_allowed_scope(category):
    record = copy.deepcopy(BASE_RECORD)
    record["scope_category"] = category
    assert intblock_rules.check_intblock_institutional_design(record) == []


@pytest.mark.parametrize("field", ["independent_organs", "enforcement"])
def test_none_must_stand_alone(field):
    record = _record(**{field: ["none", "court" if field == "independent_organs" else "suspension"]})
    issues = intblock_rules.check_intblock_institutional_design(record)
    assert _issue_types(issues) == ["INSTITUTIONAL_DESIGN_NONE_CONFLICT"]
    assert issues[0]["field"] == f"institutional_design.{field}"


def test_none_alone_is_valid():
    record = _record(independent_organs=["none"], enforcement=["none"])
    assert intblock_rules.check_intblock_institutional_design(record) == []


@pytest.mark.parametrize(
    "code",
    [
        "CN",  # not in includes
        "DE",  # observer, not a member
        "GB",  # former member (left date)
    ],
)
def test_veto_holder_must_be_current_member(code):
    record = _record(veto_holders=["US", code])
    issues = intblock_rules.check_intblock_institutional_design(record)
    assert _issue_types(issues) == ["INVALID_VETO_HOLDER"]
    assert issues[0]["current_value"] == code


def test_missing_provenance():
    record = copy.deepcopy(BASE_RECORD)
    record["provenance"] = [{"field": "headquarters", "source": "x", "retrieved_at": "2026-11-20"}]
    issues = intblock_rules.check_intblock_institutional_design(record)
    assert _issue_types(issues) == ["MISSING_INSTITUTIONAL_DESIGN_PROVENANCE"]


def test_subfield_provenance_satisfies_rule():
    record = copy.deepcopy(BASE_RECORD)
    record["provenance"][0]["field"] = "institutional_design.decision_rule"
    assert intblock_rules.check_intblock_institutional_design(record) == []


def test_prefix_lookalike_does_not_satisfy_rule():
    record = copy.deepcopy(BASE_RECORD)
    record["provenance"][0]["field"] = "institutional_design_notes"
    issues = intblock_rules.check_intblock_institutional_design(record)
    assert _issue_types(issues) == ["MISSING_INSTITUTIONAL_DESIGN_PROVENANCE"]


@pytest.mark.parametrize("rule", ["consensus", "unanimity"])
def test_veto_under_consensus_warns(rule):
    record = _record(decision_rule=rule)
    issues = intblock_rules.check_intblock_veto_under_consensus(record)
    assert _issue_types(issues) == ["VETO_HOLDERS_UNDER_CONSENSUS"]


def test_rules_are_registered():
    from internacia_builder.validate import registry

    by_name = {rule.name: rule for rule in registry.RULES[registry.INTBLOCKS]}
    assert by_name["institutional design"].severity == "error"
    assert by_name["veto holders under consensus"].severity == "warning"


# --- exports ------------------------------------------------------------------


def _arrow_rows():
    absent = copy.deepcopy(BASE_RECORD)
    absent["id"] = "ABSENT"
    del absent["institutional_design"]
    partial = copy.deepcopy(BASE_RECORD)
    partial["id"] = "PARTIAL"
    partial["institutional_design"] = {"mandate": "technical"}
    return [BASE_RECORD, absent, partial]


def test_struct_is_last_export_column():
    schema = get_intblocks_schema()
    assert schema.names[-1] == "institutional_design"
    struct = schema.field("institutional_design").type
    assert pa.types.is_struct(struct)
    assert [struct.field(i).name for i in range(struct.num_fields)] == list(DESIGN_SCHEMA["properties"])


def test_parquet_and_duckdb_round_trip(tmp_path):
    out = tmp_path / "intblocks.parquet"
    save_parquet(_arrow_rows(), out, schema=get_intblocks_schema())
    table = pq.read_table(out, columns=["id", "institutional_design"]).to_pylist()
    by_id = {row["id"]: row["institutional_design"] for row in table}
    assert by_id["TESTORG"]["enforcement"] == ["suspension"]
    assert by_id["TESTORG"]["mutual_defence"] is False
    assert by_id["ABSENT"] is None
    assert by_id["PARTIAL"]["mandate"] == "technical"
    assert by_id["PARTIAL"]["decision_rule"] is None

    con = duckdb.connect()
    try:
        rows = con.execute(
            "SELECT id, institutional_design.decision_rule, institutional_design.veto_holders "
            f"FROM read_parquet('{out}') ORDER BY id"
        ).fetchall()
    finally:
        con.close()
    assert rows == [
        ("ABSENT", None, None),
        ("PARTIAL", None, None),
        ("TESTORG", "qualified_majority", ["US"]),
    ]


def test_flattened_csv_columns():
    row = flatten_intblock(_record(enforcement=["suspension", "expulsion"]))
    assert row["design_enforcement"] == "suspension;expulsion"
    assert row["design_mandate"] == "general"
    assert row["design_mutual_defence"] is False
    assert row["design_veto_holders"] == "US"

    absent = copy.deepcopy(BASE_RECORD)
    del absent["institutional_design"]
    row = flatten_intblock(absent)
    assert row["design_enforcement"] == ""
    assert row["design_mutual_defence"] is None


def test_lite_exports_unchanged():
    from internacia_builder.export import INTBLOCKS_LITE_FIELDS

    assert not any(field.startswith("design_") for field in INTBLOCKS_LITE_FIELDS)
