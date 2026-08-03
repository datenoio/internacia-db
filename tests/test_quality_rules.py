"""Unit tests for the expanded data-quality rules (expand-data-quality-rules)."""

from datetime import date

from internacia_builder.validate import country_rules, cross_rules, intblock_rules


def _types(issues):
    return [i["issue_type"] for i in issues]


# --- Border resolution -----------------------------------------------------

def _countries(*recs):
    return list(recs), [f"data/countries/{r.get('code', 'XX')}.yaml" for r in recs]


def test_border_resolving_to_existing_country_passes():
    recs, paths = _countries(
        {"code": "DE", "iso3code": "DEU", "borders": ["FRA"]},
        {"code": "FR", "iso3code": "FRA", "borders": ["DEU"]},
    )
    assert cross_rules.check_border_resolution(recs, paths) == []


def test_unresolved_border_reported():
    recs, paths = _countries({"code": "DE", "iso3code": "DEU", "borders": ["ZZZ"]})
    issues = cross_rules.check_border_resolution(recs, paths)
    assert _types(issues) == ["UNRESOLVED_BORDER_REFERENCE"]
    assert issues[0]["current_value"] == "ZZZ"


def test_self_referencing_border_reported():
    recs, paths = _countries({"code": "DE", "iso3code": "DEU", "borders": ["DEU"]})
    issues = cross_rules.check_border_resolution(recs, paths)
    assert _types(issues) == ["UNRESOLVED_BORDER_REFERENCE"]


# --- Border reciprocity ----------------------------------------------------

def test_nonreciprocal_border_warned():
    recs, paths = _countries(
        {"code": "AA", "iso3code": "AAA", "borders": ["BBB"]},
        {"code": "BB", "iso3code": "BBB", "borders": []},
    )
    issues = cross_rules.check_border_reciprocity(recs, paths)
    assert _types(issues) == ["NONRECIPROCAL_BORDER"]


def test_allowlisted_border_pair_suppressed():
    recs, paths = _countries(
        {"code": "AA", "iso3code": "AAA", "borders": ["BBB"]},
        {"code": "BB", "iso3code": "BBB", "borders": []},
    )
    assert cross_rules.check_border_reciprocity(recs, paths, {("AAA", "BBB")}) == []


def test_reciprocity_allowlist_parsing():
    cfg = {"borders": {"reciprocity_allowlist": ["AAA-BBB", "bad", "CCC-DDD"]}}
    assert cross_rules.load_border_reciprocity_allowlist(cfg) == {("AAA", "BBB"), ("CCC", "DDD")}


# --- Organizational references ----------------------------------------------

def _intblocks(*recs):
    return list(recs), [f"data/intblocks/intorg/{r.get('id', 'X')}.yaml" for r in recs]


def test_valid_successor_reference_passes():
    recs, paths = _intblocks({"id": "OAU", "successor": "AU"}, {"id": "AU"})
    assert cross_rules.check_org_refs(recs, paths) == []


def test_unresolved_suborganization_reported():
    recs, paths = _intblocks({"id": "X", "suborganizations": [{"id": "MISSING", "name": "M"}]})
    issues = cross_rules.check_org_refs(recs, paths)
    assert _types(issues) == ["UNRESOLVED_ORG_REF"]
    assert issues[0]["current_value"] == "MISSING"


def test_org_ref_resolves_via_alias():
    recs, paths = _intblocks({"id": "X", "predecessor": "OLDNAME"})
    assert cross_rules.check_org_refs(recs, paths, alias_names={"OLDNAME"}) == []


def test_org_ref_allowlist_suppresses():
    recs, paths = _intblocks({"id": "X", "suborganizations": [{"id": "AFFILIATE", "name": "A"}]})
    assert cross_rules.check_org_refs(recs, paths, allowlist={"AFFILIATE"}) == []


# --- Headquarters country ----------------------------------------------------

def test_valid_hq_country_passes():
    recs, paths = _intblocks({"id": "X", "headquarters": {"country": "GB"}})
    assert cross_rules.check_hq_country(recs, paths, {"GB"}) == []


def test_unresolved_hq_country_reported():
    recs, paths = _intblocks({"id": "X", "headquarters": {"country": "ZZ"}})
    issues = cross_rules.check_hq_country(recs, paths, {"GB"})
    assert _types(issues) == ["UNRESOLVED_HQ_COUNTRY"]


def test_hq_country_allowlist_suppresses():
    recs, paths = _intblocks({"id": "X", "headquarters": {"country": "ZZ"}})
    assert cross_rules.check_hq_country(recs, paths, {"GB"}, allowlist={"ZZ"}) == []


