## 1. World Bank region example
- [x] 1.1 Update `docs/query-examples.md:79` and `docs/ai-consumers.md:244` — implemented by filtering on the stable `region.id` (`ECS`) instead of the label, with the expected row count stated (more robust than matching the suffixed label)
- [x] 1.2 Add the corrected query to `tests/test_documented_queries.py` with an expected-count assertion
- [x] 1.3 Document the "(all income levels)" suffix gotcha next to the example (list actual distinct `region.value` strings)

## 2. Pandas struct examples
- [x] 2.1 Update `README.md:155`, `docs/query-examples.md:947-948`, `docs/agents/query.md:103`, and `docs/ai-consumers.md:148-149` to use `dtype_backend="pyarrow"` or dict-style access
- [x] 2.2 Add a pandas smoke test that loads `countries.parquet` with a default install and executes the documented snippet

## 3. Classification gap figures
- [x] 3.1 Compute actual missing counts (currently 8 for `region`/`incomeLevel`/`lendingType`, 39 for `adminregion`) and update `llms.txt`, `AGENTS.md`, `docs/ai-consumers.md`, `docs/query-examples.md` (both occurrences)
- [x] 3.2 Add a test asserting the documented figures match the computed counts (same drift-gate pattern as other documented counts)

## 4. Memory-exhausting recipes
- [x] 4.1 Rewrite the four `JOIN intblocks i ON TRUE` recipes in `docs/query-examples.md` (lines ~595, 610, 650, 807) and their zh twins to UNNEST-first form
- [x] 4.2 Update the corresponding queries in `tests/test_documented_queries.py` and set an explicit DuckDB `memory_limit` in the test fixture so regressions fail instead of OOM-killing the runner

## 5. Schema descriptions claim
- [x] 5.1 Either backfill `description` on all properties in `data/schemas/countries.schema.json` (4/40 today) and `data/schemas/intblocks.schema.json` (16/35 today), or correct `llms.txt:29`
- [x] 5.2 If backfilling, add a validation check that every top-level schema property carries a description

## 6. Verification
- [x] 6.1 Run `pytest tests/test_documented_queries.py` — all green, no SIGKILL
- [x] 6.2 Run the markdown link checker over edited docs
