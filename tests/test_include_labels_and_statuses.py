"""Country include labels come from the country; associate-tier statuses (openspec:
normalize-include-labels-and-statuses)."""

import json

import jsonschema

from internacia_builder.contract import build_contract
from internacia_builder.export import fill_country_include_names
from internacia_builder.paths import project_root
from internacia_builder.validate import completeness, intblock_rules, registry

ROOT = project_root()


def test_build_copies_the_country_name_into_country_includes():
    intblocks = [{"id": "X", "includes": [
        {"id": "MK", "name": "Macedonia, FYR", "type": "country", "status": "member"},
        {"id": "FR", "type": "country", "status": "member"},
        {"id": "EU", "name": "EU", "type": "organization", "status": "member"},
        {"id": "SU", "name": "Soviet Union", "type": "historical-country", "status": "former_member"},
    ]}]
    countries = [{"code": "MK", "name": "North Macedonia"}, {"code": "FR", "name": "France"}]
    names = [i.get("name") for i in fill_country_include_names(intblocks, countries)[0]["includes"]]
    assert names == ["North Macedonia", "France", "EU", "Soviet Union"]


def test_schema_makes_name_optional_only_for_country_includes():
    schema = json.loads((ROOT / "data/schemas/intblocks.schema.json").read_text(encoding="utf-8"))
    item = schema["properties"]["includes"]["items"]
    assert jsonschema.Draft7Validator(item).is_valid({"id": "FR", "type": "country", "status": "member"})
    assert not jsonschema.Draft7Validator(item).is_valid({"id": "EU", "type": "organization", "status": "member"})


def test_deprecated_status_warns_with_replacements():
    catalog = completeness.load_includes_status_catalog(ROOT / "data/schemas")
    record = {"id": "X", "includes": [
        {"id": "FO", "type": "country", "status": "associate"},
        {"id": "AU", "type": "country", "status": "associate_member"},
    ]}
    issues = intblock_rules.check_deprecated_include_statuses(record, catalog)
    assert [(i["issue_type"], i["field"]) for i in issues] == [("DEPRECATED_INCLUDE_STATUS", "includes[0].status")]
    assert "'associate_member' or 'associated'" in issues[0]["suggested_action"]
    rule = next(r for r in registry.INTBLOCK_RULES if r.name == "deprecated include statuses")
    assert rule.severity == registry.W


def test_contract_lists_deprecated_status_values_on_both_columns():
    entries = build_contract("0.0.0")["deprecated"]
    assert {(e["table"], e["column"], e["value"]) for e in entries} == {
        (table, column, value)
        for table, column in (("memberships", "status"), ("intblocks", "includes[].status"))
        for value in ("associate", "associated_observer")
    }
    assert all(e["kind"] == "enum_value" and e["removal"] == "next MAJOR" and e["replacements"] for e in entries)


def test_repository_has_no_stale_country_include_names():
    ctx = registry.load_context(ROOT)
    rule = next(r for r in registry.INTBLOCK_RULES if r.name == "include display names")
    assert rule.check(ctx) == []
