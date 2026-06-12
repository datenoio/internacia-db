## 1. Schema updates

- [x] 1.1 Update `data/schemas/countries.schema.json` for structured `population`, `area`, `gini`
- [x] 1.2 Update `get_countries_schema()` in `scripts/builder.py` (struct types, `clean_data()` mapping)
- [x] 1.3 Add optional `timezone_status` enum for uninhabited territories

## 2. Enrichment tooling

- [x] 2.1 Create `scripts/enrich_countries.py` (Typer): World Bank + Wikidata + IANA tzdata fetch
- [x] 2.2 Support `--dry-run`, `--code XX`, and idempotent YAML merge with provenance comments/fields
- [x] 2.3 Manual review queue for 6 missing `wikidata_id` records (`JG`, `PT`, `CO`, `AN`, `KV`, etc.)

## 3. Data backfill

- [x] 3.1 Batch-enrich all 252 country YAML files for population, area, timezones, native_names
- [x] 3.2 Populate gini where World Bank data exists; leave null elsewhere
- [x] 3.3 Fill remaining `common_names` (59 gaps), `capital_city` (11 gaps), fix `UM` capital coordinates
- [x] 3.4 Use empty list `borders: []` for island territories instead of null where applicable

## 4. Build and gates

- [x] 4.1 Regenerate `data/datasets/countries.parquet` and compressed exports
- [x] 4.2 Set `countries_completeness.yaml` to `mode: error` for population, area, timezones, native_names
- [x] 4.3 Add CHANGELOG migration note for structured `population` Parquet type
- [x] 4.4 Run `openspec validate fill-countries-core-fields --strict`
