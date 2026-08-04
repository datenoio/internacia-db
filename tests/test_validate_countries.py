"""Unit tests for validate_countries checks."""

import validate_countries as vc


def test_check_duplicates_flags_repeated_codes():
    records = [
        ("a.yaml", {"code": "AA", "iso3code": "AAA", "numeric_code": "001"}),
        ("b.yaml", {"code": "AA", "iso3code": "AAB", "numeric_code": "002"}),
    ]
    errors = vc.check_duplicates(records)
    assert any("duplicate code 'AA'" in e for e in errors)


def test_check_duplicates_clean_records():
    records = [
        ("a.yaml", {"code": "AA", "iso3code": "AAA", "numeric_code": "001"}),
        ("b.yaml", {"code": "AB", "iso3code": "AAB", "numeric_code": "002"}),
    ]
    assert vc.check_duplicates(records) == []


def test_validate_borders_rejects_alpha2():
    errors = vc.validate_borders({"borders": ["CA", "MEX"]}, "x.yaml")
    assert len(errors) == 1
    assert "CA" in errors[0]


def test_validate_borders_accepts_alpha3():
    assert vc.validate_borders({"borders": ["CAN", "MEX"]}, "x.yaml") == []


def test_validate_indicator_years_rejects_zero():
    record = {"population": {"value": 1, "year": 0}}
    errors = vc.validate_indicator_years(record, "x.yaml")
    assert len(errors) == 1
    assert "population.year" in errors[0]


def test_validate_indicator_years_accepts_missing_year():
    record = {"population": {"value": 1, "source": "Wikidata"}}
    assert vc.validate_indicator_years(record, "x.yaml") == []


def test_validate_indicator_years_accepts_real_year():
    record = {"gini": {"value": 30.5, "year": 2019}}
    assert vc.validate_indicator_years(record, "x.yaml") == []


def test_entity_status_non_iso_code_must_not_be_official():
    record = {"code": "XK", "entity_type": "disputed_territory", "code_status": "official_iso3166_1"}
    errors, _ = vc.validate_entity_status(record, "XK.yaml")
    assert any("must not have code_status official_iso3166_1" in e for e in errors)


def test_entity_status_iso_code_must_be_official():
    record = {"code": "US", "entity_type": "sovereign_state", "code_status": "user_assigned"}
    errors, _ = vc.validate_entity_status(record, "US.yaml")
    assert any("must have code_status official_iso3166_1" in e for e in errors)


def test_completeness_error_mode_above_threshold():
    records = [{"a": "x"}, {"a": None}]
    config = {"fields": {"a": {"max_null_rate": 0.0, "mode": "error"}}}
    errors, warnings, report = vc.validate_completeness(records, config)
    assert len(errors) == 1
    assert warnings == []
    assert report["fields"]["a"]["null_count"] == 1


def test_completeness_warn_mode_above_threshold():
    records = [{"a": "x"}, {"a": ""}]
    config = {"fields": {"a": {"max_null_rate": 0.0, "mode": "warn"}}}
    errors, warnings, _ = vc.validate_completeness(records, config)
    assert errors == []
    assert len(warnings) == 1


def test_completeness_within_threshold():
    records = [{"a": "x"}, {"a": None}]
    config = {"fields": {"a": {"max_null_rate": 0.5, "mode": "error"}}}
    errors, warnings, _ = vc.validate_completeness(records, config)
    assert errors == []
    assert warnings == []


def test_timezones_not_applicable_is_not_null():
    record = {"timezone_status": "not_applicable"}
    assert vc.is_null_field(record, "timezones") is False


def test_official_iso_count_enforced():
    records = [{"code_status": "official_iso3166_1"}] * (vc.EXPECTED_OFFICIAL_ISO_COUNT - 1)
    errors = vc.validate_official_iso_count(records)
    assert len(errors) == 1


def test_validate_currency_codes_warns_invalid():
    record = {"currencies": [{"code": "usd", "name": "US Dollar"}]}
    warnings = vc.validate_currency_codes(record, "x.yaml")
    assert len(warnings) == 1
    assert "ISO 4217" in warnings[0]


def test_validate_currency_codes_accepts_valid():
    record = {"currencies": [{"code": "USD", "name": "US Dollar"}]}
    assert vc.validate_currency_codes(record, "x.yaml") == []


def test_validate_provenance_freshness_warns_stale():
    record = {"provenance": [{"field": "population", "source": "World Bank", "retrieved_at": "2020-01-01"}]}
    warnings = vc.validate_provenance_freshness(record, "x.yaml", max_age_months=12)
    assert len(warnings) == 1
    assert "stale" in warnings[0]


def test_validate_provenance_freshness_accepts_recent():
    record = {"provenance": [{"field": "population", "source": "World Bank", "retrieved_at": "2026-06-01"}]}
    assert vc.validate_provenance_freshness(record, "x.yaml", max_age_months=12) == []
