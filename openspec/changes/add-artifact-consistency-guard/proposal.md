# Change: Guard generated dataset artifacts against source and build drift

## Why
Committed artifacts under `data/datasets/` are produced by a manual build step and CI never verifies them against a fresh build. This already shipped a real defect (JSONL/YAML exports missing `BLASMBL` while Parquet/DuckDB contained it), and current path filters let dataset-only commits skip CI entirely. Consumers can get different results depending on the format they read.

## What Changes
- Add `scripts/check_generated_artifacts.py` that verifies, across every committed format (JSONL, YAML, Parquet, DuckDB), identical primary-key sets and row counts, and that these match the current YAML source id set.
- Verify all manifests, Parquet `*.meta.json` sidecars, and the DuckDB `_meta` table share one build identity (`version`, `git_commit`, `build_date`).
- Add a CI job that rebuilds into a temporary directory and fails if primary-key sets, row counts, or manifest identity differ from committed `data/datasets/`.
- Extend `scripts/diff_countries_baseline.py` to include `blocktypes`, and stop passing `--allow-row-count-change` by default in PR CI so unexplained row-count changes fail.
- Include `data/datasets/**` in the validate workflow push/PR path filters.
- Emit `data/datasets/blocktypes.manifest.json` for symmetry with `countries`/`intblocks` (currently only a sidecar exists although `llms.txt` and `release.yml` reference the manifest).

## Impact
- Affected specs: cross-dataset-integrity, dataset-release
- Affected code: `scripts/check_generated_artifacts.py` (new), `scripts/builder.py`, `scripts/diff_countries_baseline.py`, `.github/workflows/validate.yml`, `.github/workflows/release.yml`, `data/datasets/blocktypes.manifest.json` (new artifact)
