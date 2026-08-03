# Internacia DB — AI agent guide

Structured reference data: **256 countries**, **1037 intblocks** (organizations/groups),
**78 blocktypes**. Licensed CC-BY-4.0 (data); code is MIT.

中文指南：[AGENTS.zh.md](AGENTS.zh.md) · [llms.zh.txt](llms.zh.txt)

## What do you need?

| Goal | Start here | Do not |
|------|------------|--------|
| **Query, join, or enrich** downstream data | [llms.txt](llms.txt) → [docs/ai-consumers.md](docs/ai-consumers.md) | Parse source YAML under `data/countries/` or `data/intblocks/` |
| **Look up countries, borders, org membership** | [docs/agents/query.md](docs/agents/query.md) | Join intblocks on `includes[].name` (use `includes[].id`) |
| **Edit country or intblock YAML** | [docs/agents/contribute.md](docs/agents/contribute.md) | Hand-edit `data/datasets/` (generated only) |
| **Schema change, new capability, breaking export** | [docs/agents/openspec-quickstart.md](docs/agents/openspec-quickstart.md) → [openspec/AGENTS.md](openspec/AGENTS.md) | Implement before approval |

## Preferred data access

- **DuckDB:** `data/datasets/internacia.duckdb` (tables: `countries`, `intblocks`, `blocktypes`, `_meta`)
- **Parquet:** `data/datasets/{countries,intblocks,blocktypes}.parquet`
- **Remote:** [internacia-api](https://github.com/datenoio/internacia-api), [internacia-python](https://github.com/datenoio/internacia-python)

Check version before upgrading: `SELECT dataset, version, schema_hash FROM _meta;` or read `data/datasets/*.manifest.json`.

## Join keys and gotchas

- Countries: `code` (alpha-2, primary), `iso3code`, `wikidata_id`
- Intblocks: `id` (uppercase, e.g. `NATO`, `EU`); membership via `includes[].id` → country `code`
- **`borders` uses alpha-3**, not alpha-2 — join on `iso3code`
- **`population` / `area` / `gini` are structs** — use `.value` for the number; `year` is null when unknown (never 0)
- Current ISO countries only (249): `code_status = 'official_iso3166_1'`
- Intblock id renames: consult `data/datasets/intblocks_aliases.json`

## Never (scope guardrails)

- Add socioeconomic profile fields to countries (HDI, GDP, government type, internet penetration, etc.)
- Treat all 256 country codes as official ISO — filter on `code_status`
- Assume missing World Bank `region` / `incomeLevel` is an error (8 entities are unclassified; `adminregion` is absent for 39 high-income economies by design)
- Read `data/_legacy/` — obsolete pre-1.0 snapshots kept for historical reference only

## Validation (contributors)

```bash
python scripts/validate_countries.py          # human-readable output
python scripts/validate_countries.py --json   # structured output for agents
python scripts/validate_intblocks.py --json
pytest tests/
```

## Query examples

Verified DuckDB recipes: [docs/query-examples.md](docs/query-examples.md) (backed by `tests/test_documented_queries.py`).
Polars / Parquet: [docs/query-examples-polars.md](docs/query-examples-polars.md) (backed by `tests/test_documented_queries_polars.py`).
Chinese: [docs/query-examples.zh.md](docs/query-examples.zh.md).

## Platform shims

- [AGENTS.zh.md](AGENTS.zh.md) · [llms.zh.txt](llms.zh.txt) — 中文（Kimi K3、GLM、通义灵码）
- [.kimi/AGENTS.md](.kimi/AGENTS.md) — Kimi Code
- [.lingma/rules/](.lingma/rules/) — 通义灵码 Project Rules
- [CLAUDE.md](CLAUDE.md) — Claude Code
- [.github/copilot-instructions.md](.github/copilot-instructions.md) — GitHub Copilot
- [llms-full.txt](llms-full.txt) — extended index for crawlers
- [.cursor/skills/](.cursor/skills/) — thin Cursor wrappers → `docs/agents/`
- [.agent/workflows/](.agent/workflows/) — portable step-by-step workflows

<!-- OPENSPEC:START -->
# OpenSpec Instructions

These instructions are for AI assistants working in this project.

Always open `@/openspec/AGENTS.md` when the request:
- Mentions planning or proposals (words like proposal, spec, change, plan)
- Introduces new capabilities, breaking changes, architecture shifts, or big performance/security work
- Sounds ambiguous and you need the authoritative spec before coding

Use `@/openspec/AGENTS.md` to learn:
- How to create and apply change proposals
- Spec format and conventions
- Project structure and guidelines
- **Countries dataset scope**: reference data only — do not add socioeconomic profile fields (HDI, GDP, government type, etc.)

Keep this managed block so 'openspec update' can refresh the instructions.

<!-- OPENSPEC:END -->