# --- Wikidata uniqueness ------------------------------------------------------

def test_shared_wikidata_id_reported():
    recs, paths = _intblocks({"id": "A", "wikidata_id": "Q123"}, {"id": "B", "wikidata_id": "Q123"})
    issues = cross_rules.check_duplicate_wikidata_ids(paths, recs)
    assert _types(issues) == ["DUPLICATE_WIKIDATA_ID"] * 2
    assert "['A', 'B']" in issues[0]["suggested_action"]


def test_unique_wikidata_ids_pass():
    recs, paths = _intblocks({"id": "A", "wikidata_id": "Q1"}, {"id": "B", "wikidata_id": "Q2"})
    assert cross_rules.check_duplicate_wikidata_ids(paths, recs) == []


def test_allowlisted_wikidata_id_suppressed():
    recs, paths = _intblocks({"id": "A", "wikidata_id": "Q123"}, {"id": "B", "wikidata_id": "Q123"})
    assert cross_rules.check_duplicate_wikidata_ids(paths, recs, {"Q123"}) == []


# --- Include display-name advisory --------------------------------------------

def test_include_name_mismatch_reported():
    recs, paths = _intblocks(
        {"id": "ORG", "includes": [{"id": "TR", "name": "Anatolia", "type": "country", "status": "member"}]}
    )
    countries = {"TR": {"code": "TR", "name": "Turkey"}}
    issues = cross_rules.check_include_name_mismatch(recs, paths, countries)
    assert _types(issues) == ["INCLUDE_NAME_MISMATCH"]


def test_include_name_variant_accepted():
    recs, paths = _intblocks(
        {"id": "ORG", "includes": [{"id": "KR", "name": "Republic of Korea", "type": "country", "status": "member"}]}
    )
    countries = {"KR": {"code": "KR", "name": "Korea, Rep.", "official_name": "Korea, Republic of"}}
    assert cross_rules.check_include_name_mismatch(recs, paths, countries) == []


# --- Indicator plausibility ----------------------------------------------------

def test_negative_population_reported():
    issues = country_rules.check_country_indicator_values({"population": {"value": -5}})
    assert _types(issues) == ["INVALID_INDICATOR_VALUE"]


def test_zero_population_allowed_for_uninhabited():
    assert country_rules.check_country_indicator_values({"population": {"value": 0}}) == []


def test_gini_outside_range_reported():
    issues = country_rules.check_country_indicator_values({"gini": {"value": 140}})
    assert _types(issues) == ["INVALID_INDICATOR_VALUE"]


def test_future_indicator_year_reported():
    future = date.today().year + 1
    issues = country_rules.check_country_indicator_values({"population": {"value": 10, "year": future}})
    assert _types(issues) == ["INVALID_INDICATOR_VALUE"]


def test_plausible_indicators_pass():
    record = {"population": {"value": 100, "year": 2024}, "area": {"value": 42.5}, "gini": {"value": 33.1}}
    assert country_rules.check_country_indicator_values(record) == []


# --- Entity flag consistency -----------------------------------------------------

def test_dependent_territory_with_un_membership_reported():
    record = {"entity_type": "dependent_territory", "un_member": True}
    issues = country_rules.check_country_entity_flags(record)
    assert _types(issues) == ["INCONSISTENT_ENTITY_FLAGS"]


def test_sovereign_state_flags_pass():
    record = {"entity_type": "sovereign_state", "un_member": True, "independent": True}
    assert country_rules.check_country_entity_flags(record) == []


# --- Provenance integrity ---------------------------------------------------------

def test_provenance_unknown_field_reported():
    record = {"name": "X", "provenance": [{"field": "nonexistent_field", "retrieved_at": "2026-01-01"}]}
    issues = country_rules.check_provenance_integrity(record)
    assert _types(issues) == ["PROVENANCE_INTEGRITY"]


def test_provenance_dotted_path_resolves():
    record = {
        "headquarters": {"coordinates": {"lat": 1, "lng": 2}},
        "provenance": [{"field": "headquarters.coordinates", "retrieved_at": "2026-01-01"}],
    }
    assert country_rules.check_provenance_integrity(record) == []


def test_provenance_future_date_reported():
    record = {"name": "X", "provenance": [{"field": "name", "retrieved_at": "2999-01-01"}]}
    issues = country_rules.check_provenance_integrity(record)
    assert _types(issues) == ["PROVENANCE_INTEGRITY"]


