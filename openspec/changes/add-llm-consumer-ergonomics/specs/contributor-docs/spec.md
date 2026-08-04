## ADDED Requirements

### Requirement: LLM tool-call schema artifacts

The repository SHALL publish compact JSON Schema subsets at `data/schemas/country_lookup.openai.json` and `data/schemas/intblock_lookup.openai.json` suitable for OpenAI function-calling and similar tool-use APIs, documented in `docs/ai-consumers.md`.

#### Scenario: Agent loads country lookup schema

- **WHEN** an integrator reads `country_lookup.openai.json`
- **THEN** it defines query parameters for lookup by ISO code or name without nested struct definitions

### Requirement: Token budget guidance

`llms.txt` SHALL include approximate token counts or relative size guidance for major consumption paths (full Parquet/JSON vs lite exports vs DuckDB projection queries).

#### Scenario: Agent chooses lite path

- **WHEN** an LLM agent reads llms.txt before loading data
- **THEN** it finds token budget hints recommending lite exports for entity-linking-only tasks

### Requirement: Policy-researcher query recipes

`docs/query-examples.md` SHALL include tested membership-analysis queries for policy researchers (organization overlap, former members, regional community density, succession chains) validated by `tests/test_documented_queries.py`.

#### Scenario: NATO and EU overlap query tested

- **WHEN** CI runs documented query tests
- **THEN** the NATO∩EU membership query returns the expected country count

### Requirement: Documented includes status enum

`docs/ai-consumers.md` SHALL list canonical `includes[].status` values from `data/schemas/includes_status.yaml` with semantics for LLM-generated filters.

#### Scenario: Status filter documented

- **WHEN** a consumer reads ai-consumers membership section
- **THEN** they find definitions for `member`, `former_member`, `observer`, and `founding_member`
