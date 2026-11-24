# Agent guide: querying Internacia data

Platform-neutral workflow for looking up countries, borders, org membership, and entity linking.
Works with Cursor, Claude Code, Copilot, Codex, and any agent with file or API access.

## Before querying

1. Read [llms.txt](../../llms.txt) for join keys and gotchas (compact index).
2. Use exported datasets — **do not parse** `data/countries/*.yaml` or `data/intblocks/**/*.yaml` unless authoring.
3. Full consumption contract: [ai-consumers.md](../ai-consumers.md).
4. Query recipes: [query-examples.md](../query-examples.md) (DuckDB),
   [query-examples-polars.md](../query-examples-polars.md) (Polars / Parquet),
   [query-examples-r.md](../query-examples-r.md) (R / dplyr),
   [query-examples-observable.md](../query-examples-observable.md) (Observable / Plot).

## Access paths

| Method | Path / URL |
|--------|------------|
| DuckDB (preferred) | `data/datasets/internacia.duckdb` after `python scripts/builder.py build`, or the latest Release asset (exports are not committed) |
| Parquet | `data/datasets/countries.parquet`, `intblocks.parquet`, `blocktypes.parquet`, `memberships.parquet`, `trade_agreements.parquet`, `trade_agreement_parties.parquet`, `trade_agreement_instruments.parquet` |
| Version check | `SELECT * FROM _meta;` or `data/datasets/*.manifest.json` |
| Python SDK (no full checkout) | https://github.com/datenoio/internacia-python (`internacia` 0.5.0 on PyPI reads data contracts 3.x and 4.x, not the current 5.x — see [SDK status](../llm-scenarios.md#sdk-status)) |
| HTTP API | https://github.com/datenoio/internacia-api (**in development**, self-host only; no public hosted instance) |

## Join keys

| Entity | Primary key | Also useful |
|--------|-------------|-------------|
| Country | `code` (alpha-2) | `iso3code`, `numeric_code`, `wikidata_id` |
| Intblock | `id` | `wikidata_id`, `blocktype`, `partof` |
| Membership | `includes[].id` → country `code` | **Not** `includes[].name` |
| Blocktype taxonomy | `blocktypes.id` | matches values in `intblocks.blocktype` list |
| Borders | alpha-3 in `borders` | join on neighbor `iso3code` |
| Trade agreement | `trade_agreements.id` | `intblock_id` (roster of a 3+ party agreement), `wto_rta_id`, `dta_id` |
| Agreement party | `trade_agreement_parties.party_id` | country `code` or intblock `id`, by `party_type` |

## Scope (in / out)

**In scope:** ISO identifiers, geography, demographics with source/year, World Bank classifications, languages/currencies/timezones, org membership, trade and investment agreements (parties, status, dates), Wikidata links.

**Out of scope:** HDI, GDP, government type, internet penetration, time-series indicators — enrich downstream from other datasets.

## Canonical queries (DuckDB)

Version and schema:

```sql
SELECT dataset, version, schema_hash, build_date FROM _meta;
```

Current ISO countries (249):

```sql
SELECT code, name FROM countries
WHERE code_status = 'official_iso3166_1' ORDER BY code;
```

UN members:

```sql
SELECT code, name FROM countries WHERE un_member = true ORDER BY name;
```

Country attribute fields (former attribute intblocks — prefer these over retired
`LHTRAFFIC` / `DVD_*` / `WS*` / `LS*` / `*GAUGE` ids; remap via
`attribute_intblock_migrations.json`):

```sql
SELECT code, name FROM countries WHERE car_side = 'left';
SELECT code, name FROM countries WHERE dvd_region = 1;
SELECT c.code, c.name FROM countries c, UNNEST(c.writing_directions) t(d) WHERE d.id = 'rtl';
SELECT c.code, c.name FROM countries c, UNNEST(c.legal_systems) t(l) WHERE l.id = 'common_law';
```

Land neighbors (alpha-3 borders — join on `iso3code`):

```sql
SELECT n.code, n.name
FROM countries th,
     UNNEST(th.borders) AS b(neighbor_iso3)
JOIN countries n ON n.iso3code = b.neighbor_iso3
WHERE th.code = 'TH'
ORDER BY n.name;
```

Org members (NATO example):

```sql
SELECT m.id AS member_code, m.name AS member_label, m.status
FROM intblocks i, UNNEST(i.includes) AS t(m)
WHERE i.id = 'NATO' AND m.type = 'country';
```

Orgs that include a country (Laos example):

```sql
SELECT i.id, i.name
FROM intblocks i, UNNEST(i.includes) AS t(m)
WHERE m.id = 'LA' AND m.type = 'country'
ORDER BY i.name;
```

Resolve intblock alias before join (Python):

```python
import json
import pandas as pd

aliases = {a["alias"]: a["target"] for a in json.load(open("data/datasets/intblocks_aliases.json"))}
blocks = pd.read_parquet("data/datasets/intblocks.parquet")
blocks["id"] = blocks["id"].map(lambda x: aliases.get(x, x))
```

Structured population field (Pandas — `.struct` needs the Arrow dtype backend):

```python
df = pd.read_parquet("data/datasets/countries.parquet", dtype_backend="pyarrow")
pop = df["population"].struct.field("value")
```

## Trade agreements

Trade and investment agreements live in the registry tables `trade_agreements`,
`trade_agreement_parties` and `trade_agreement_instruments`, plus the
`country_trade_agreements` view (one row per country and current agreement; a bloc party
such as the EU expands to its current members with `via = 'EU'`). Two-party FTAs are only
in the registry: since 5.0.0 they are not intblocks. Filter on `agreement_type` when you
count trade agreements, because investment treaties, trade relations agreements and
preference schemes share the table.

```sql
SELECT c.agreement_id, c.agreement_type, c.via
FROM country_trade_agreements c
WHERE c.country_code = 'CL' AND c.agreement_status = 'in_force'
  AND c.agreement_type NOT IN ('investment', 'trade_relations', 'preference_scheme')
ORDER BY c.agreement_id;
```

Field semantics: [ai-consumers.md](../ai-consumers.md#trade-agreements-registry);
more SQL: [llm-scenarios.md](../llm-scenarios.md#29-trade-agreements-of-a-country).

## Common mistakes

| Mistake | Correct approach |
|---------|------------------|
| Join borders on alpha-2 | Use alpha-3; join `borders` → `iso3code` |
| Join intblocks on `includes[].name` | Use `includes[].id` (country code) |
| Assume 256 codes are all ISO official | Filter `code_status = 'official_iso3166_1'` |
| Read plain number from `population` | Use struct field `.value` (pandas: `dtype_backend="pyarrow"`; Polars: `.struct.field("value")`) |
| Expect HDI/GDP in this dataset | Out of scope; enrich downstream |
| Ignore alias remaps | Load `intblocks_aliases.json` before joining on intblock `id` |
| Look for a two-party FTA in `intblocks` | Query `trade_agreements` / `country_trade_agreements`; aliases with `reason = 'moved'` point there |

## DuckDB struct lists

Unnest list-of-struct columns: `UNNEST(i.includes) AS t(m)` then reference `m.id`, `m.type`, `m.status`.

## Related

- [AGENTS.md](../../AGENTS.md) — root routing hub
- [AGENTS.zh.md](../../AGENTS.zh.md) — 中文路由入口
- [contribute.md](contribute.md) — editing YAML (maintainers)
- [discover.md](discover.md) — find missing intblocks / improve existing records
- [zh/query.md](zh/query.md) — 中文查询指南
