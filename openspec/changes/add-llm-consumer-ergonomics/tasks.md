## 1. Tool schemas
- [x] 1.1 Add `country_lookup.openai.json` and `intblock_lookup.openai.json` under `data/schemas/`
- [x] 1.2 Document in `docs/ai-consumers.md`

## 2. Token budgets
- [x] 2.1 Measure approximate token counts for full vs lite exports (after lite ships or estimate from Parquet)
- [x] 2.2 Add guidance tables to `llms.txt` and `llms-full.txt`

## 3. Query cookbook
- [x] 3.1 Add embedding/RAG recipe section to `docs/query-examples.md`
- [x] 3.2 Add policy-researcher section (NATO∩EU, former members, regional EC overlap, succession chains)
- [x] 3.3 Extend `tests/test_documented_queries.py` for new recipes

## 4. Membership status documentation
- [x] 4.1 Document `includes[].status` values and semantics in `docs/ai-consumers.md` referencing `includes_status.yaml`
