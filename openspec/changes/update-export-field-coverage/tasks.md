## 1. Field coverage in columnar exports
- [x] 1.1 Add `left` to the `includes` struct in the Arrow/DuckDB export schema
- [x] 1.2 Export `active_period` and `last_verified`, or document them as source-only in README and ai-consumers
- [x] 1.3 Update the schema/export parity test allowlist accordingly
- [x] 1.4 Verify the former-membership recipes return identical results on JSONL and Parquet/DuckDB paths

## 2. Plain JSONL and YAML symmetry
- [x] 2.1 Emit uncompressed `countries.jsonl`, `intblocks.jsonl`, `blocktypes.jsonl` at build time
- [x] 2.2 Decide and apply one policy for YAML exports (all plain, all zst, or both) and document it
- [x] 2.3 List the new artifacts in README's output-files table and `llms.txt`

## 3. Memberships edge export
- [x] 3.1 Generate `memberships.parquet` and `memberships.csv` (`intblock_id`, `country_code`, `status`, `joined`, `left`) from `includes` at build time
- [x] 3.2 Add a `memberships` table to `internacia.duckdb`
- [x] 3.3 Add row-count consistency (edge rows == sum of country-type includes) to `check_generated_artifacts.py`
- [x] 3.4 Document edge-table joins in `docs/query-examples.md` with a tested recipe

## 4. Verification
- [x] 4.1 Full build + `check_generated_artifacts` green
- [x] 4.2 `pytest tests/` green including new parity tests
