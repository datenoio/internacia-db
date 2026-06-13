"""Unit tests for enrich_intblocks pure logic (no network)."""

import enrich_intblocks as ei


def test_normalize_strips_punctuation_and_diacritics():
    assert ei.normalize("  Côte d'Ivoire!! ") == "cote d ivoire"
    assert ei.normalize("African Union") == "african union"


def test_is_acronym():
    assert ei.is_acronym("NATO")
    assert ei.is_acronym("EU")
    assert not ei.is_acronym("Union")
    assert not ei.is_acronym("E")  # too short
    assert not ei.is_acronym("North Atlantic")  # has space


def test_is_templated():
    assert ei.is_templated("International entity focused on economic cooperation.")
    assert ei.is_templated("an international organization for trade")
    assert not ei.is_templated("Specialized agency of the African Union.")
    assert not ei.is_templated("")


def test_clean_description_capitalizes_and_punctuates():
    assert ei.clean_description("supranational union in Africa") == "Supranational union in Africa."
    assert ei.clean_description("Already done.") == "Already done."


def test_record_qid_from_links():
    record = {"links": [{"url": "https://www.wikidata.org/wiki/Q7159", "type": "wikidata"}]}
    assert ei.record_qid_from_links(record) == "Q7159"
    assert ei.record_qid_from_links({"links": []}) is None


def test_enrich_other_names_adds_missing_and_preserves_existing():
    record = {"other_names": [{"id": "en", "name": "African Union"}]}
    entity = {"labels": {"en": {"value": "African Union"}, "fr": {"value": "Union africaine"}}}
    changed = ei.enrich_other_names(record, entity)
    assert changed is True
    names = {n["id"]: n["name"] for n in record["other_names"]}
    assert names["en"] == "African Union"  # preserved
    assert names["fr"] == "Union africaine"  # added
    assert any(p["field"] == "other_names" for p in record["provenance"])


def test_enrich_other_names_noop_when_present():
    record = {"other_names": [{"id": "en", "name": "X"}, {"id": "fr", "name": "Y"}]}
    entity = {"labels": {"en": {"value": "X"}, "fr": {"value": "Y"}}}
    assert ei.enrich_other_names(record, entity) is False


def test_enrich_acronyms_only_adds_acronym_like_aliases():
    record = {}
    entity = {"aliases": {"en": [{"value": "AU"}, {"value": "the African Union"}]}}
    changed = ei.enrich_acronyms(record, entity)
    assert changed is True
    values = {a["value"] for a in record["acronyms"]}
    assert "AU" in values
    assert "the African Union" not in values


def test_enrich_descriptions_replaces_templated_only():
    record = {"description": "International entity focused on economic cooperation."}
    entity = {"descriptions": {"en": {"value": "regional economic community in West Africa"}}}
    assert ei.enrich_descriptions(record, entity, force=False) is True
    assert record["description"] == "Regional economic community in West Africa."
    assert any(p["field"] == "description" for p in record["provenance"])


def test_enrich_descriptions_keeps_real_description():
    record = {"description": "A detailed, human-written description of the body."}
    entity = {"descriptions": {"en": {"value": "short wd desc"}}}
    assert ei.enrich_descriptions(record, entity, force=False) is False


def test_upsert_provenance_replaces_same_field():
    record = {"provenance": [{"field": "wikidata_id", "source": "old"}]}
    ei.upsert_provenance(record, "wikidata_id", "Wikidata", url="u", license="CC0")
    entries = [p for p in record["provenance"] if p["field"] == "wikidata_id"]
    assert len(entries) == 1
    assert entries[0]["source"] == "Wikidata"
