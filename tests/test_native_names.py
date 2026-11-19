"""native_names from each entity's own languages (openspec: fix-country-native-names), offline."""

import enrich_countries as ec
import yaml

from internacia_builder import native_names as nn
from internacia_builder.paths import project_root
from internacia_builder.validate import country_rules, registry

VOCAB = {
    "deu": {"id": "deu", "key": "de", "wikidata_codes": ["de"]},
    "zho": {"id": "zho", "key": "zh", "wikidata_codes": ["zh"]},
    "nor": {"id": "nor", "key": "no", "wikidata_codes": ["nb", "nn", "no"]},
    "nzs": {"id": "nzs", "key": "nzs", "wikidata_codes": []},
}


def claim(lang, text, rank="normal", ended=False):
    c = {"mainsnak": {"datavalue": {"value": {"language": lang, "text": text}}}, "rank": rank}
    if ended:
        c["qualifiers"] = {"P582": [{}]}
    return c


def entity(labels, official=(), native=()):
    return {
        "labels": {lang: {"language": lang, "value": v} for lang, v in labels.items()},
        "aliases": {"en": [{"value": "Red China"}]},
        "claims": {"P1448": list(official), "P1705": list(native)},
    }


def record(code, *langs):
    return {"code": code, "languages": [{"code": c} for c in langs]}


GERMANY = entity(
    {"de": "Deutschland", "en": "Germany", "fr": "Allemagne"},
    official=[claim("de", "Deutsches Reich", ended=True), claim("de", "Bundesrepublik Deutschland", "preferred")],
)


def test_official_and_common_are_not_swapped_and_exonyms_are_dropped():
    names = nn.build_native_names(record("DE", "deu"), GERMANY, VOCAB)
    assert names == {"de": {"official": "Bundesrepublik Deutschland", "common": "Deutschland"}}


def test_aliases_never_appear():
    china = entity({"zh-hans": "中华人民共和国"}, official=[claim("zh-hans", "中华人民共和国", "preferred")])
    values = {v for entry in nn.build_native_names(record("CN", "zho"), china, VOCAB).values() for v in entry.values()}
    assert "Red China" not in values


def test_chinese_uses_the_entity_script_and_native_label_fallback():
    china = entity(
        {"zh-hans": "中华人民共和国", "zh-hant": "中華人民共和國", "zh": "中國"},
        official=[claim("zh-hant", "中華人民共和國"), claim("zh-hans", "中华人民共和国", "preferred")],
        native=[claim("zh-hans", "中华人民共和国", "preferred"), claim("zh-hans", "中国")],
    )
    assert nn.build_native_names(record("CN", "zho"), china, VOCAB) == {"zh": {"official": "中华人民共和国", "common": "中国"}}
    taiwan = entity({"zh-tw": "中華民國", "zh-hans": "中华民国"}, official=[claim("zh-tw", "中華民國", "preferred")],
                    native=[claim("zh-tw", "中華民國"), claim("zh-tw", "臺灣")])
    assert nn.build_native_names(record("TW", "zho"), taiwan, VOCAB) == {"zh": {"official": "中華民國", "common": "臺灣"}}


def test_norwegian_falls_back_through_bokmal_and_missing_values_are_omitted():
    svalbard = entity({"nb": "Svalbard og Jan Mayen", "nn": "Svalbard og Jan Mayen"})
    assert nn.build_native_names(record("SJ", "nor"), svalbard, VOCAB) == {"no": {"common": "Svalbard og Jan Mayen"}}


def test_deprecated_statements_and_codeless_languages_yield_nothing():
    ent = entity({}, official=[claim("de", "Altname", "deprecated")])
    assert nn.build_native_names(record("XX", "deu", "nzs"), ent, VOCAB) == {}
    assert nn.wikidata_codes(record("XX", "nzs"), VOCAB) == {}
    assert nn.allowed_keys(record("XX", "deu", "nzs"), VOCAB) == {"de", "nzs"}


def test_keys_outside_the_entity_languages_are_reported():
    rec = {**record("DE", "deu"), "native_names": {"de": {"common": "Deutschland"}, "en": {"common": "Germany"}}}
    issues = nn.check_native_name_keys(rec, VOCAB)
    assert [(i["issue_type"], i["current_value"]) for i in issues] == [("NATIVE_NAME_LANGUAGE", "en")]
    assert "other_names" in issues[0]["suggested_action"]


def test_empty_map_is_complete_only_without_languages():
    assert not country_rules.is_null_field({"native_names": {}, "languages": []}, "native_names")
    assert country_rules.is_null_field({"native_names": {}, "languages": [{"code": "deu"}]}, "native_names")
    assert country_rules.is_null_field({"languages": []}, "native_names")


def test_wikidata_batch_chunks_languages_and_keeps_claims(monkeypatch):
    calls = []

    def fake_fetch(url):
        calls.append(url)
        lang = "de" if len(calls) == 1 else "zu"
        entry = {"labels": {lang: {"value": lang}}}
        if "claims" in url:
            entry["claims"] = {"P1448": []}
        return {"entities": {"Q183": entry}}

    monkeypatch.setattr(ec, "fetch_json", fake_fetch)
    monkeypatch.setattr(ec, "REQUEST_DELAY", 0)
    merged = ec.wikidata_batch(["Q183"], [f"l{i}" for i in range(120)])
    assert len(calls) == 3 and "labels%7Cclaims" in calls[0] and "claims" not in calls[1]
    assert set(merged["Q183"]["labels"]) == {"de", "zu"} and "claims" in merged["Q183"]


def test_refresh_keeps_provenance_position_and_is_idempotent():
    rec = {
        **record("DE", "deu"),
        "wikidata_id": "Q183",
        "native_names": {"en": {"official": "Germany", "common": "Federal Republic of Germany"}},
        "provenance": [
            {"field": "native_names", "source": "Wikidata", "retrieved_at": "2026-06-15"},
            {"field": "timezones", "source": "IANA tzdata", "retrieved_at": "2026-06-15"},
        ],
    }
    assert ec.refresh_native_names(rec, GERMANY)
    ec.sync_provenance_from_record(rec, retrieved_fields={"native_names"})
    assert [p["field"] for p in rec["provenance"]] == ["native_names", "timezones"]
    assert rec["provenance"][0]["url"] == "https://www.wikidata.org/wiki/Q183"
    assert not ec.refresh_native_names(rec, GERMANY)


def test_vocabulary_covers_every_country_language_code():
    vocab = nn.load_language_codes()
    codes = {
        str(lang["code"])
        for path in (project_root() / "data" / "countries").glob("*.yaml")
        for lang in (yaml.safe_load(path.read_text(encoding="utf-8")).get("languages") or [])
    }
    assert codes <= set(vocab), sorted(codes - set(vocab))
    assert all(e.get("note") for e in vocab.values() if not e["wikidata_codes"])


def test_native_name_rule_is_registered_and_the_repository_is_consistent():
    rule = next(r for r in registry.COUNTRY_RULES if r.name == "native name languages")
    ctx = registry.load_context(project_root())
    assert [i for rec, p in zip(ctx.countries.records, ctx.countries.paths, strict=True) for i in rule.check(ctx, rec, p)] == []
