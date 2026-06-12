## 1. Release metadata

- [x] 1.1 Extend `scripts/builder.py` to write `data/datasets/countries.manifest.json` with `version`, `build_date`, `git_commit`, `row_count`, `schema_hash`
- [x] 1.2 Include intblocks manifest or combined `internacia.manifest.json` if builder already unified (optional)

## 2. CI expansion

- [x] 2.1 Update `.github/workflows/validate.yml`: run on PR, upload completeness report artifact
- [x] 2.2 Add schema/row-count diff check against `main` branch baseline for countries parquet
- [x] 2.3 Fail PR when `validate_countries.py` reports errors

## 3. Provenance and reporting

- [x] 3.1 Add optional `provenance` array shape to country JSON Schema: `{field, source, url, retrieved_at, license}`
- [x] 3.2 Update `scripts/enrich_countries.py` to append provenance entries per enriched field group
- [x] 3.3 Add `scripts/report_country_include_names.py`: log include `name` vs canonical `name` mismatches (warn-only, exit 0)

## 4. Documentation

- [x] 4.1 CHANGELOG: structured `population`, borders alpha-3 contract, entity status fields
- [x] 4.2 README: link to manifest, CI badges, consumer migration section
- [x] 4.3 Run `openspec validate add-countries-release-governance --strict`
