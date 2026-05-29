# Change: Add countries validation and build quality gates

## Why

The countries dataset advertises 33 columns in README and PyArrow schema, but five analytical fields (`population`, `area`, `gini`, `timezones`, `native_names`) are 100% empty across all 252 records. Border references use ISO alpha-3 codes while the primary `code` field is alpha-2, creating a silent consumer contract mismatch. There is no automated validation for country YAML sources—only intblock link validation exists today.

See [dev/research/countries_gaps_,manus_20260528.md](../../../dev/research/countries_gaps_,manus_20260528.md).

## What Changes

- Extend [data/schemas/countries.schema.json](../../../data/schemas/countries.schema.json) to cover all builder-exported fields.
- Add `scripts/validate_countries.py` (Typer CLI) for schema, identifier, duplicate, whitespace, border-format, and intblock cross-reference checks.
- Integrate validation into [scripts/builder.py](../../../scripts/builder.py) before dataset export.
- Add `data/schemas/countries_completeness.yaml` completeness thresholds manifest (warn mode for five critical fields until Change 2).
- Document border code semantics and known-null territory rules in README.
- Add minimal CI workflow running country validation and build.

## Impact

- Affected specs: `countries-data-quality`, `countries-build`, `cross-dataset-integrity` (new capabilities)
- Affected code: `data/schemas/`, `scripts/builder.py`, `scripts/validate_countries.py`, `README.md`, `.github/workflows/`
- Breaking: None in this change (validation is additive; completeness gate starts in warn mode)
