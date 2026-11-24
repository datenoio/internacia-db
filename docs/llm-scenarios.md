# LLM-friendly scenarios (copy/paste)

These examples are written for code-generating agents:

- Prefer **DuckDB** (`internacia.duckdb` from the GitHub Release assets) — every
  scenario below has a SQL form that works on the current data.
- Use the **Python SDK** only after checking [SDK status](#sdk-status).
- Remember join keys:
  - Intblock membership joins use `includes[].id` (country `code`) / `memberships.country_code`.
  - `countries.borders` contains **ISO alpha-3** neighbor codes; join on `countries.iso3code`.

## SDK status

`internacia` 0.5.0 (the current PyPI release) reads data contracts 3.x and 4.x.
Current Internacia releases are contract 5.x. Verified with `internacia==0.5.0`
against the v5.2.0 DuckDB:

- `InternaciaClient()` without `db_path` downloads the newest **4.x** release, not
  the current data.
- `InternaciaClient(db_path=...)` on a 5.x `internacia.duckdb` raises
  `ContractError`. Pass `check_contract=False` to open it anyway: country and
  intblock lookups, `get_by_acronym`, `search.fuzzy`, `resolve_id` and
  `get_by_member(..., current_only=True)` work.
- The SDK has no trade agreements accessor. For the two-party FTAs that left
  `intblocks` in 5.0.0, `client.intblocks.resolve_id(...)` returns
  `status: moved` but not the table that now holds the id (`trade_agreements`).
  Use the SQL in [scenario 29](#29-trade-agreements-of-a-country).
- `client.intblocks.get_by_member(...)` without `current_only=True` also returns
  organizations the country has **left** (for `US`: NAFTA, SEATO, TPP and more).

SDK 0.6.0, which reads contract 5 and adds `client.trade_agreements`, is on the
SDK's `main` branch but not yet on PyPI. Until it ships, treat the SDK snippets
below as illustrations and run the DuckDB SQL next to them.

## 1. Country lookup by ISO alpha-2

```python
from internacia import InternaciaClient

client = InternaciaClient()
country = client.countries.get_by_code("US")
print(country["name"])
```

DuckDB:

```sql
SELECT code, iso3code, name
FROM countries
WHERE code = 'US';
```

## 2. Country lookup by ISO numeric code

```python
from internacia import InternaciaClient

client = InternaciaClient()
country = client.countries.get_by_numeric_code("840")  # United States
print(country["code"], country["name"])
```

DuckDB:

```sql
SELECT code, name
FROM countries
WHERE numeric_code = '840';
```

## 3. All UN member countries

DuckDB:

```sql
SELECT code, name
FROM countries
WHERE un_member = true
ORDER BY name;
```

Python SDK:

```python
from internacia import InternaciaClient

client = InternaciaClient()
countries = client.countries.get_un_members()
for c in countries[:5]:
    print(c["code"], c["name"])
```

## 4. Membership roster: blocks that contain a country (e.g., US in NATO)

Python SDK (returns matching blocks without membership status; without
`current_only=True` it also returns organizations the country has left — see
[SDK status](#sdk-status)):

```python
from internacia import InternaciaClient

client = InternaciaClient()
blocks = client.intblocks.get_by_member("US", current_only=True)
for b in blocks[:5]:
    print(b["id"], b["name"])
```

DuckDB (current members only, with membership edge metadata):

```sql
SELECT i.id, i.name, m.status, m.joined
FROM memberships m
JOIN intblocks i ON i.id = m.intblock_id
WHERE m.country_code = 'US'
  AND m.status IN ('member', 'founding_member')
ORDER BY m.joined NULLS LAST
LIMIT 20;
```

## 5. Land neighbors: neighbors of Germany

DuckDB (borders are ISO alpha-3; join on `iso3code`):

```sql
SELECT n.code, n.name
FROM countries g,
     UNNEST(g.borders) AS b(iso3)
JOIN countries n ON n.iso3code = b.iso3
WHERE g.code = 'DE'
ORDER BY n.name;
```

## 6. Fuzzy match messy names (multilingual)

```python
from internacia import InternaciaClient

client = InternaciaClient()
results = client.search.fuzzy("United States", limit=5)
for r in results:
    print(r["type"], r["name"])
```

Example in a non-English script:

```python
from internacia import InternaciaClient

client = InternaciaClient()
results = client.search.fuzzy("欧盟", limit=5)
for r in results:
    print(r["type"], r["name"])
```

DuckDB (exact and approximate matches over names, other-language names, and
intblock acronyms; replace both search strings):

```sql
WITH names AS (
  SELECT 'country' AS type, code AS id, name AS label, name AS alias FROM countries
  UNION ALL
  SELECT 'country', c.code, c.name, o.name FROM countries c, UNNEST(c.other_names) AS t(o)
  UNION ALL
  SELECT 'intblock', id, name, name FROM intblocks
  UNION ALL
  SELECT 'intblock', i.id, i.name, o.name FROM intblocks i, UNNEST(i.other_names) AS t(o)
  UNION ALL
  SELECT 'intblock', i.id, i.name, a.value FROM intblocks i, UNNEST(i.acronyms) AS t(a)
)
SELECT type, id, label,
       max(jaro_winkler_similarity(lower(alias), lower('欧盟'))) AS score
FROM names
GROUP BY type, id, label
ORDER BY score DESC, id
LIMIT 5;
```

## 7. Blocks by acronym (e.g., EU)

```python
from internacia import InternaciaClient

client = InternaciaClient()
eu_blocks = client.intblocks.get_by_acronym("EU")
for b in eu_blocks[:5]:
    print(b["id"], b["name"])
```

DuckDB:

```sql
SELECT DISTINCT i.id, i.name
FROM intblocks i,
     UNNEST(i.acronyms) AS t(a)
WHERE upper(a.value) = 'EU'
ORDER BY i.id;
```

## 8. Blocks by tag (e.g., trade)

```python
from internacia import InternaciaClient

client = InternaciaClient()
blocks = client.intblocks.get_by_tag("trade")
for b in blocks[:5]:
    print(b["id"], b["name"])
```

DuckDB:

```sql
SELECT id, name
FROM intblocks
WHERE list_contains(tags, 'trade')
ORDER BY id
LIMIT 20;
```

## 9. Former membership roster (historical memberships)

DuckDB:

```sql
SELECT i.id, i.name, m.left
FROM memberships m
JOIN intblocks i ON i.id = m.intblock_id
WHERE m.country_code = 'US'
  AND m.status = 'former_member'
ORDER BY m.left NULLS LAST;
```

## 10. Driving side (country attribute filter)

```sql
SELECT code, name
FROM countries
WHERE car_side = 'left'
ORDER BY code;
```

## 11. Blocks by blocktype (e.g., trade / fisheries)

Python SDK:

```python
from internacia import InternaciaClient

client = InternaciaClient()
blocks = client.intblocks.get_by_blocktype("trade")
for b in blocks[:5]:
    print(b["id"], b["name"])
```

DuckDB:

```sql
SELECT id, name
FROM intblocks
WHERE list_contains(blocktype, 'trade')
ORDER BY id
LIMIT 20;
```

## 12. Blocks by `scope_category`

The six entity kinds are `igo`, `treaty_body`, `policy_forum`,
`reference_enumeration`, `intergovernmental_body`, and
`non_state_organization`. The category does not establish country membership;
join `memberships` only after checking the member status/roster semantics.

DuckDB:

```sql
SELECT id, name
FROM intblocks
WHERE scope_category = 'igo'
ORDER BY id
LIMIT 20;
```

## 13. Parent/child hierarchy: blocks whose `partof` includes NATO

DuckDB:

```sql
SELECT c.id, c.name
FROM intblocks c,
     UNNEST(c.partof) AS t(parent_id)
WHERE parent_id = 'NATO'
ORDER BY c.id;
```

## 14. Land neighbors of Germany, restricted to current ISO countries

DuckDB:

```sql
SELECT n.code, n.name
FROM countries g,
     UNNEST(g.borders) AS b(iso3)
JOIN countries n ON n.iso3code = b.iso3
WHERE g.code = 'DE'
  AND n.code_status = 'official_iso3166_1'
ORDER BY n.name;
```

## 15. UN members that drive on the left

DuckDB:

```sql
SELECT code, name
FROM countries
WHERE un_member = true
  AND car_side = 'left'
ORDER BY name;
```

Python SDK:

```python
from internacia import InternaciaClient

client = InternaciaClient()
countries = client.countries.get_un_members()

# Filter client-side (car_side is a country attribute)
left_driving = [c for c in countries if c.get("car_side") == "left"]
for c in left_driving[:5]:
    print(c["code"], c["name"])
```

## 16. Blocks by `status` (e.g., formal)

Python SDK:

```python
from internacia import InternaciaClient

client = InternaciaClient()
blocks = client.intblocks.get_by_status("formal")
for b in blocks[:5]:
    print(b["id"], b["name"])
```

DuckDB:

```sql
SELECT id, name
FROM intblocks
WHERE status = 'formal'
ORDER BY id
LIMIT 20;
```

## 17. Remap legacy country codes before lookup/join (KV -> XK, etc.)

Python:

```python
import json

with open("data/datasets/countries_aliases.json", encoding="utf-8") as f:
    aliases = {a["alias"]: a["target"] for a in json.load(f)}

def remap_country_code(code: str) -> str:
    return aliases.get(code, code)

code = remap_country_code("KV")  # example legacy code
```

Then do the normal lookup/join with `code`.

## 18. Population values are structs: use `.value` (not the struct itself)

DuckDB:

```sql
SELECT code, name,
       population.value AS population,
       population.year AS population_year
FROM countries
WHERE population.value IS NOT NULL
ORDER BY population DESC
LIMIT 10;
```

## 19. Membership roster: members vs observers (NATO example)

DuckDB:

Full members (current seats):

```sql
SELECT i.id, i.name, m.status, m.joined
FROM memberships m
JOIN intblocks i ON i.id = m.intblock_id
WHERE m.country_code = 'US'
  AND m.intblock_id = 'NATO'
  AND m.status IN ('member', 'founding_member')
ORDER BY m.joined NULLS LAST;
```

Observers (if you need them):

```sql
SELECT i.id, i.name, m.status, m.joined
FROM memberships m
JOIN intblocks i ON i.id = m.intblock_id
WHERE m.country_code = 'US'
  AND m.intblock_id = 'NATO'
  AND m.status IN ('observer', 'associated_observer')
ORDER BY m.joined NULLS LAST;
```

## 20. Recursive org hierarchy: all descendants of NATO via `partof`

This follows parent links stored in `intblocks.partof` and finds children recursively.

```sql
WITH RECURSIVE org_tree AS (
  -- Start from the root
  SELECT 'NATO' AS id

  UNION ALL

  -- Find children whose partof[] includes any id we already found
  SELECT i.id
  FROM intblocks i
  JOIN org_tree t ON list_contains(i.partof, t.id)
)
SELECT i.id, i.name
FROM intblocks i
WHERE i.id IN (SELECT id FROM org_tree)
ORDER BY i.id;
```

## 21. Entity-linking coverage: only records with `wikidata_id`

```sql
SELECT code, name
FROM countries
WHERE wikidata_id IS NOT NULL
ORDER BY name
LIMIT 20;
```

```sql
SELECT id, name
FROM intblocks
WHERE wikidata_id IS NOT NULL
ORDER BY id
LIMIT 20;
```

## 22. World Bank region/gating gotcha: filter on `region.id`, not `region.value`

```sql
-- Correct (stable ids)
SELECT code, name, region.id AS region_id
FROM countries
WHERE region.id = 'ECS';
```

```sql
-- Incorrect / brittle (labels upstream can vary)
-- WHERE region.value = 'Europe & Central Asia';
```

## 23. Borders join gotcha: `borders` are ISO alpha-3 codes

Correct join pattern (use `countries.iso3code`, not `countries.code`):

```sql
SELECT n.code, n.name
FROM countries g,
     UNNEST(g.borders) AS b(neighbor_iso3)
JOIN countries n ON n.iso3code = b.neighbor_iso3
WHERE g.code = 'DE'
ORDER BY n.name;
```

If you accidentally join on `n.code` here, you’ll get empty or wrong results.

## 24. Population structs: filter on `population.year` when the year matters

```sql
SELECT code, name,
       population.value AS population,
       population.year AS population_year
FROM countries
WHERE population.year IS NOT NULL
ORDER BY population.value DESC
LIMIT 10;
```

## 25. Membership join gotcha: use `includes[].id` (country `code`), not `includes[].name`

Correct (join on authoritative country code):

```sql
SELECT i.id, i.name
FROM intblocks i,
     UNNEST(i.includes) AS t(m)
WHERE m.id = 'LA'
  AND m.type = 'country'
ORDER BY i.name
LIMIT 20;
```

Gotcha: `includes[].name` is a *label*. For countries the export copies the country's `name`, but joins still belong on the code.

```sql
-- Wrong: don't join on includes[].name
-- WHERE m.name = 'Laos'
```

## 26. Use `memberships` edges for simpler org&lt;-&gt;country queries

If you need membership edge fields (`status`, `joined`, `left`), prefer the flattened `memberships` table:

```sql
SELECT i.id, i.name, m.status, m.joined
FROM memberships m
JOIN intblocks i ON i.id = m.intblock_id
WHERE m.country_code = 'LA'
  AND m.status IN ('member', 'founding_member')
ORDER BY m.joined NULLS LAST
LIMIT 20;
```

## 27. Filter to current ISO countries (avoid special/non-standard codes)

```sql
SELECT code, name
FROM countries
WHERE code_status = 'official_iso3166_1'
ORDER BY code;
```

## 28. Resolve retired intblock IDs

Retired, merged, and renamed intblock IDs (for example `USAN` → `UNASUR`) stay in `intblocks_aliases.json`
(also `.parquet`). Resolve a stored ID before looking it up:

```sql
SELECT i.id, i.name
FROM intblocks i
WHERE i.id = coalesce(
  (SELECT target
   FROM read_json_auto('data/datasets/intblocks_aliases.json')
   WHERE alias = 'USAN'),
  'USAN'
);
```

## 29. Trade agreements of a country

Trade and investment agreements are in the trade agreements registry, not in `intblocks`:
`trade_agreements`, `trade_agreement_parties`, `trade_agreement_instruments` and the
`country_trade_agreements` view. Two-party FTAs (`CETA`, `USKR`, `EUJP`) are **only** there;
agreements with three or more parties that are signed or in force (`RCEP`, `CPTPP`) are also
intblocks, linked by `trade_agreements.intblock_id`. The view expands a bloc party such as the
EU to its current members (`via = 'EU'`).

DuckDB (agreements in force for Chile, without investment treaties, trade relations
agreements and preference schemes; `in_force` is empty while an agreement is only applied
provisionally, so take the earlier date):

```sql
SELECT c.agreement_id, t.name, c.agreement_type, c.via,
       coalesce(c.provisional_application, c.in_force) AS applies_since
FROM country_trade_agreements c
JOIN trade_agreements t ON t.id = c.agreement_id
WHERE c.country_code = 'CL'
  AND c.agreement_status = 'in_force'
  AND c.agreement_type NOT IN ('investment', 'trade_relations', 'preference_scheme')
ORDER BY c.agreement_id;
```

An id that left `intblocks` in 5.0.0 has an alias with `reason = 'moved'` and
`target_dataset = 'trade_agreements'`, under the same id:

```sql
SELECT a.alias, a.target_dataset, t.name, t.status, t.provisional_application
FROM intblocks_aliases a
JOIN trade_agreements t ON t.id = a.target
WHERE a.alias = 'CETA' AND a.reason = 'moved';
```

The registry has no trade values, tariff lines or depth scores. More recipes and the field
semantics (`verification`, preference scheme roles, instruments): [AI consumer guide](ai-consumers.md#trade-agreements-registry)
and [data contract](data-contract.md#canonical-views-and-reference-tables).