def test_provenance_invalid_date_reported():
    record = {"name": "X", "provenance": [{"field": "name", "retrieved_at": "not-a-date"}]}
    issues = country_rules.check_provenance_integrity(record)
    assert _types(issues) == ["PROVENANCE_INTEGRITY"]


def test_insufficient_provenance_reported():
    record = {"name": "X", "provenance": [{"field": "name", "retrieved_at": "2026-01-01"}]}
    issues = country_rules.check_provenance_count(record, min_count=4)
    assert _types(issues) == ["INSUFFICIENT_PROVENANCE"]
    assert issues[0]["current_value"] == "1"


def test_provenance_count_at_minimum_passes():
    record = {
        "name": "X",
        "provenance": [
            {"field": "name", "retrieved_at": "2026-01-01"},
            {"field": "name", "retrieved_at": "2026-01-02"},
            {"field": "name", "retrieved_at": "2026-01-03"},
            {"field": "name", "retrieved_at": "2026-01-04"},
        ],
    }
    assert country_rules.check_provenance_count(record, min_count=4) == []


def test_provenance_count_disabled_when_min_zero():
    record = {"name": "X"}
    assert country_rules.check_provenance_count(record, min_count=0) == []


# --- Coordinates and currencies ------------------------------------------------------

def test_capital_city_out_of_range_lat_reported():
    record = {"capital_city": {"lat": 99.0, "lng": 10.0}}
    issues = country_rules.check_country_coordinates(record)
    assert _types(issues) == ["INVALID_COORDINATES"]
    assert issues[0]["field"] == "capital_city.lat"


def test_valid_coordinates_pass():
    record = {"centroid": {"lat": 42.0, "lng": -71.0}, "capital_city": {"lat": 0, "lng": 180}}
    assert country_rules.check_country_coordinates(record) == []


def test_invalid_currency_code_reported():
    record = {"currencies": [{"code": "usd"}]}
    issues = country_rules.check_country_currency_codes(record)
    assert _types(issues) == ["INVALID_CURRENCY_CODE"]


# --- Filename alignment ---------------------------------------------------------------

def test_country_filename_mismatch_reported():
    issues = country_rules.check_country_filename({"code": "AT"}, "data/countries/DE.yaml")
    assert _types(issues) == ["FILENAME_ID_MISMATCH"]


def test_country_filename_match_passes():
    assert country_rules.check_country_filename({"code": "DE"}, "data/countries/DE.yaml") == []


# --- Intblock chronology ----------------------------------------------------------------

def test_dissolved_before_founded_reported():
    issues = intblock_rules.check_intblock_chronology({"founded": "1990", "dissolved": "1985"})
    assert "CHRONOLOGY_ERROR" in _types(issues)


def test_future_founded_reported():
    future = str(date.today().year + 1)
    issues = intblock_rules.check_intblock_chronology({"founded": future})
    assert _types(issues) == ["CHRONOLOGY_ERROR"]


def test_unparseable_founded_reported():
    issues = intblock_rules.check_intblock_chronology({"founded": "1998-00-00"})
    assert _types(issues) == ["CHRONOLOGY_ERROR"]


def test_decade_founded_accepted():
    assert intblock_rules.check_intblock_chronology({"founded": "1950s"}) == []


def test_ordered_dates_pass():
    assert intblock_rules.check_intblock_chronology({"founded": "1945-06-26", "dissolved": "1946"}) == []


# --- Intblock lifecycle (historical without dissolved) -------------------------------------

def test_historical_without_dissolved_reported():
    issues = intblock_rules.check_intblock_lifecycle({"status": "historical"})
    assert _types(issues) == ["LIFECYCLE_INCONSISTENCY"]


def test_historical_with_dissolved_passes():
    assert intblock_rules.check_intblock_lifecycle({"status": "historical", "dissolved": "2009"}) == []


# --- Membership consistency -------------------------------------------------------------------

def _inc(cid, status="member"):
    return {"id": cid, "name": cid, "type": "country", "status": status}


def test_duplicate_include_entry_reported():
    record = {"id": "X", "includes": [_inc("FR"), _inc("FR")]}
    issues = intblock_rules.check_intblock_membership_consistency(record)
    assert "DUPLICATE_INCLUDE_ENTRY" in _types(issues)


def test_membership_count_mismatch_reported():
    record = {"id": "X", "membership_count": 10, "includes": [_inc("FR"), _inc("DE"), _inc("IT")]}
    issues = intblock_rules.check_intblock_membership_consistency(record)
    assert "MEMBERSHIP_COUNT_MISMATCH" in _types(issues)


