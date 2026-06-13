# Change: Make datasets self-describing with embedded version metadata

## Why

Dataset version, `schema_hash`, and build metadata currently live only in sidecar
`*.manifest.json` files. A consumer holding just `internacia.duckdb` (the SDK's primary distribution,
downloaded from releases) cannot reliably answer "what version/schema am I on?" The
`internacia-python` README explicitly wishes for an in-database metadata/version table to support
update checks.

See [docs/strategy-and-user-needs.md](../../../docs/strategy-and-user-needs.md) §4.3 / Track A3.

## What Changes

- Embed a `_meta` table in `internacia.duckdb` with the same fields as the manifests
  (`dataset`, `version`, `build_date`, `git_commit`, `row_count`, `schema_hash`), one row per dataset.
- Emit a `data/datasets/<dataset>.meta.json` sidecar next to each Parquet file so Parquet-only
  consumers also get version info without a separate manifest lookup.
- Keep the existing `*.manifest.json` files (no removal) so current consumers are unaffected.

## Impact

- Affected specs: `dataset-release` (added)
- Affected code: `scripts/builder.py` (DuckDB export + Parquet sidecar), tests
- Breaking: None (additive; existing manifests retained)
