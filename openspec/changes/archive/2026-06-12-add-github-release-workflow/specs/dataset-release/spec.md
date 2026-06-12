## ADDED Requirements

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

## MODIFIED Requirements

### Requirement: Countries build manifest

Each successful countries dataset build SHALL write `data/datasets/countries.manifest.json` containing at minimum: `version`, `build_date` (ISO 8601), `git_commit` (short SHA or `unknown`), `row_count`, and `schema_hash`. The `version` field SHALL match the semver tag when built as part of a release workflow.

#### Scenario: Manifest version matches release tag

- **WHEN** a release build runs for tag `v1.3.0`
- **THEN** `countries.manifest.json` `version` equals `1.3.0`

#### Scenario: Manifest written after build

- **WHEN** `scripts/builder.py` completes a countries export
- **THEN** `countries.manifest.json` exists with `row_count` equal to the current country record count