def test_membership_count_matching_member_class_passes():
    record = {
        "id": "X",
        "membership_count": 2,
        "includes": [_inc("FR"), _inc("DE"), _inc("US", status="observer")],
    }
    assert intblock_rules.check_intblock_membership_consistency(record) == []


def test_membership_count_tolerance_from_config():
    record = {"id": "X", "membership_count": 4, "includes": [_inc("FR"), _inc("DE"), _inc("IT")]}
    config = {"includes": {"membership_count": {"tolerance": 1}}}
    assert intblock_rules.check_intblock_membership_consistency(record, config) == []


def test_contradictory_applicability_reported():
    record = {"id": "X", "membership_applicability": "not_applicable", "includes": [_inc("FR")]}
    issues = intblock_rules.check_intblock_membership_consistency(record)
    assert "CONTRADICTORY_APPLICABILITY" in _types(issues)


def test_non_country_count_type_exempt_from_roster_comparison():
    # membership_count counts national federations, not the country roster,
    # so the count/roster divergence must not be flagged.
    record = {
        "id": "X",
        "membership_count": 211,
        "membership_count_type": "organizations",
        "includes": [_inc("FR"), _inc("DE"), _inc("IT")],
        "provenance": [{"field": "membership_count", "url": "https://example.org/members"}],
    }
    assert intblock_rules.check_intblock_membership_consistency(record) == []


def test_non_country_count_type_requires_provenance():
    record = {
        "id": "X",
        "membership_count": 211,
        "membership_count_type": "organizations",
        "includes": [_inc("FR")],
    }
    issues = intblock_rules.check_intblock_membership_consistency(record)
    assert "MEMBERSHIP_COUNT_MISMATCH" in _types(issues)


def test_countries_count_type_still_compared_against_roster():
    record = {
        "id": "X",
        "membership_count": 10,
        "membership_count_type": "countries",
        "includes": [_inc("FR"), _inc("DE"), _inc("IT")],
    }
    issues = intblock_rules.check_intblock_membership_consistency(record)
    assert "MEMBERSHIP_COUNT_MISMATCH" in _types(issues)


# --- Deprecated topics ---------------------------------------------------------------------------

def test_deprecated_topic_key_reported():
    record = {"id": "X", "topics": [{"key": "climate", "name": "Climate"}]}
    issues = intblock_rules.check_intblock_topics(record, {"climate": "climate_change"})
    assert _types(issues) == ["DEPRECATED_TOPIC_KEY"]
    assert "climate_change" in issues[0]["suggested_action"]


def test_canonical_topic_key_passes():
    record = {"id": "X", "topics": [{"key": "climate_change", "name": "Climate change"}]}
    assert intblock_rules.check_intblock_topics(record, {"climate": "climate_change"}) == []


# --- Intblock filename and directory alignment ------------------------------------------------------

def test_intblock_filename_mismatch_reported():
    issues = intblock_rules.check_intblock_filename({"id": "XYZ"}, "data/intblocks/bank/ADB.yaml")
    assert _types(issues) == ["FILENAME_ID_MISMATCH"]


def test_intblock_directory_mismatch_reported():
    record = {"id": "ADB", "blocktype": ["fund"]}
    issues = intblock_rules.check_intblock_directory_alignment(record, "data/intblocks/bank/ADB.yaml")
    assert _types(issues) == ["DIRECTORY_BLOCKTYPE_MISMATCH"]


def test_intblock_directory_match_passes():
    record = {"id": "ADB", "blocktype": ["bank"]}
    assert intblock_rules.check_intblock_directory_alignment(record, "data/intblocks/bank/ADB.yaml") == []


# --- Country field validity (add-extended-quality-rules) ----------------------

def test_invalid_tld_reported():
    issues = country_rules.check_country_tld({"code": "FR", "tld": "fr"})
    assert _types(issues) == ["INVALID_TLD"]


def test_valid_tld_passes():
    assert country_rules.check_country_tld({"code": "FR", "tld": ".fr"}) == []


def test_invalid_calling_code_reported():
    issues = country_rules.check_country_calling_codes({"calling_codes": ["33"]})
    assert _types(issues) == ["INVALID_CALLING_CODE"]


def test_area_code_extension_calling_code_passes():
    assert country_rules.check_country_calling_codes({"calling_codes": ["+35818"]}) == []


