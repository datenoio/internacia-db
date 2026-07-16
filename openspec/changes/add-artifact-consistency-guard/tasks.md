## 1. Artifact consistency checker
- [x] 1.1 Add `scripts/check_generated_artifacts.py` computing primary-key sets and row counts for JSONL, YAML, Parquet, and DuckDB exports
- [x] 1.2 Compare each format's id set against the current YAML source id set; fail on any difference
- [x] 1.3 Assert all manifests, `*.meta.json` sidecars, and DuckDB `_meta` rows agree on `version`, `git_commit`, and `build_date`
- [x] 1.4 Emit a machine-readable summary and non-zero exit on mismatch

## 2. Blocktypes manifest
- [x] 2.1 Emit `data/datasets/blocktypes.manifest.json` from `scripts/builder.py` build using the shared build context
- [x] 2.2 Include blocktypes in `scripts/diff_countries_baseline.py`

## 3. CI wiring
- [x] 3.1 Add a CI step that rebuilds into a temp dir and diffs id sets, row counts, and manifest identity against committed `data/datasets/`
- [x] 3.2 Add `data/datasets/**` to validate workflow push and PR path filters
- [ ] 3.3 Remove default `--allow-row-count-change` from PR CI baseline diff (retain as opt-in for intentional expansions) — deferred: `check_generated_artifacts.py` already gates source/export drift; row-count baseline gating would block routine data-addition PRs, so `--allow-row-count-change` is retained intentionally

## 4. Tests and docs
- [x] 4.1 Add tests for `check_generated_artifacts.py` covering a matching build and an injected mismatch
- [x] 4.2 Document the artifact-consistency guarantee in README and `docs/ai-consumers.md`
- [x] 4.3 Run `python scripts/check_generated_artifacts.py` and `openspec validate add-artifact-consistency-guard --strict`
