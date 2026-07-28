---
description: Look up organization membership via DuckDB or exported datasets.
---
<!-- AGENT:START -->
**Goal:** Find members of an intblock (e.g. NATO, EU, ASEAN) or orgs that include a given country.

**Read first:** [docs/agents/query.md](../../docs/agents/query.md) and [llms.txt](../../llms.txt).

**Guardrails**
- Use exported datasets (`data/datasets/internacia.duckdb`), not source YAML.
- Join on `includes[].id` (country alpha-2), never `includes[].name`.
- Resolve intblock aliases from `data/datasets/intblocks_aliases.json` before joining on `id`.

**Steps**
1. Confirm DuckDB exists: `data/datasets/internacia.duckdb` (build with `python scripts/builder.py build --formats duckdb` if missing).
2. Check version: `SELECT dataset, version, schema_hash FROM _meta;`
3. For org → members, run (replace `ORG_ID`):

```sql
SELECT m.id AS member_code, m.name AS member_label, m.status, m.type
FROM intblocks i, UNNEST(i.includes) AS t(m)
WHERE i.id = 'ORG_ID' AND m.type = 'country'
ORDER BY m.id;
```

4. For country → orgs, run (replace `CC` with alpha-2 code):

```sql
SELECT i.id, i.name, m.status
FROM intblocks i, UNNEST(i.includes) AS t(m)
WHERE m.id = 'CC' AND m.type = 'country'
ORDER BY i.name;
```

5. Compare row counts to expectations in [docs/query-examples.md](../../docs/query-examples.md) when available.

**Reference**
- Full cookbook: [docs/query-examples.md](../../docs/query-examples.md)
- Remote access without checkout: [internacia-api](https://github.com/commondataio/internacia-api)
<!-- AGENT:END -->