def test_unknown_timezone_reported():
    issues = country_rules.check_country_timezones({"timezones": ["Europe/Nowhere"]})
    assert _types(issues) == ["INVALID_TIMEZONE"]


def test_known_timezone_passes():
    assert country_rules.check_country_timezones({"timezones": ["Europe/Paris"]}) == []


def test_flag_emoji_mismatch_reported():
    record = {
        "code": "FR",
        "code_status": "official_iso3166_1",
        "flag_emoji": country_rules.flag_emoji_for_code("DE"),
    }
    issues = country_rules.check_country_flag_emoji(record)
    assert _types(issues) == ["FLAG_EMOJI_MISMATCH"]


def test_matching_flag_emoji_passes():
    record = {
        "code": "FR",
        "code_status": "official_iso3166_1",
        "flag_emoji": country_rules.flag_emoji_for_code("FR"),
    }
    assert country_rules.check_country_flag_emoji(record) == []


def test_non_iso_code_flag_not_checked():
    record = {"code": "XA", "code_status": "user_assigned", "flag_emoji": "🏴"}
    assert country_rules.check_country_flag_emoji(record) == []


def test_landlocked_without_borders_reported():
    issues = country_rules.check_country_landlocked(
        {"code_status": "official_iso3166_1", "landlocked": True, "borders": []}
    )
    assert _types(issues) == ["LANDLOCKED_INCONSISTENCY"]


def test_landlocked_with_borders_passes():
    record = {"code_status": "official_iso3166_1", "landlocked": True, "borders": ["FRA"]}
    assert country_rules.check_country_landlocked(record) == []


def test_island_not_landlocked_passes():
    record = {"code_status": "official_iso3166_1", "landlocked": False, "borders": []}
    assert country_rules.check_country_landlocked(record) == []


def test_non_iso_landlocked_without_borders_exempt():
    # borders holds ISO alpha-3 codes only, so user-assigned/obsolete records
    # (e.g. XS, XT, XN) legitimately combine landlocked=true with empty borders.
    record = {"code_status": "user_assigned", "landlocked": True, "borders": []}
    assert country_rules.check_country_landlocked(record) == []


# --- Region hierarchy ----------------------------------------------------------

def test_subregion_outside_continent_reported():
    record = {"code": "XX", "continents": ["Asia"], "subregion": "Caribbean"}
    issues = country_rules.check_country_region_hierarchy(record)
    assert _types(issues) == ["REGION_HIERARCHY_MISMATCH"]


def test_subregion_matching_continent_passes():
    record = {"code": "FR", "continents": ["Europe"], "subregion": "Western Europe"}
    assert country_rules.check_country_region_hierarchy(record) == []


def test_region_hierarchy_allowlist_suppresses():
    record = {"code": "CX", "continents": ["Asia"], "subregion": "Australia and New Zealand"}
    assert country_rules.check_country_region_hierarchy(record, {"CX"}) == []


def test_transcontinental_second_continent_passes():
    record = {"code": "CY", "continents": ["Europe", "Asia"], "subregion": "Western Asia"}
    assert country_rules.check_country_region_hierarchy(record) == []


# --- Capital distance ----------------------------------------------------------

def test_swapped_capital_coordinates_reported():
    record = {
        "code": "EH",
        "capital_city": {"name": "El Aaiún", "lat": -13.28, "lng": 27.14},
        "centroid": {"lat": 24.5, "lng": -13.0},
        "area": {"value": 266000},
    }
    issues = country_rules.check_country_capital_distance(record)
    assert _types(issues) == ["CAPITAL_FAR_FROM_CENTROID"]


def test_large_country_capital_within_budget_passes():
    record = {
        "code": "RU",
        "capital_city": {"name": "Moscow", "lat": 55.75, "lng": 37.62},
        "centroid": {"lat": 60.0, "lng": 100.0},
        "area": {"value": 17098242},
    }
    assert country_rules.check_country_capital_distance(record) == []


def test_capital_distance_allowlist_suppresses():
    record = {
        "code": "UM",
        "capital_city": {"name": "Washington DC", "lat": 38.89, "lng": -77.03},
        "centroid": {"lat": 19.3, "lng": 166.63},
        "area": {"value": 34.2},
    }
    config = {"geography": {"capital_distance": {"allowlist": ["UM"]}}}
    assert country_rules.check_country_capital_distance(record, config) == []


# --- Text encoding ---------------------------------------------------------------

def test_mojibake_double_encoding_reported():
    issues = country_rules.check_country_text_encoding({"name": "CÃ´te d'Ivoire"})
    assert _types(issues) == ["MOJIBAKE_TEXT"]


