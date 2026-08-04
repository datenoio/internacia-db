# Change: Automate enrichment refresh with monthly PR workflow

## Why
`enrichment-check.yml` runs monthly and uploads a freshness report, and `STALE_PROVENANCE` quality rules exist, but enrichment is never auto-applied. World Bank classifications and Wikidata-sourced fields silently age. The deep review recommends extending the workflow to open a PR when diffs are detected.

## What Changes
- Extend `.github/workflows/enrichment-check.yml` to run enrichment scripts when staleness is detected and open a PR via `peter-evans/create-pull-request` (or equivalent).
- Keep human review as merge gate; do not auto-merge.
- Document the cadence in `docs/enrichment.md` and CONTRIBUTING.

## Impact
- Affected specs: dev-tooling, data-quality-analysis
- Affected code: `.github/workflows/enrichment-check.yml`, `docs/enrichment.md`
