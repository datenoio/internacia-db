# Query examples

Verified DuckDB recipes against `data/datasets/internacia.duckdb`. For scope, join keys,
and field semantics see [ai-consumers.md](ai-consumers.md).

**DuckDB struct lists:** use `UNNEST(column) AS t(row)` and reference `row.field` (e.g.
`UNNEST(i.includes) AS t(m)` then `m.id`, `m.type`).

```bash
duckdb data/datasets/internacia.duckdb
```

## Country filters

### UN members only

```sql
SELECT code, name
FROM countries
WHERE un_member = true
ORDER BY name;
```

**Expected:** 192 rows.

**Gotcha:** `un_member` is a country-level boolean. The `UN` intblock roster (193 country
entries via `includes`) can differ slightly — use the flag for a simple filter, or unnest
the `UN` intblock when you need roster metadata (`status`, `joined`).

### Current ISO countries only (249)

```sql
SELECT code, name, iso3code
FROM countries
WHERE code_status = 'official_iso3166_1'
ORDER BY code;
```

**Expected:** 249 rows. Seven non-standard codes (`AN`, `JG`, `KV`, `XA`, `XS`, `XT`, `XN`)
are excluded. See [country-code-policy.md](country-code-policy.md).

### Sovereign states

```sql
SELECT code, name, entity_type
FROM countries
WHERE entity_type = 'sovereign_state'
ORDER BY name;
```

**Expected:** 194 rows.

### Independent but not UN members

```sql
SELECT code, name
FROM countries
WHERE independent = true AND un_member = false;
```

**Expected:** 2 rows (`GW` Guinea-Bissau, `VA` Vatican City).

### Landlocked countries

```sql
SELECT code, name, subregion
FROM countries
WHERE landlocked
ORDER BY name;
```

**Expected:** 44 rows.

### By World Bank region

```sql
SELECT code, name, region.value AS region
FROM countries
WHERE region.value = 'Europe & Central Asia'
  AND code_status = 'official_iso3166_1'
ORDER BY name;
```

**Gotcha:** `region`, `incomeLevel`, and `lendingType` are structs `{id, value}`. They are
absent for ~33 territories the World Bank does not classify.

### By income level

```sql
SELECT code, name, incomeLevel.value AS income
FROM countries
WHERE incomeLevel.value = 'Low income'
ORDER BY name;
```

**Expected:** 41 rows.

## Geography and borders

Land neighbors are stored as **ISO 3166-1 alpha-3** codes in `borders`. Join on
`countries.iso3code`, not `code`.

### Neighbors of Thailand

```sql
SELECT n.code, n.name, n.iso3code
FROM countries th,
     UNNEST(th.borders) AS b(neighbor_iso3)
JOIN countries n ON n.iso3code = b.neighbor_iso3
WHERE th.code = 'TH'
ORDER BY n.name;
```

**Expected:** 4 rows — `KH` Cambodia, `LA` Lao PDR, `MM` Myanmar, `MY` Malaysia.

### Reverse lookup: who borders Laos?

```sql
SELECT code, name
FROM countries
WHERE list_contains(borders, 'LAO')
ORDER BY name;
```

**Expected:** 5 rows (China, Cambodia, Myanmar, Thailand, Vietnam).

### Countries with the most land borders

```sql
SELECT code, name, len(borders) AS border_count
FROM countries
WHERE len(borders) > 0
ORDER BY border_count DESC
LIMIT 10;
```

**Expected top:** `CN` (16), `RU` (14), `BR` (10).

### Landlocked in Southeast Asia

```sql
SELECT code, name
FROM countries
WHERE landlocked AND subregion = 'South-Eastern Asia';
```

**Expected:** 1 row (`LA` Lao PDR).

### Island nations and territories (no land borders)

```sql
SELECT code, name
FROM countries
WHERE len(borders) = 0
ORDER BY name;
```

**Expected:** 93 rows. Empty list, not `NULL`.

## Intblocks and membership

Join on `includes[].id` (usually country alpha-2). **`includes[].name` is a display label
only** — do not use it for joins.

### Organizations that include Laos

```sql
SELECT i.id, i.name, m.status, m.joined
FROM intblocks i, UNNEST(i.includes) AS t(m)
WHERE m.id = 'LA' AND m.type = 'country'
ORDER BY i.name;
```

**Expected:** 187 rows (ASEAN, UN agencies, trade agreements, sports federations, etc.).

Filter to a bloc:

```sql
SELECT i.id, i.name, m.status
FROM intblocks i, UNNEST(i.includes) AS t(m)
WHERE i.id = 'ASEAN' AND m.type = 'country'
ORDER BY m.id;
```

**Expected:** 11 ASEAN member states.

### NATO members

```sql
SELECT m.id AS code, m.name, m.status, m.joined
FROM intblocks i, UNNEST(i.includes) AS t(m)
WHERE i.id = 'NATO' AND m.type = 'country'
ORDER BY m.id;
```

