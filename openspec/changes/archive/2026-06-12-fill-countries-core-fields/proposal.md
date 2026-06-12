# Change: Fill countries core profile fields

## Why

Five fields advertised in the public schema are 100% empty across all 252 country records: `population`, `area`, `gini`, `timezones`, and `native_names`. This blocks analytical and localization use cases and violates the implied contract in README and PyArrow schema. Additional partial gaps exist for `common_names` (59), `capital_city` (11), and `wikidata_id` (6).

Depends on **add-countries-validation** (schema enforcement and completeness manifest).

See [dev/research/countries_gaps_,manus_20260528.md](../../../dev/research/countries_gaps_,manus_20260528.md).

## What Changes

- Add `scripts/enrich_countries.py` for World Bank, Wikidata, and IANA timezone enrichment with provenance metadata.
- Restructure `population`, `area`, and `gini` as `{value, year, source}` indicators in YAML, JSON Schema, and PyArrow.
- Populate `timezones` and `native_names` for all applicable entities.
- Partial backfill: `common_names`, `wikidata_id`, `capital_city` gaps per audit.
- Regenerate `data/datasets/countries.*` exports.
- Switch completeness manifest to `error` mode for the five former blocker fields.

## Impact

- Affected specs: `countries-profile` (new capability)
- Affected code: `data/countries/*.yaml`, `scripts/builder.py`, `scripts/enrich_countries.py`, `data/schemas/`, `data/datasets/`
- **BREAKING**: `population` column type changes from bare `int64` to structured struct in Parquet; consumers must migrate (document in CHANGELOG)
