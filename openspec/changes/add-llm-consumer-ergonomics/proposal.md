# Change: Expand LLM consumer ergonomics and policy-researcher cookbook

## Why
The deep review identified missing token-budget guidance, embedding/RAG recipes, OpenAI tool-call schemas, and policy-researcher query examples. Phase 3 items do not require schema changes but benefit from a tracked change linking docs and test-backed examples.

## What Changes
- Add `data/schemas/country_lookup.openai.json` and `intblock_lookup.openai.json` for tool-use APIs.
- Add token budget tables to `llms.txt` and `llms-full.txt`.
- Add embedding/RAG section and policy-researcher membership queries to `docs/query-examples.md` with tests.
- Document `includes[].status` enum values in `docs/ai-consumers.md` (catalog already exists in `includes_status.yaml`).

## Impact
- Affected specs: contributor-docs
- Affected code: `data/schemas/`, `docs/`, `llms.txt`, `tests/test_documented_queries.py`
