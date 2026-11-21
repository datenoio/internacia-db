# Change: Make `native_names` hold names in each entity's own languages

## Why
`native_names` does not contain what its name and schema description promise. The enricher
(`build_native_names` in `scripts/enrich_countries.py`) takes the Wikidata **label** as
`official` and the **first alias** as `common`, for English and the six UN languages. As a result:

- The two variants are swapped: DE `en` is `{official: Germany, common: Federal Republic of Germany}`.
- Aliases are not names. They include pejorative and obsolete forms: CN `en.common: Red China` and
  `fr.common: Chine communiste`, BY `en.common: White Russia`, RU `fr.common: Rus.`.
- The entries are mostly exonyms and repeat `other_names`, which already holds the six UN-language
  labels for 246 records. Of the 1504 entries, 255 are `en` and about 246 each are `ar`, `es`,
  `fr`, `ru` and `zh`. The entity's own languages are usually missing: CH has no `it` or `rm`,
  and IN has no `hi`.
- `zh` mixes scripts within one record (DE `zh.official` 德國 is traditional, `zh.common` 德意志).
- The language-code mapping truncates ISO 639-3 to two letters (`c[:2]`). That is right for
  `hin`, but wrong for `pol`, `ces` and `swe` (`po`, `ce`, `sw`).

## What Changes
- **BREAKING (content):** `native_names` keys become the entity's languages from `languages[]`,
  mapped through a reviewed table. Exonyms in other languages stay only in `other_names`. The
  export type `map<string, struct<official: string, common: string>>` does not change.
- `official` comes from Wikidata P1448 (official name) in that language. `common` comes from the
  Wikidata label in that language, falling back to P1705 (native label) when the label repeats
  `official`. Aliases are never used. Either value may be null, and an entry with neither is
  omitted.
- Chinese uses the entity's script: Simplified for CN and SG, Traditional for TW, HK and MO.
  The key stays `zh`.
- New vocabulary `data/vocabs/language_codes.yaml` maps the 154 ISO 639-3 codes used in
  `languages[]` to a map key (ISO 639-1 when it exists, otherwise ISO 639-3) and to the Wikidata
  label codes to try, in order. It covers collisions (`ron` also resolves to the "Moldovan" item),
  Norwegian (`nor` has labels only under `nb`/`nn`) and macrolanguages with no Wikidata code
  (`ber`, `smi`, `kon`).
- New validation rule `NATIVE_NAME_LANGUAGE` (warning): every `native_names` key must be one of
  the record's mapped `languages[]`. Completeness keeps `mode: error`. An empty map is accepted
  only when `languages[]` is empty, following the existing `timezone_status: not_applicable`
  precedent.
- Provenance for `native_names` points to the entity's Wikidata page with the retrieval date.

## Impact
- Affected specs: countries-profile (Native names map)
- Affected code: `scripts/enrich_countries.py`, `internacia_builder/validate/country_rules.py`,
  `internacia_builder/validate/cross_rules.py` (include-name variants), `data/schemas/countries.schema.json`
- Affected data: all 256 `data/countries/*.yaml`, and the new `data/vocabs/language_codes.yaml`
- Affected docs: README, `docs/ai-consumers.md`, `docs/data-dictionary.md`, `docs/enrichment.md`,
  `llms.txt`, `llms.zh.txt`, CHANGELOG
- Consumers: about 1130 exonym entries disappear, and `en` remains only for the 91 entities that list
  English. Consumers that read `native_names['en']` should use `name`/`official_name`. Consumers
  that search exonyms should use `other_names`. The `internacia-python` `search` matches only
  `native_names[].common`, so it must also search `other_names` before this ships. Release it in
  the next MAJOR, as the versioning policy requires when consumers must change queries.