**Expected:** 32 rows.

### EU members

```sql
SELECT m.id AS code, m.name, m.status
FROM intblocks i, UNNEST(i.includes) AS t(m)
WHERE i.id = 'EU' AND m.type = 'country'
ORDER BY m.id;
```

**Expected:** 27 rows.

### Observer members of an organization

```sql
SELECT i.id, i.name, m.id AS member_code, m.name AS member_label
FROM intblocks i, UNNEST(i.includes) AS t(m)
WHERE i.id = 'BSEC' AND m.status = 'observer'
ORDER BY m.id;
```

**Expected:** 14 observer entries for BSEC (Black Sea Economic Cooperation).

### Trade blocs by taxonomy

```sql
SELECT i.id, i.name, bt.name AS category
FROM intblocks i
JOIN blocktypes bt ON list_contains(i.blocktype, bt.id)
WHERE bt.id = 'trade'
ORDER BY i.name;
```

**Expected:** 8 rows.

### Formal organizations headquartered in Switzerland

```sql
SELECT id, name, headquarters.city
FROM intblocks
WHERE headquarters.country = 'CH' AND status = 'formal'
ORDER BY name;
```

**Expected:** 51 rows (~46% of intblocks have headquarters populated).

### Child organizations of the UN

```sql
SELECT id, name, partof
FROM intblocks
WHERE list_contains(partof, 'UN')
ORDER BY name;
```

**Expected:** 30 rows.

### Multilingual intblock names

```sql
SELECT id, name, onm.name AS translated_name, onm.id AS lang
FROM intblocks, UNNEST(other_names) AS onm
WHERE onm.id = 'fr'
ORDER BY id
LIMIT 20;
```

## Cross-dataset joins

### UN members not in the EU

```sql
SELECT c.code, c.name
FROM countries c
WHERE c.un_member = true
  AND c.code NOT IN (
    SELECT m.id
    FROM intblocks i, UNNEST(i.includes) AS t(m)
    WHERE i.id = 'EU' AND m.type = 'country'
  )
ORDER BY c.name;
```

**Expected:** 165 rows.

### Countries in both NATO and EU

```sql
WITH nato AS (
  SELECT m.id
  FROM intblocks i, UNNEST(i.includes) AS t(m)
  WHERE i.id = 'NATO' AND m.type = 'country'
),
eu AS (
  SELECT m.id
  FROM intblocks i, UNNEST(i.includes) AS t(m)
  WHERE i.id = 'EU' AND m.type = 'country'
)
SELECT c.code, c.name
FROM countries c
JOIN nato ON c.code = nato.id
JOIN eu ON c.code = eu.id
ORDER BY c.name;
```

**Expected:** 23 rows.

### Compare UN member flag vs UN intblock roster

```sql
SELECT
  (SELECT COUNT(*) FROM countries WHERE un_member = true) AS un_member_flag,
  (SELECT COUNT(*)
   FROM intblocks i, UNNEST(i.includes) AS t(m)
   WHERE i.id = 'UN' AND m.type = 'country') AS un_intblock_roster;
```

**Expected:** 192 vs 193 — small discrepancies are possible; pick one surface and document
your choice.

### Organizations a country belongs to

```sql
SELECT i.id, i.name, i.blocktype
FROM intblocks i, UNNEST(i.includes) AS t(m)
WHERE m.id = 'FR' AND m.type = 'country'
ORDER BY i.name;
```

## Pandas and Polars

### Structured metric fields

```python
import pandas as pd

df = pd.read_parquet("data/datasets/countries.parquet")
df["pop"] = df["population"].struct.field("value")
df["region_name"] = df["region"].struct.field("value")
```

### Membership table from intblocks

```python
import pandas as pd

blocks = pd.read_parquet("data/datasets/intblocks.parquet")
members = blocks.explode("includes").dropna(subset=["includes"])
members = pd.json_normalize(members["includes"])
members = members[members["type"] == "country"]
```

### Resolve intblock id aliases before join

```python
import json
import pandas as pd

aliases = {
    a["alias"]: a["target"]
    for a in json.load(open("data/datasets/intblocks_aliases.json"))
}
blocks = pd.read_parquet("data/datasets/intblocks.parquet")
blocks["id"] = blocks["id"].map(lambda x: aliases.get(x, x))
```

## Other access paths

- **[internacia-python](https://github.com/commondataio/internacia-python)** — typed lookups,
  fuzzy search, filters without writing SQL.
- **[internacia-api](https://github.com/commondataio/internacia-api)** — HTTP access without
  local dataset files.

## Related documentation

- [ai-consumers.md](ai-consumers.md) — consumption contract and common mistakes
- [country-code-policy.md](country-code-policy.md) — entity status and code filtering
- [llms.txt](../llms.txt) — compact index for LLM context windows
