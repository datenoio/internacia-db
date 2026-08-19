# LLM-friendly scenarios (copy/paste)

These examples are written for code-generating agents:

- Prefer the **Python SDK** (`pip install internacia`) when it covers the task.
- Fall back to **DuckDB** when you need a multi-join or when you want membership/border details.
- Remember join keys:
  - Intblock membership joins use `includes[].id` (country `code`) / `memberships.country_code`.
  - `countries.borders` contains **ISO alpha-3** neighbor codes; join on `countries.iso3code`.

## 1. Country lookup by ISO alpha-2

```python
from internacia import InternaciaClient

client = InternaciaClient()
country = client.countries.get_by_code("US")
print(country["name"])
```

## 2. Country lookup by ISO numeric code

```python
from internacia import InternaciaClient

client = InternaciaClient()
country = client.countries.get_by_numeric_code("840")  # United States
print(country["code"], country["name"])
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

Python SDK (returns matching blocks; membership status fields may not be included):

```python
from internacia import InternaciaClient

client = InternaciaClient()
blocks = client.intblocks.get_by_member("US")
for b in blocks[:5]:
    print(b["id"], b["name"])
```

DuckDB (includes membership edge metadata):

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

## 7. Blocks by acronym (e.g., EU)

```python
from internacia import InternaciaClient

client = InternaciaClient()
eu_blocks = client.intblocks.get_by_acronym("EU")
for b in eu_blocks[:5]:
    print(b["id"], b["name"])
```

## 8. Blocks by tag (e.g., trade)

```python
from internacia import InternaciaClient

client = InternaciaClient()
blocks = client.intblocks.get_by_tag("trade")
for b in blocks[:5]:
    print(b["id"], b["name"])
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

## 11. Blocks by blocktype (e.g., trade / intorg)

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

## 12. Blocks by `scope_category` (igo / treaty_body / policy_forum / reference_enumeration)

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

aliases = json.load(open("data/datasets/countries_aliases.json"))

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
SELECT id, name
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

Gotcha: `includes[].name` is a *label* and may not match the canonical country name.

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

