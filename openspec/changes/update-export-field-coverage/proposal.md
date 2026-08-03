# Change: Export former-membership fields, plain JSONL, and a memberships edge table

## Why
Verified on 2026-08-02: the Parquet and DuckDB exports silently drop intblock fields including `includes[].left` (the DuckDB `includes` struct carries only `id, name, type, status, joined, role, note`), along with `active_period` and `last_verified`. This breaks the flagship former-membership query recipes on the columnar path — departure dates exist only in YAML/JSONL sources. Additionally, JSONL is shipped only zstd-compressed (no plain JSONL/JSON/CSV anywhere), which strands agents in restricted sandboxes without zstd, and every roster analytic requires UNNEST gymnastics because no flattened membership table exists.

## What Changes
- Add `left` (and any other includes sub-fields present in source) to the Arrow/DuckDB `includes` struct; export `active_period` and `last_verified` as columns, or — where a field is deliberately source-only — document the divergence prominently in `README.md` and `docs/ai-consumers.md`.
- Ship plain (uncompressed) `countries.jsonl`, `intblocks.jsonl`, and `blocktypes.jsonl` alongside the `.zst` variants; resolve the YAML asymmetry (`blocktypes.yaml` plain vs `countries`/`intblocks` zstd-only) in the same pass.
- Add a flattened `memberships` edge export (`intblock_id`, `country_code`, `status`, `joined`, `left`) as Parquet and CSV plus a DuckDB table, generated at build time from `includes`.
- Extend the artifact-consistency guard and export parity tests to cover the new artifacts and fields.

## Impact
- Affected specs: dataset-release
- Affected code: `internacia_builder/build.py` (Arrow schemas, writers), `scripts/check_generated_artifacts.py`, `tests/` (export parity), `README.md`, `docs/ai-consumers.md`, `llms.txt`, new artifacts under `data/datasets/`
