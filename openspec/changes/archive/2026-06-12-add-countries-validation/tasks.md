## 1. Schema and configuration

- [x] 1.1 Extend `data/schemas/countries.schema.json` for all builder fields (`population`, `area`, `gini`, `timezones`, `native_names`, `borders`, `common_names`, `other_names`, `demonyms`, etc.)
- [x] 1.2 Add `data/schemas/countries_completeness.yaml` with per-field `max_null_rate` and `mode` (warn for five critical fields)
- [x] 1.3 Document `borders` as ISO alpha-3 land-border list in schema `description` and README

## 2. Validation tooling

- [x] 2.1 Create `scripts/validate_countries.py` (Typer CLI): JSON Schema validation per YAML file
- [x] 2.2 Add checks: alpha-2/alpha-3/numeric/M49 format, duplicate `code`/`iso3code`/`numeric_code`, trailing whitespace on categorical fields
- [x] 2.3 Add border format check (3-letter uppercase alpha-3)
- [x] 2.4 Add intblock cross-reference: `includes` with `type: country` must resolve to `data/countries/{id}.yaml` or allowlist (warn for `XA`, `XS`, `XT`, `XN`)

## 3. Build integration

- [x] 3.1 Call validator from `scripts/builder.py` before export; exit non-zero on schema/identifier errors
- [x] 3.2 Strip trailing whitespace on `region.value`, `subregion`, and similar categorical strings in `clean_data()`
- [x] 3.3 Run completeness checks; warn on configured fields until Change 2

## 4. Documentation and CI

- [x] 4.1 Update README country schema table: border alpha-3 convention, known-null semantics for territories
- [x] 4.2 Add `.github/workflows/validate.yml` running `validate_countries.py` and builder on pull requests
- [x] 4.3 Run `openspec validate add-countries-validation --strict`
