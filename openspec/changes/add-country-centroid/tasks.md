## 1. Schema

- [x] 1.1 Add `centroid` object (`lat`, `lng`) to `data/schemas/countries.schema.json`
- [x] 1.2 Update PyArrow schema in `scripts/builder.py` for Parquet/DuckDB export
- [x] 1.3 Add `centroid` completeness rule to `countries_completeness.yaml` (warn then error)

## 2. Data population (High)

- [x] 2.1 Source centroid coordinates from Natural Earth or World Bank geocoded country list
- [x] 2.2 Populate all 252 country YAML files with `centroid.lat` and `centroid.lng`
- [x] 2.3 Add `provenance` for centroid values; migrate/remove ad hoc `latitude`/`longitude` on HK, IL, MO

## 3. Validation and release

- [x] 3.1 Add validator check for lat/lng ranges (-90..90, -180..180)
- [x] 3.2 Rebuild datasets and verify manifest `schema_hash` change documented in CHANGELOG
- [x] 3.3 Run `openspec validate add-country-centroid --strict`
