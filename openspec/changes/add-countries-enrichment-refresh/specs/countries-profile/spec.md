## MODIFIED Requirements

### Requirement: Configurable completeness thresholds

Completeness rules SHALL be defined in `data/schemas/countries_completeness.yaml` with per-field `max_null_rate` and `mode` (`warn` or `error`). The `gini` field MAY be tightened incrementally as enrichment improves coverage.

#### Scenario: Gini threshold tightened after backfill

- **WHEN** gini null rate falls below a new `max_null_rate` target
- **THEN** maintainers MAY switch `gini.mode` from `warn` to `error` in a documented release

#### Scenario: Field exceeding threshold fails in error mode

- **WHEN** a field has `mode: error` and null rate exceeds `max_null_rate`
- **THEN** validation fails with a completeness error

## ADDED Requirements

### Requirement: Provenance freshness warnings

When a country record includes provenance entries, validation SHALL warn when `retrieved_at` exceeds a configured maximum age.

#### Scenario: Stale provenance warns

- **WHEN** a provenance entry `retrieved_at` is older than the configured threshold
- **THEN** validation emits a freshness warning identifying the field and record

### Requirement: Enrichment refresh documentation

The repository SHALL document how maintainers refresh externally sourced country fields and update provenance timestamps.

#### Scenario: Refresh runbook available

- **WHEN** a maintainer needs to refresh World Bank or Wikidata sourced fields
- **THEN** documentation describes commands, expected diffs, and validation steps
