"""Unit tests for validate_intblocks checks."""

import builder
import validate_intblocks as vi

from internacia_builder.paths import project_root
from internacia_builder.validate import completeness as vc

# Fields declared in the JSON Schema but intentionally not exported to Arrow
# (source-only metadata not needed by columnar consumers).
SOURCE_ONLY_INTBLOCK_FIELDS = {
    "abbrRU",
    "listed",
    "translations",
    "founding_members",
    "notes",
    "suborganizations",
    "official_documents",
    "recognition_status",
    "social_media",
    "secretariat",
    "previous_names",
}


def test_intblock_filename_must_match_id():
    records = [
        ("data/intblocks/political/UfM.yaml", {"id": "UfM"}),
        ("data/intblocks/political/UFM.yaml", {"id": "UfM"}),
    ]
    errors = vi.validate_filename_ids(records)
    assert len(errors) == 1
    assert "does not match id 'UfM'" in errors[0]


def test_directory_alignment_requires_dir_in_blocktype():
    records = [
        ("data/intblocks/space/OK.yaml", {"id": "OK", "blocktype": ["agreement", "space"]}),
        ("data/intblocks/space/BAD.yaml", {"id": "BAD", "blocktype": ["agreement"]}),
    ]
    errors = vi.validate_directory_alignment(records)
    assert len(errors) == 1
    assert "space" in errors[0]


def test_intblocks_schema_export_parity():
    """Every Arrow export field must be declared in the JSON Schema."""
    schema = vi.load_json(vi.project_root() / "data" / "schemas" / "intblocks.schema.json")
    declared = set(schema["properties"])
    export_fields = set(builder.get_intblocks_schema().names)
    missing = export_fields - declared
    assert not missing, f"exported intblock fields not declared in JSON Schema: {sorted(missing)}"


def test_check_duplicate_ids():
    records = [
        ("a/X.yaml", {"id": "X"}),
        ("b/X.yaml", {"id": "X"}),
        ("c/Y.yaml", {"id": "Y"}),
    ]
    errors = vi.check_duplicate_ids(records)
    assert len(errors) == 1
    assert "duplicate id 'X'" in errors[0]


def test_validate_blocktypes_unknown_value():
    records = [("a.yaml", {"id": "X", "blocktype": ["bank", "nonsense"]})]
    errors = vi.validate_blocktypes(records, {"bank", "fund"})
    assert len(errors) == 1
    assert "nonsense" in errors[0]


def test_validate_partof_string_reference():
    records = [
        ("a.yaml", {"id": "CHILD", "partof": "PARENT"}),
        ("b.yaml", {"id": "PARENT"}),
    ]
    assert vi.validate_partof_refs(records) == []


def test_validate_partof_unresolved_reference():
    records = [("a.yaml", {"id": "CHILD", "partof": ["MISSING"]})]
    warnings = vi.validate_partof_refs(records)
    assert len(warnings) == 1
    assert "MISSING" in warnings[0]


def test_validate_partof_dict_entries():
    records = [
        ("a.yaml", {"id": "CHILD", "partof": [{"id": "PARENT", "name": "Parent Org"}]}),
        ("b.yaml", {"id": "PARENT"}),
    ]
    assert vi.validate_partof_refs(records) == []


def test_lifecycle_warns_on_ended_field():
    records = [("a.yaml", {"id": "X", "ended": "1995", "status": "historical"})]
    warnings = vi.validate_lifecycle(records)
    assert any("'ended'" in w for w in warnings)


def test_lifecycle_warns_on_dissolved_without_historical_status():
    records = [("a.yaml", {"id": "X", "dissolved": "2009", "status": "formal"})]
    warnings = vi.validate_lifecycle(records)
    assert any("expected 'historical'" in w for w in warnings)


def test_lifecycle_accepts_dissolved_historical():
    records = [("a.yaml", {"id": "X", "dissolved": "2009", "status": "historical"})]
    assert vi.validate_lifecycle(records) == []


def test_schema_validation_against_repo_schema():
    schema = vi.load_json(vi.project_root() / "data" / "schemas" / "intblocks.schema.json")
    good = {
        "id": "TESTORG",
        "name": "Test Organization",
        "blocktype": ["intorg"],
        "status": "formal",
        "includes": [{"id": "NO", "name": "Norway", "type": "country", "status": "member"}],
    }
    assert vi.validate_schema(good, schema, "good.yaml") == []

    bad = {"id": "TESTORG", "name": "Test", "blocktype": [], "status": "bogus"}
    errors = vi.validate_schema(bad, schema, "bad.yaml")
    assert any("status" in e for e in errors)
    assert any("blocktype" in e for e in errors)


