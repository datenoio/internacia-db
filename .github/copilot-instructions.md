# Copilot instructions for internacia-db

See [AGENTS.md](../AGENTS.md) for full agent routing.

## Data access

- Prefer `data/datasets/internacia.duckdb` or Parquet exports over parsing source YAML.
- Python SDK: [internacia-python](https://github.com/datenoio/internacia-python).
- internacia-api is **self-host only** ([internacia-api](https://github.com/datenoio/internacia-api)); no public hosted HTTP API.

## Scope

Countries are **reference data only**. Do not add HDI, GDP, government type, internet penetration, or similar socioeconomic profile fields.

## Join rules

- Countries: primary key `code` (alpha-2); borders are alpha-3 — join on `iso3code`.
- Intblocks: primary key `id`; membership via `includes[].id` (not `includes[].name`).

## Editing data

Follow [docs/agents/contribute.md](../docs/agents/contribute.md). Run validators before proposing changes:

```bash
python scripts/validate_countries.py --json
python scripts/validate_intblocks.py --json
```

Schema or breaking changes require an OpenSpec proposal first — see [docs/agents/openspec-quickstart.md](../docs/agents/openspec-quickstart.md).
