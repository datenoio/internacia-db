# dataset-release Specification

## Purpose
TBD - created by archiving change add-countries-release-governance. Update Purpose after archive.
## Requirements
### Requirement: Countries build manifest

Each successful countries dataset build SHALL write `data/datasets/countries.manifest.json` containing at minimum: `version`, `build_date` (ISO 8601), `git_commit` (short SHA or `unknown`), `row_count`, and `schema_hash`. The `version` field SHALL match the semver tag when built as part of a release workflow.

#### Scenario: Manifest version matches release tag

- **WHEN** a release build runs for tag `v1.3.0`
- **THEN** `countries.manifest.json` `version` equals `1.3.0`

#### Scenario: Manifest written after build

- **WHEN** `scripts/builder.py` completes a countries export
- **THEN** `countries.manifest.json` exists with `row_count` equal to the current country record count

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

### Requirement: Semver tag release workflow

Pushing a git tag matching `v*` SHALL trigger a workflow that builds all dataset formats and publishes them as GitHub Release assets.

#### Scenario: Tag triggers release build

- **WHEN** a maintainer pushes tag `v1.3.0`
- **THEN** CI runs validation and `builder.py build`, then attaches outputs under `data/datasets/` to the GitHub Release

#### Scenario: Release assets include core formats

- **WHEN** a release workflow completes successfully
- **THEN** release assets include at minimum countries and intblocks Parquet or compressed JSONL outputs and `internacia.duckdb`

### Requirement: Release consumption documentation

README SHALL document how consumers obtain datasets via GitHub Releases versus cloning the repository.

#### Scenario: Download instructions present

- **WHEN** a consumer reads README release section
- **THEN** they find steps to download assets for a specific semver tag

### Requirement: Intblocks build manifest

Each successful intblocks dataset build SHALL write `data/datasets/intblocks.manifest.json` containing at minimum: `version`, `build_date` (ISO 8601), `git_commit` (short SHA or `unknown`), `row_count`, and `schema_hash`.

#### Scenario: Manifest written after build

- **WHEN** `scripts/builder.py` completes an intblocks export
- **THEN** `intblocks.manifest.json` exists with `row_count` matching the intblock source file count

#### Scenario: Schema hash changes on schema migration

- **WHEN** PyArrow schema for intblocks changes
- **THEN** `schema_hash` in the manifest differs from the previous build

### Requirement: Embedded DuckDB metadata table

The DuckDB export SHALL include a `_meta` table containing one row per dataset with at minimum
`dataset`, `version`, `build_date` (ISO 8601), `git_commit`, `row_count`, and `schema_hash`, so the
database file is self-describing without external manifests.

#### Scenario: Metadata table queryable after build

- **WHEN** `scripts/builder.py build --formats duckdb` completes
- **THEN** `SELECT version, schema_hash FROM _meta WHERE dataset = 'countries'` returns the current build version and schema hash

#### Scenario: One row per dataset

- **WHEN** the DuckDB file is built
- **THEN** `_meta` contains a row for each of `countries`, `intblocks`, and `blocktypes`

### Requirement: Parquet sidecar metadata

Each Parquet export SHALL be accompanied by a `data/datasets/<dataset>.meta.json` sidecar containing
the same fields as the dataset manifest, so Parquet-only consumers can determine version without a
separate manifest lookup.

#### Scenario: Sidecar written next to Parquet

- **WHEN** `scripts/builder.py` writes `countries.parquet`
- **THEN** `countries.meta.json` exists in the same directory with matching `version` and `schema_hash`

### Requirement: Identifier alias map artifact

Each successful build SHALL emit an intblock identifier alias artifact at
`data/datasets/intblocks_aliases.json` (and a Parquet equivalent) mapping every retired or renamed
intblock id to its current id. Each entry SHALL include `alias` (retired id), `target` (current id),
`reason` (`renamed`, `merged`, or `disambiguated`), and `since` (the version that introduced the change).

#### Scenario: Alias artifact written on build

- **WHEN** `scripts/builder.py build` completes an intblocks export
- **THEN** `data/datasets/intblocks_aliases.json` exists and contains an entry for each known retired id

#### Scenario: Retired id is resolvable

- **WHEN** a consumer holds the retired id `ASF`
- **THEN** the alias artifact maps `ASF` to its current id `FSA`

### Requirement: Alias artifact in release assets

The alias artifact SHALL be published as a GitHub Release asset by the tag-triggered release workflow.

#### Scenario: Release includes alias artifact

- **WHEN** a release workflow completes for a `v*` tag
- **THEN** release assets include `intblocks_aliases.json`

