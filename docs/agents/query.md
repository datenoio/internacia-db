# Agent guide: querying Internacia data

Platform-neutral workflow for looking up countries, borders, org membership, and entity linking.
Works with Cursor, Claude Code, Copilot, Codex, and any agent with file or API access.

## Before querying

1. Read [llms.txt](../../llms.txt) for join keys and gotchas (compact index).
2. Use exported datasets — **do not parse** `data/countries/*.yaml` or `data/intblocks/**/*.yaml` unless authoring.
3. Full consumption contract: [ai-consumers.md](../ai-consumers.md).
4. Verified recipes: [query-examples.md](../query-examples.md).

## Access paths

| Method | Path / URL |
|--------|------------|
| DuckDB (preferred, in-repo) | `data/datasets/internacia.duckdb` |
| Parquet | `data/datasets/countries.parquet`, `intblocks.parquet`, `blocktypes.parquet` |
| Version check | `SELECT * FROM _meta;` or `data/datasets/*.manifest.json` |
| Python SDK (no full checkout) | https://github.com/commondataio/internacia-python |
| HTTP API (no local files) | https://github.com/commondataio/internacia-api |

## Join keys

| Entity | Primary key | Also useful |
|--------|-------------|-------------|
| Country | `code` (alpha-2) | `iso3code`, `numeric_code`, `wikidata_id` |
| Intblock | `id` | `wikidata_id`, `blocktype`, `partof` |
| Membership | `includes[].id` → country `code` | **Not** `includes[].name` |
| Blocktype taxonomy | `blocktypes.id` | matches values in `intblocks.blocktype` list |
| Borders | alpha-3 in `borders` | join on neighbor `iso3code` |

## Scope (in / out)

**In scope:** ISO identifiers, geography, demographics with source/year, World Bank classifications, languages/currencies/timezones, org membership, Wikidata links.

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

Structured population field (Pandas):

```python
df = pd.read_parquet("data/datasets/countries.parquet")
pop = df["population"].struct.field("value")
```

## Common mistakes

| Mistake | Correct approach |
|---------|------------------|
| Join borders on alpha-2 | Use alpha-3; join `borders` → `iso3code` |
| Join intblocks on `includes[].name` | Use `includes[].id` (country code) |
| Assume 256 codes are all ISO official | Filter `code_status = 'official_iso3166_1'` |
| Read plain number from `population` | Use struct field `.value` |
| Expect HDI/GDP in this dataset | Out of scope; enrich downstream |
| Ignore alias remaps | Load `intblocks_aliases.json` before joining on intblock `id` |

## DuckDB struct lists

Unnest list-of-struct columns: `UNNEST(i.includes) AS t(m)` then reference `m.id`, `m.type`, `m.status`.

## Related

- [AGENTS.md](../../AGENTS.md) — root routing hub
- [AGENTS.zh.md](../../AGENTS.zh.md) — 中文路由入口
- [contribute.md](contribute.md) — editing YAML (maintainers)
- [zh/query.md](zh/query.md) — 中文查询指南
