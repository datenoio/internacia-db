## ADDED Requirements

### Requirement: Countries build manifest

Each successful countries dataset build SHALL write `data/datasets/countries.manifest.json` containing at minimum: `version`, `build_date` (ISO 8601), `git_commit` (short SHA or `unknown`), `row_count`, and `schema_hash`.

#### Scenario: Manifest written after build

- **WHEN** `scripts/builder.py` completes a countries export
- **THEN** `countries.manifest.json` exists with `row_count` equal to 252

#### Scenario: Schema hash changes on struct migration

- **WHEN** PyArrow schema for countries changes
- **THEN** `schema_hash` in the manifest differs from the previous build

### Requirement: Pull request validation workflow

The repository SHALL run country validation and dataset build on pull requests affecting `data/countries/` or `scripts/`.

#### Scenario: Invalid country fails CI

- **WHEN** a pull request introduces a country YAML with invalid `iso3code`
- **THEN** the CI workflow fails

#### Scenario: Completeness report published

- **WHEN** CI runs on a pull request
- **THEN** a completeness summary artifact or log is available for review

### Requirement: Field-level provenance on country records

Country YAML records MAY include a `provenance` list. When present, each entry SHALL include `field`, `source`, and `retrieved_at` (ISO 8601 date); `url` and `license` are optional.

#### Scenario: Enrichment adds provenance

- **WHEN** `enrich_countries.py` updates `population` from World Bank
- **THEN** the YAML record includes a provenance entry with `field: population` and non-empty `source`

#### Scenario: Records without enrichment omit provenance

- **WHEN** a country file has only hand-curated data
- **THEN** validation passes whether or not `provenance` is present

### Requirement: Changelog migration documentation

Breaking or consumer-affecting schema changes SHALL be documented in `CHANGELOG.md` with migration guidance.

#### Scenario: Population struct documented

- **WHEN** structured `population` ships
- **THEN** CHANGELOG contains an entry describing the Parquet type change and example access pattern
