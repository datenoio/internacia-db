## ADDED Requirements

### Requirement: Intblock taxonomy documentation

`docs/ai-consumers.md` SHALL document the `scope_category` field and link to `docs/intblock-inclusion-policy.md`.

#### Scenario: Agent discovers scope filter

- **WHEN** an LLM agent reads `llms.txt` or `docs/ai-consumers.md`
- **THEN** it finds a DuckDB filter example excluding reference enumerations from IGO membership queries
