## ADDED Requirements

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