def test_validate_aliases_accepts_valid_rename():
    aliases = [{"alias": "OLD", "target": "NEW", "reason": "renamed", "since": "1.4.0"}]
    assert vi.validate_aliases(aliases, {"NEW"}) == []


def test_validate_aliases_rejects_dangling_target():
    aliases = [{"alias": "OLD", "target": "MISSING", "reason": "renamed", "since": "1.4.0"}]
    errors = vi.validate_aliases(aliases, {"NEW"})
    assert any("MISSING" in e for e in errors)


def test_validate_aliases_rejects_unmarked_collision():
    aliases = [{"alias": "ASF", "target": "FSA", "reason": "renamed", "since": "1.3.0"}]
    errors = vi.validate_aliases(aliases, {"ASF", "FSA"})
    assert any("collides" in e for e in errors)


def test_validate_aliases_allows_disambiguated_collision():
    aliases = [{"alias": "ASF", "target": "FSA", "reason": "disambiguated", "since": "1.3.0"}]
    assert vi.validate_aliases(aliases, {"ASF", "FSA"}) == []


def test_validate_aliases_rejects_bad_reason():
    aliases = [{"alias": "OLD", "target": "NEW", "reason": "typo", "since": "1.4.0"}]
    errors = vi.validate_aliases(aliases, {"NEW"})
    assert any("invalid reason" in e for e in errors)


def test_description_quality_warns_over_threshold():
    records = [
        {"id": "A", "description": "International entity focused on trade."},
        {"id": "B", "description": "A real, specific description."},
    ]
    config = {"quality": {"templated_description": {"max": 0.25, "mode": "warn"}}}
    errors, warnings, report = vi.validate_description_quality(records, config)
    assert errors == []
    assert len(warnings) == 1
    assert report["templated_count"] == 1
    assert report["templated_rate"] == 0.5


def test_description_quality_no_config_reports_only():
    records = [{"id": "A", "description": "International entity focused on trade."}]
    errors, warnings, report = vi.validate_description_quality(records, {})
    assert errors == [] and warnings == []
    assert report["templated_count"] == 1


def test_completeness_thresholds():
    records = [{"id": "A", "wikidata_id": "Q1"}, {"id": "B"}]
    config = {"fields": {"wikidata_id": {"max_null_rate": 0.25, "mode": "warn"}}}
    errors, warnings, report = vi.validate_completeness(records, config)
    assert errors == []
    assert len(warnings) == 1
    assert report["fields"]["wikidata_id"]["null_count"] == 1


def test_includes_not_null_when_membership_not_applicable():
    record = {"id": "X", "membership_applicability": "not_applicable"}
    assert vc.is_null_intblock_field(record, "includes") is False


def test_membership_applicability_warns_when_includes_missing():
    records = [("a.yaml", {"id": "X"})]
    config = {"includes": {"membership_applicability": {"require_marker_when_empty": True, "mode": "warn"}}}
    errors, warnings = vc.validate_membership_applicability(records, config)
    assert errors == []
    assert len(warnings) == 1
    assert "membership_applicability" in warnings[0]


def test_includes_status_rejects_unknown_status():
    catalog = vc.load_includes_status_catalog(project_root() / "data" / "schemas")
    records = [("a.yaml", {"id": "X", "includes": [{"id": "US", "name": "United States", "type": "country", "status": "bogus"}]})]
    config = {"includes": {"status": {"mode": "error"}}}
    errors, warnings = vc.validate_includes_status(records, catalog, config)
    assert len(errors) == 1
    assert "bogus" in errors[0]


def test_includes_status_accepts_catalog_status():
    catalog = vc.load_includes_status_catalog(project_root() / "data" / "schemas")
    records = [("a.yaml", {"id": "X", "includes": [{"id": "US", "name": "United States", "type": "country", "status": "member"}]})]
    config = {"includes": {"status": {"mode": "error"}}}
    errors, warnings = vc.validate_includes_status(records, catalog, config)
    assert errors == []
    assert warnings == []