def test_replacement_character_reported():
    issues = country_rules.check_country_text_encoding({"name": "Fran\ufffdaise"})
    assert _types(issues) == ["MOJIBAKE_TEXT"]


def test_accented_text_passes():
    record = {"name": "Côte d'Ivoire", "official_name": "República Española", "common_names": ["São Tomé"]}
    assert country_rules.check_country_text_encoding(record) == []


def test_intblock_mojibake_in_description_reported():
    issues = intblock_rules.check_intblock_text_encoding({"name": "X", "description": "founded â€” 1950"})
    assert _types(issues) == ["MOJIBAKE_TEXT"]


# --- Parent entity resolution -----------------------------------------------------

def test_unresolved_parent_entity_reported():
    recs, paths = _countries(
        {"code": "AA", "parent_entity": {"code": "ZZ", "name": "Nowhere"}},
    )
    issues = cross_rules.check_parent_entity_refs(recs, paths)
    assert _types(issues) == ["UNRESOLVED_PARENT_ENTITY"]


def test_resolved_parent_entity_passes():
    recs, paths = _countries(
        {"code": "AA", "parent_entity": {"code": "BB", "name": "Parent"}},
        {"code": "BB"},
    )
    assert cross_rules.check_parent_entity_refs(recs, paths) == []


# --- Include date consistency ------------------------------------------------------

def test_left_before_joined_reported():
    record = {"id": "X", "includes": [{"id": "FR", "type": "country", "joined": "1995", "left": "1990"}]}
    issues = intblock_rules.check_intblock_include_dates(record)
    assert _types(issues) == ["INCLUDE_DATE_INCONSISTENCY"]


def test_joined_after_dissolved_reported():
    record = {
        "id": "X",
        "dissolved": "1991",
        "includes": [{"id": "FR", "type": "country", "joined": "1994"}],
    }
    issues = intblock_rules.check_intblock_include_dates(record)
    assert _types(issues) == ["INCLUDE_DATE_INCONSISTENCY"]


def test_unparseable_joined_reported():
    record = {"id": "X", "includes": [{"id": "FR", "type": "country", "joined": "1991-00-00"}]}
    issues = intblock_rules.check_intblock_include_dates(record)
    assert _types(issues) == ["INCLUDE_DATE_INCONSISTENCY"]


def test_future_joined_reported():
    future = str(date.today().year + 1)
    record = {"id": "X", "includes": [{"id": "FR", "type": "country", "joined": future}]}
    issues = intblock_rules.check_intblock_include_dates(record)
    assert _types(issues) == ["INCLUDE_DATE_INCONSISTENCY"]


def test_ratification_before_entry_into_force_passes():
    record = {
        "id": "X",
        "founded": "2008-07-03",
        "includes": [{"id": "AG", "type": "country", "joined": "2008-05-09"}],
    }
    assert intblock_rules.check_intblock_include_dates(record) == []


def test_year_precision_not_compared_against_specific_date():
    record = {
        "id": "X",
        "dissolved": "2015-11-01",
        "includes": [{"id": "FR", "type": "country", "left": "2015"}],
    }
    assert intblock_rules.check_intblock_include_dates(record) == []


# --- Founding members -----------------------------------------------------------------

def test_founding_member_missing_from_includes_reported():
    record = {
        "id": "X",
        "founding_members": ["CU"],
        "includes": [{"id": "FR", "type": "country", "status": "member"}],
    }
    issues = intblock_rules.check_intblock_founding_members(record, {"CU", "FR"})
    assert _types(issues) == ["FOUNDING_MEMBER_NOT_INCLUDED"]


def test_unresolved_founding_member_reported():
    record = {"id": "X", "founding_members": ["ZZ"], "includes": []}
    issues = intblock_rules.check_intblock_founding_members(record, {"FR"})
    assert _types(issues) == ["FOUNDING_MEMBER_NOT_INCLUDED"]


def test_founding_member_in_includes_passes():
    record = {
        "id": "X",
        "founding_members": ["FR"],
        "includes": [{"id": "FR", "type": "country", "status": "founding_member"}],
    }
    assert intblock_rules.check_intblock_founding_members(record, {"FR"}) == []


def test_founding_members_without_includes_pass():
    record = {"id": "X", "founding_members": ["FR"], "membership_applicability": "not_applicable"}
    assert intblock_rules.check_intblock_founding_members(record, {"FR"}) == []


# --- Last verified freshness -------------------------------------------------------------

