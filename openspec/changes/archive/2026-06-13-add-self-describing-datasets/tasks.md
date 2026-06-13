## 1. Embedded DuckDB metadata

- [x] 1.1 In `scripts/builder.py`, create a `_meta` table in `internacia.duckdb` during DuckDB export
- [x] 1.2 Populate one row per dataset (`countries`, `intblocks`, `blocktypes`) with `version`, `build_date`, `git_commit`, `row_count`, `schema_hash`

## 2. Parquet sidecar metadata

- [x] 2.1 Emit `data/datasets/<dataset>.meta.json` alongside each Parquet export with the same fields
- [x] 2.2 Ensure values match the corresponding `*.manifest.json`

## 3. Tests and docs

- [x] 3.1 Add a test querying `SELECT * FROM _meta` from a freshly built DuckDB and asserting fields
- [x] 3.2 Add a test asserting Parquet sidecar `.meta.json` matches the manifest
- [x] 3.3 README: document the in-DB `_meta` table and `.meta.json` sidecars for consumers
- [x] 3.4 Run `openspec validate add-self-describing-datasets --strict`
