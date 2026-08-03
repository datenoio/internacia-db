# Change: Fix false documented examples and make all doc recipes test-backed

## Why
An independent audit (dev/internacia-db-review.md, verified 2026-08-02) confirmed four classes of documented examples that fail when an agent or user runs them: (1) the World Bank region filter `region.value = 'Europe & Central Asia'` returns 0 rows because the stored value is `'Europe & Central Asia (all income levels)'` — this example has no "Expected:" count and no test coverage; (2) the pandas `.struct.field()` examples in 5 doc locations raise `AttributeError` with default pandas (verified on pandas 3.0.3: parquet structs load as object dicts unless `dtype_backend="pyarrow"`); (3) the "~33 entities missing WB classifications" figure repeated in 4 docs is wrong (actual: 8 missing `region`/`incomeLevel`, 39 missing `adminregion`); (4) four cross-join recipes (`JOIN intblocks i ON TRUE`) in `docs/query-examples.md` and `tests/test_documented_queries.py` exhaust memory (reproduced: `OutOfMemoryException` under a 1 GB limit; the corresponding tests are SIGKILLed). Additionally `llms.txt:29` falsely claims "Each property includes a description field" while `countries.schema.json` has descriptions on 4/40 properties and `intblocks.schema.json` on 16/35.

## What Changes
- Correct the World Bank region example in `docs/query-examples.md` and `docs/ai-consumers.md` to use the actual stored value, add an "Expected:" row count, and add it to `tests/test_documented_queries.py`.
- Fix the pandas struct examples in `README.md`, `docs/query-examples.md`, `docs/agents/query.md`, and `docs/ai-consumers.md` to use `pd.read_parquet(..., dtype_backend="pyarrow")` (or `df["population"].str["value"]` for default dtypes), and add a pandas smoke test.
- Replace the "~33" classification-gap figure with computed values in `llms.txt`, `AGENTS.md`, `docs/ai-consumers.md`, and `docs/query-examples.md` (two occurrences).
- Rewrite the four memory-exhausting `ON TRUE` cross-join recipes to UNNEST-first form in `docs/query-examples.md`, `docs/query-examples.zh.md`, and `tests/test_documented_queries.py`, and require documented recipes to run under a bounded DuckDB memory limit.
- Fix the false schema-descriptions claim in `llms.txt` (either backfill property descriptions in `data/schemas/*.schema.json` or correct the sentence).

## Impact
- Affected specs: contributor-docs
- Affected code: `README.md`, `llms.txt`, `AGENTS.md`, `docs/query-examples.md`, `docs/query-examples.zh.md`, `docs/ai-consumers.md`, `docs/agents/query.md`, `tests/test_documented_queries.py`, optionally `data/schemas/*.schema.json`