def test_stale_last_verified_reported():
    record = {"id": "X", "last_verified": "2000-01-01"}
    issues = intblock_rules.check_intblock_last_verified(record, max_age_months=12)
    assert _types(issues) == ["STALE_LAST_VERIFIED"]


def test_recent_last_verified_passes():
    record = {"id": "X", "last_verified": date.today().isoformat()}
    assert intblock_rules.check_intblock_last_verified(record, max_age_months=12) == []


def test_invalid_last_verified_reported():
    record = {"id": "X", "last_verified": "recently"}
    issues = intblock_rules.check_intblock_last_verified(record, max_age_months=12)
    assert _types(issues) == ["STALE_LAST_VERIFIED"]


# --- Unknown topic keys ----------------------------------------------------------------

def test_unknown_topic_key_reported():
    record = {"id": "X", "topics": [{"key": "underwater_basket_weaving", "name": "?"}]}
    issues = intblock_rules.check_intblock_topics(record, {}, {"water", "economy"})
    assert _types(issues) == ["UNKNOWN_TOPIC_KEY"]


def test_catalogued_topic_key_passes():
    record = {"id": "X", "topics": [{"key": "water", "name": "Water"}]}
    assert intblock_rules.check_intblock_topics(record, {}, {"water"}) == []


def test_deprecated_key_not_double_reported_as_unknown():
    record = {"id": "X", "topics": [{"key": "climate", "name": "Climate"}]}
    issues = intblock_rules.check_intblock_topics(record, {"climate": "climate_change"}, {"climate_change"})
    assert _types(issues) == ["DEPRECATED_TOPIC_KEY"]


# --- Historical entity members -------------------------------------------------------------

def test_historical_entity_active_member_reported():
    recs, paths = _intblocks(
        {"id": "ORG", "status": "formal", "includes": [{"id": "AN", "type": "country", "status": "member"}]}
    )
    countries = {"AN": {"code": "AN", "entity_type": "historical_entity"}}
    issues = cross_rules.check_historical_entity_members(recs, paths, countries)
    assert _types(issues) == ["HISTORICAL_ENTITY_ACTIVE_MEMBER"]


def test_former_member_status_for_historical_entity_passes():
    recs, paths = _intblocks(
        {"id": "ORG", "status": "formal", "includes": [{"id": "AN", "type": "country", "status": "former_member"}]}
    )
    countries = {"AN": {"code": "AN", "entity_type": "historical_entity"}}
    assert cross_rules.check_historical_entity_members(recs, paths, countries) == []


def test_historical_block_membership_not_flagged():
    recs, paths = _intblocks(
        {"id": "ORG", "status": "historical", "includes": [{"id": "SU", "type": "country", "status": "member"}]}
    )
    countries = {"SU": {"code": "SU", "entity_type": "historical_entity"}}
    assert cross_rules.check_historical_entity_members(recs, paths, countries) == []


# --- Lineage reciprocity ----------------------------------------------------------------------

def test_missing_successor_backlink_reported():
    recs, paths = _intblocks({"id": "GATT", "successor": "WTO"}, {"id": "WTO"})
    issues = cross_rules.check_successor_reciprocity(recs, paths)
    assert _types(issues) == ["SUCCESSOR_RECIPROCITY"]


def test_reciprocal_lineage_passes():
    recs, paths = _intblocks(
        {"id": "OAU", "successor": "AU"},
        {"id": "AU", "predecessor": "OAU"},
    )
    assert cross_rules.check_successor_reciprocity(recs, paths) == []


def test_inverse_pointing_elsewhere_not_flagged():
    # predecessor/successor are single-valued; a record absorbed from several
    # organizations can point back at only one of them.
    recs, paths = _intblocks(
        {"id": "NORDEL", "successor": "ENTSOE"},
        {"id": "UCTE", "successor": "ENTSOE"},
        {"id": "ENTSOE", "predecessor": "UCTE"},
    )
    assert cross_rules.check_successor_reciprocity(recs, paths) == []


def test_unresolved_successor_not_flagged_here():
    recs, paths = _intblocks({"id": "A", "successor": "MISSING"})
    assert cross_rules.check_successor_reciprocity(recs, paths) == []


def test_suborg_child_missing_partof_reported():
    recs, paths = _intblocks(
        {"id": "OECD", "suborganizations": [{"id": "DAC", "name": "DAC"}]},
        {"id": "DAC"},
    )
    issues = cross_rules.check_partof_suborg_reciprocity(recs, paths)
    assert _types(issues) == ["PARTOF_SUBORG_RECIPROCITY"]
    assert issues[0]["record_id"] == "DAC"


