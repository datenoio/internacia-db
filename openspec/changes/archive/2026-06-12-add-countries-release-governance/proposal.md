# Change: Add countries release governance and provenance

## Why

The repository lacks machine-readable release metadata, PR-level CI guarantees beyond ad-hoc validation, and field-level provenance for externally sourced values. Intblock include names diverge from canonical country names in thousands of cases—identifier integrity should be enforced while display names remain source labels.

Depends on **add-countries-validation**, **fill-countries-core-fields**, and **add-countries-entity-status**.

See [dev/research/countries_gaps_,manus_20260528.md](../../../dev/research/countries_gaps_,manus_20260528.md).

## What Changes

- Emit `data/datasets/countries.manifest.json` on each build (version, commit, row count, schema hash).
- Expand CI: schema diff, completeness report artifact on pull requests.
- Optional `provenance` list on country records for enrichment traceability.
- Add `scripts/report_country_include_names.py` for alias audit (warn-only).
- CHANGELOG migration notes for structured indicators and border contract.

## Impact

- Affected specs: `dataset-release` (new), `cross-dataset-integrity` (modified)
- Affected code: `scripts/builder.py`, `.github/workflows/`, `CHANGELOG.md`, optional country YAML provenance blocks
- Breaking: None (additive manifest and provenance)