def test_suborg_child_with_partof_passes():
    recs, paths = _intblocks(
        {"id": "OECD", "suborganizations": [{"id": "DAC", "name": "DAC"}]},
        {"id": "DAC", "partof": "OECD"},
    )
    assert cross_rules.check_partof_suborg_reciprocity(recs, paths) == []


def test_partof_without_parent_listing_not_flagged():
    recs, paths = _intblocks(
        {"id": "UNEP", "suborganizations": []},
        {"id": "ABIDJAN", "partof": "UNEP"},
    )
    assert cross_rules.check_partof_suborg_reciprocity(recs, paths) == []


# --- Acronym uniqueness -------------------------------------------------------------------------

def _acr(value, lang="en"):
    return {"lang": lang, "value": value}


def test_duplicate_acronym_same_blocktype_reported():
    recs, paths = _intblocks(
        {"id": "IADB", "blocktype": ["bank"], "acronyms": [_acr("IDB")]},
        {"id": "ISBD", "blocktype": ["bank"], "acronyms": [_acr("IDB")]},
    )
    issues = cross_rules.check_duplicate_acronyms(recs, paths)
    assert _types(issues) == ["DUPLICATE_ACRONYM"] * 2


def test_duplicate_acronym_different_blocktype_not_flagged():
    recs, paths = _intblocks(
        {"id": "A", "blocktype": ["bank"], "acronyms": [_acr("WA")]},
        {"id": "B", "blocktype": ["sport"], "acronyms": [_acr("WA")]},
    )
    assert cross_rules.check_duplicate_acronyms(recs, paths) == []


def test_duplicate_acronym_related_records_not_flagged():
    recs, paths = _intblocks(
        {"id": "BRIC", "blocktype": ["political"], "successor": "BRICS", "acronyms": [_acr("BRICS+")]},
        {"id": "BRICS", "blocktype": ["political"], "predecessor": "BRIC", "acronyms": [_acr("BRICS+")]},
    )
    assert cross_rules.check_duplicate_acronyms(recs, paths) == []


def test_duplicate_acronym_allowlist_suppresses():
    recs, paths = _intblocks(
        {"id": "IADB", "blocktype": ["bank"], "acronyms": [_acr("IDB")]},
        {"id": "ISBD", "blocktype": ["bank"], "acronyms": [_acr("IDB")]},
    )
    assert cross_rules.check_duplicate_acronyms(recs, paths, {"IDB"}) == []


def test_non_english_acronym_not_compared():
    recs, paths = _intblocks(
        {"id": "A", "blocktype": ["bank"], "acronyms": [_acr("CIAT", lang="es")]},
        {"id": "B", "blocktype": ["bank"], "acronyms": [_acr("CIAT")]},
    )
    assert cross_rules.check_duplicate_acronyms(recs, paths) == []


# --- Headquarters coordinate plausibility ------------------------------------------------------

def test_hq_coordinates_far_from_country_reported():
    recs, paths = _intblocks(
        {
            "id": "X",
            "headquarters": {"country": "CH", "coordinates": {"lat": -46.2, "lng": -173.9}},
        }
    )
    countries = {"CH": {"code": "CH", "centroid": {"lat": 47.0, "lng": 8.0}, "area": {"value": 41284}}}
    issues = cross_rules.check_hq_coordinates(recs, paths, countries)
    assert _types(issues) == ["HQ_COORDINATES_OUTSIDE_COUNTRY"]


def test_hq_coordinates_near_centroid_pass():
    recs, paths = _intblocks(
        {
            "id": "X",
            "headquarters": {"country": "CH", "coordinates": {"lat": 46.2, "lng": 6.15}},
        }
    )
    countries = {"CH": {"code": "CH", "centroid": {"lat": 47.0, "lng": 8.0}, "area": {"value": 41284}}}
    assert cross_rules.check_hq_coordinates(recs, paths, countries) == []


def test_hq_coordinates_allowlist_suppresses():
    recs, paths = _intblocks(
        {
            "id": "X",
            "headquarters": {"country": "CH", "coordinates": {"lat": -46.2, "lng": -173.9}},
        }
    )
    countries = {"CH": {"code": "CH", "centroid": {"lat": 47.0, "lng": 8.0}, "area": {"value": 41284}}}
    config = {"geography": {"hq_distance": {"allowlist": ["X"]}}}
    assert cross_rules.check_hq_coordinates(recs, paths, countries, config) == []
