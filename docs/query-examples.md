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

**Expected:** 193 rows.

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

**Expected:** 1 row (`VA` Vatican City).

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

**Expected:** 193 vs 193 — both surfaces should agree; if they diverge, pick one and
document your choice.

### Near-universal UN coverage without China, the US, or both

Find intblocks whose roster includes **more than half** of UN member states (`un_member =
true`, 193 countries) but omits at least one of the two largest non-members: China (`CN`)
or the United States (`US`).

Count active country participants only — exclude `former_member` from the roster tally:

```sql
WITH un AS (
  SELECT code FROM countries WHERE un_member = true
),
un_count AS (
  SELECT COUNT(*)::DOUBLE AS n FROM un
),
block_rosters AS (
  SELECT
    i.id,
    i.name,
    COUNT(DISTINCT m.id) FILTER (
      WHERE m.id IN (SELECT code FROM un)
        AND COALESCE(m.status, 'member') != 'former_member'
    ) AS un_members_in_roster,
    bool_or(m.id = 'CN' AND COALESCE(m.status, 'member') != 'former_member') AS has_china,
    bool_or(m.id = 'US' AND COALESCE(m.status, 'member') != 'former_member') AS has_usa
  FROM intblocks i, UNNEST(i.includes) AS t(m)
  WHERE m.type = 'country'
  GROUP BY i.id, i.name
)
SELECT
  b.id,
  b.name,
  b.un_members_in_roster,
  ROUND(100.0 * b.un_members_in_roster / u.n, 1) AS pct_un_members,
  CASE
    WHEN NOT b.has_china AND NOT b.has_usa THEN 'CN and US'
    WHEN NOT b.has_china THEN 'CN'
    WHEN NOT b.has_usa THEN 'US'
  END AS absent
FROM block_rosters b
CROSS JOIN un_count u
WHERE b.un_members_in_roster > u.n * 0.5
  AND (NOT b.has_china OR NOT b.has_usa)
ORDER BY pct_un_members DESC, b.name;
```

**Expected:** 28 rows — 18 missing the US only (e.g. `CBD`, `UNCLOS`), 2 missing China
only (`EGMONTGROUP`, `IAU_UNIV`), 8 missing both (`NAM`, `ICW`, `APMINEBANCONVENTION`).

Filter to a single exclusion pattern:

```sql
-- Missing China only (includes the US)
...
WHERE b.un_members_in_roster > u.n * 0.5
  AND NOT b.has_china
  AND b.has_usa;

-- Missing the US only (includes China)
...
WHERE b.un_members_in_roster > u.n * 0.5
  AND b.has_china
  AND NOT b.has_usa;

-- Missing both China and the US
...
WHERE b.un_members_in_roster > u.n * 0.5
  AND NOT b.has_china
  AND NOT b.has_usa;
```

**Expected:** 2, 18, and 8 rows respectively.

**Gotcha:** Use `countries.un_member` as the denominator, not the `UN` intblock roster
(193 entries). Some high-coverage records are informal groupings (`LMY`, `PERIPHCOUNT`) —
inspect `blocktype` and `status` before treating them as formal organizations.

### Organizations a country belongs to

```sql
SELECT i.id, i.name, i.blocktype
FROM intblocks i, UNNEST(i.includes) AS t(m)
WHERE m.id = 'FR' AND m.type = 'country'
ORDER BY i.name;
```

### Russia: former memberships only

List intblocks where the Russian Federation (`RU`) appears with `former_member` status and
is **not** an active member of the same organization:

```sql
SELECT i.id, i.name, m.status, m.joined, m.note
FROM intblocks i, UNNEST(i.includes) AS t(m)
WHERE m.id = 'RU'
  AND m.type = 'country'
  AND m.status = 'former_member'
ORDER BY m.joined NULLS LAST, i.name;
```

**Expected:** 11 rows (`BEACST`, `DANUBECOM`, `EASTERNBLOC`, `ECHR`, `EUA`, `GRECO`, `ICES`,
`JCPOA`, `NSS`, `OPENSKY`, `RAMSAR`).

**Gotcha:** `internacia.duckdb` and Parquet omit `includes[].left` (departure date). Use
`intblocks.jsonl.zst` when you need temporal filters on when membership ended.

### Russia: departed around March 2022

Organizations where Russia was a member until March 2022 and is now recorded only as
`former_member`. Read from compressed JSONL — DuckDB decompresses `.zst` automatically:

```sql
SELECT
  i.id,
  i.name AS organization,
  json_extract_string(m, '$.status') AS status,
  json_extract_string(m, '$.joined') AS joined,
  json_extract_string(m, '$.left') AS departed,
  json_extract_string(m, '$.note') AS note
FROM read_json('data/datasets/intblocks.jsonl.zst', format='newline_delimited') i,
     UNNEST(CAST(i.includes AS JSON[])) AS t(m)
WHERE json_extract_string(m, '$.id') = 'RU'
  AND json_extract_string(m, '$.type') = 'country'
  AND json_extract_string(m, '$.status') = 'former_member'
  AND (
    json_extract_string(m, '$.left') LIKE '2022-03%'
    OR json_extract_string(m, '$.note') ILIKE '%March 2022%'
  )
ORDER BY departed, organization;
```

**Expected:** 3 rows:

| id | organization | departed | note |
|----|-------------|----------|------|
| `EUA` | European University Association | `2022-03` | — |
| `ECHR` | European Court of Human Rights | `2022-03-16` | — |
| `ICES` | International Council for the Exploration of the Sea | `2025-12-09` | Suspended 30 March 2022; formal withdrawal later |

**Gotcha:** Coverage is source-dependent — e.g. `COE` (Council of Europe) may still list
Russia as `member` while child bodies like `ECHR` already mark `former_member`. Filter on
`former_member` explicitly; do not infer departures from absence in active rosters.

Equivalent Python (JSONL.zst, no source YAML):

```python
import json
import zstandard

path = "data/datasets/intblocks.jsonl.zst"
with zstandard.ZstdDecompressor().stream_reader(open(path, "rb")) as reader:
    lines = reader.read().decode().splitlines()

rows = []
for line in lines:
    block = json.loads(line)
    for m in block.get("includes") or []:
        if m.get("id") != "RU" or m.get("type") != "country":
            continue
        if m.get("status") != "former_member":
            continue
        left = m.get("left") or ""
        note = m.get("note") or ""
        if left.startswith("2022-03") or "March 2022" in note:
            rows.append(
                {
                    "id": block["id"],
                    "organization": block["name"],
                    "joined": m.get("joined"),
                    "departed": left or None,
                    "note": note or None,
                }
            )

assert len(rows) == 3
assert {r["id"] for r in rows} == {"ECHR", "EUA", "ICES"}
```

## Membership overlap and set logic

### NATO members outside the EU

```sql
SELECT c.code, c.name
FROM countries c
WHERE c.code IN (
    SELECT m.id
    FROM intblocks i, UNNEST(i.includes) AS t(m)
    WHERE i.id = 'NATO' AND m.type = 'country'
  )
  AND c.code NOT IN (
    SELECT m.id
    FROM intblocks i, UNNEST(i.includes) AS t(m)
    WHERE i.id = 'EU' AND m.type = 'country'
  )
ORDER BY c.name;
```

**Expected:** 9 rows — `AL`, `CA`, `GB`, `IS`, `ME`, `MK`, `NO`, `TR`, `US`.

### EU members outside the eurozone

Eurozone membership is tracked via the `EMU` intblock:

```sql
SELECT c.code, c.name
FROM countries c
WHERE c.code IN (
    SELECT m.id
    FROM intblocks i, UNNEST(i.includes) AS t(m)
    WHERE i.id = 'EU' AND m.type = 'country'
  )
  AND c.code NOT IN (
    SELECT m.id
    FROM intblocks i, UNNEST(i.includes) AS t(m)
    WHERE i.id = 'EMU' AND m.type = 'country'
  )
ORDER BY c.name;
```

**Expected:** 7 rows — `BG`, `CZ`, `DK`, `HU`, `PL`, `RO`, `SE`.

### Jaccard similarity between organization rosters

Measure overlap as |A ∩ B| / |A ∪ B|. Swap `NATO` / `EU` for any pair:

```sql
WITH a AS (
  SELECT m.id
  FROM intblocks i, UNNEST(i.includes) AS t(m)
  WHERE i.id = 'NATO' AND m.type = 'country'
),
b AS (
  SELECT m.id
  FROM intblocks i, UNNEST(i.includes) AS t(m)
  WHERE i.id = 'EU' AND m.type = 'country'
)
SELECT ROUND(
  (SELECT COUNT(*) FROM (SELECT id FROM a INTERSECT SELECT id FROM b)) * 1.0
  / NULLIF((SELECT COUNT(*) FROM (SELECT id FROM a UNION SELECT id FROM b)), 0),
  2
) AS jaccard;
```

**Expected:** `0.64` (23 countries in both, 36 total distinct).

### Full member in one bloc, observer in another

EU members with only **observer** status in BSEC (Black Sea Economic Cooperation):

```sql
SELECT c.code, c.name
FROM countries c
WHERE c.code IN (
    SELECT m.id
    FROM intblocks i, UNNEST(i.includes) AS t(m)
    WHERE i.id = 'EU' AND m.type = 'country'
  )
  AND c.code IN (
    SELECT m.id
    FROM intblocks i, UNNEST(i.includes) AS t(m)
    WHERE i.id = 'BSEC' AND m.type = 'country' AND m.status = 'observer'
  )
ORDER BY c.name;
```

**Expected:** 9 rows — includes `DE`, `FR`, `IT`, `PL`.

**Gotcha:** Filter on `includes[].status`; the same country can appear in both blocs with
different participation levels.

## Organization density and status

### Most organization-dense UN members

```sql
SELECT c.code, c.name, COUNT(DISTINCT i.id) AS org_count
FROM countries c
JOIN intblocks i ON TRUE
JOIN UNNEST(i.includes) AS t(m) ON m.id = c.code AND m.type = 'country'
WHERE c.un_member
GROUP BY c.code, c.name
ORDER BY org_count DESC
LIMIT 10;
```

**Expected top:** `FR` (397), `GB` (384), `DE` (374), `IT` (363), `US` (360).

### Least organization-dense UN members

```sql
SELECT c.code, c.name, COUNT(DISTINCT i.id) AS org_count
FROM countries c
JOIN intblocks i ON TRUE
JOIN UNNEST(i.includes) AS t(m) ON m.id = c.code AND m.type = 'country'
WHERE c.un_member
GROUP BY c.code, c.name
ORDER BY org_count ASC
LIMIT 10;
```

**Expected bottom:** `KP` (117), `FM` (118), `PW` (124), `MH` (125), `LI` (128).

### Heavily connected countries missing from a bloc

UN members in 100+ intblocks but **not** in the OECD:

```sql
SELECT c.code, c.name, d.org_count
FROM (
  SELECT m.id AS code, COUNT(DISTINCT i.id) AS org_count
  FROM intblocks i, UNNEST(i.includes) AS t(m)
  WHERE m.type = 'country'
  GROUP BY m.id
  HAVING org_count >= 100
) d
JOIN countries c ON c.code = d.code
WHERE c.un_member
  AND c.code NOT IN (
    SELECT m.id
    FROM intblocks i, UNNEST(i.includes) AS t(m)
    WHERE i.id = 'OECD' AND m.type = 'country'
  )
ORDER BY d.org_count DESC;
```

**Expected:** 155 rows — includes `CN`, `IN`, `RU` near the top; `KP` at the bottom.

### Countries with many observer seats

```sql
SELECT c.code, c.name, COUNT(*) AS observer_count
FROM countries c
JOIN intblocks i ON TRUE
JOIN UNNEST(i.includes) AS t(m) ON m.id = c.code AND m.type = 'country'
WHERE m.status = 'observer'
GROUP BY c.code, c.name
HAVING observer_count >= 5
ORDER BY observer_count DESC, c.name;
```

**Expected:** 13 rows — `HU`, `IN`, `MD`, `TH`, `UA` each with 6 observer entries.

## Geography and membership

### Landlocked UN members in no trade bloc

```sql
SELECT c.code, c.name
FROM countries c
WHERE c.landlocked
  AND c.un_member
  AND c.code NOT IN (
    SELECT m.id
    FROM intblocks i, UNNEST(i.includes) AS t(m)
    WHERE list_contains(i.blocktype, 'trade')
      AND m.type = 'country'
      AND COALESCE(m.status, 'member') != 'former_member'
  )
ORDER BY c.name;
```

**Expected:** 5 rows — `AD`, `BT`, `SM`, `TM`, `UZ`.

### Landlocked enclaves (single land neighbor)

```sql
SELECT c.code, c.name, len(c.borders) AS neighbor_count
FROM countries c
WHERE c.landlocked AND len(c.borders) = 1
ORDER BY c.name;
```

**Expected:** 3 rows — `LS` Lesotho, `SM` San Marino, `VA` Vatican City.

### Border-income homogeneity

Countries whose **every** land neighbor shares the same World Bank income level:

```sql
SELECT c.code, c.name, c.incomeLevel.value AS income, len(c.borders) AS border_count
FROM countries c
WHERE c.incomeLevel.value IS NOT NULL
  AND len(c.borders) >= 2
  AND NOT EXISTS (
    SELECT 1
    FROM UNNEST(c.borders) AS b(iso3)
    JOIN countries n ON n.iso3code = b.iso3
    WHERE n.incomeLevel.value IS DISTINCT FROM c.incomeLevel.value
  )
ORDER BY border_count DESC, c.name;
```

**Expected:** 20 rows — includes `DE` (9 borders, all high-income OECD), `TZ` (8 borders,
all low income).

**Gotcha:** Join borders on `iso3code`, not alpha-2. ~33 entities lack `incomeLevel`.

### Countries whose neighbors are all EU members

Every land neighbor must be in the `EU` intblock roster:

```sql
SELECT c.code, c.name
FROM countries c
WHERE len(c.borders) > 0
  AND NOT EXISTS (
    SELECT 1
    FROM UNNEST(c.borders) AS b(iso3)
    JOIN countries n ON n.iso3code = b.iso3
    WHERE n.code NOT IN (
      SELECT m.id
      FROM intblocks i, UNNEST(i.includes) AS t(m)
      WHERE i.id = 'EU' AND m.type = 'country'
    )
  )
ORDER BY c.name;
```

**Expected:** 13 rows — includes `BE`, `CZ`, `LU`, `VA`. Excludes `DE` (borders Switzerland,
which is not in the EU roster).

## Organization lifecycle and hierarchy

### Predecessor and successor chains

```sql
SELECT id, name, predecessor, successor, dissolved
FROM intblocks
WHERE predecessor IS NOT NULL OR successor IS NOT NULL
ORDER BY id;
```

**Expected:** 24 rows — includes `BRIC` → `BRICS`, `G7` ↔ `G8`, `GATT` → `WTO`, `NAFTA`
→ `USMCA`.

### Dissolved organizations that still carry rosters

```sql
SELECT id, name, dissolved, len(includes) AS roster_size
FROM intblocks
WHERE dissolved IS NOT NULL AND len(includes) > 0
ORDER BY dissolved, name;
```

**Expected:** 33 rows — includes `WARSAWPACT`, `SEATO`, `G8`, `WESTERNBLOC`.

### UN agency hierarchy (two-level `partof`)

Grandchild agencies under `UN` via an intermediate parent (e.g. `UNESCO`, `UNDP`):

```sql
SELECT child.id, child.name, parent.id AS parent_id, grand.id AS root_id
FROM intblocks child
JOIN intblocks parent ON list_contains(child.partof, parent.id)
JOIN intblocks grand ON list_contains(parent.partof, grand.id)
WHERE grand.id = 'UN'
ORDER BY child.id;
```

**Expected:** 25 rows — includes `IIEP` (UNESCO → UN), `UNCDF` (UNDP → UN).

### Former members with join and departure dates

Requires `includes[].left` from JSONL export:

```sql
SELECT
  i.id,
  i.name AS organization,
  json_extract_string(m, '$.id') AS country_code,
  json_extract_string(m, '$.joined') AS joined,
  json_extract_string(m, '$.left') AS departed
FROM read_json('data/datasets/intblocks.jsonl.zst', format='newline_delimited') i,
     UNNEST(CAST(i.includes AS JSON[])) AS t(m)
WHERE json_extract_string(m, '$.status') = 'former_member'
  AND json_extract_string(m, '$.joined') IS NOT NULL
ORDER BY i.id, country_code;
```

**Expected:** 199 rows — e.g. `CISSTAT` / `UA` (joined 1991, left 2014), `WESTERNBLOC` /
`US` (joined 1947, left 1991).

## Edge cases and data quality

### Disputed territories in organizations

```sql
SELECT c.code, c.name, COUNT(DISTINCT i.id) AS org_count
FROM countries c
JOIN intblocks i ON TRUE
JOIN UNNEST(i.includes) AS t(m) ON m.id = c.code AND m.type = 'country'
WHERE c.entity_type = 'disputed_territory'
GROUP BY c.code, c.name
ORDER BY org_count DESC;
```

**Expected:** 5 rows — `KV` Kosovo (49), `EH` Western Sahara (12); `XA`, `XS`, `XT` with
fewer affiliations.

### Independent but not UN members — org counts

Extends the country filter with membership tallies:

```sql
SELECT c.code, c.name, COUNT(DISTINCT i.id) AS org_count
FROM countries c
JOIN intblocks i ON TRUE
JOIN UNNEST(i.includes) AS t(m) ON m.id = c.code AND m.type = 'country'
WHERE c.independent = true AND c.un_member = false
GROUP BY c.code, c.name
ORDER BY c.code;
```

**Expected:** 1 row — `VA` Vatican City (40 org affiliations).

### Declared vs actual roster size

Where `membership_count` differs from `len(includes)`:

```sql
SELECT
  id,
  name,
  membership_count,
  len(includes) AS actual_count,
  membership_count - len(includes) AS delta
FROM intblocks
WHERE membership_count IS NOT NULL
  AND len(includes) > 0
  AND membership_count != len(includes)
ORDER BY ABS(membership_count - len(includes)) DESC, id
LIMIT 20;
```

**Expected:** 200 mismatches total; largest positive deltas are non-country memberships
counted in `membership_count` (e.g. `IGA`, `WNA`).

### Include label vs canonical country name

`includes[].name` is a display label — compare against `countries.name` and
`common_names`:

```sql
SELECT
  i.id AS intblock_id,
  m.id AS country_code,
  m.name AS include_label,
  c.name AS canonical_name
FROM intblocks i, UNNEST(i.includes) AS t(m)
JOIN countries c ON c.code = m.id
WHERE m.type = 'country'
  AND m.name IS NOT NULL
  AND m.name != c.name
  AND NOT list_contains(c.common_names, m.name)
ORDER BY i.id, m.id
LIMIT 20;
```

**Expected:** 1826 mismatches total (advisory); examples include `CD` labeled
"Congo, The Democratic Republic of the" vs canonical "Congo, Dem. Rep.".

**Gotcha:** Mismatches are **not errors** — always join on `includes[].id`, never on
`includes[].name`.

## Taxonomy and discovery

### Intblocks with the most blocktypes

```sql
SELECT id, name, len(blocktype) AS type_count, blocktype
FROM intblocks
ORDER BY type_count DESC, id
LIMIT 10;
```

**Expected top:** `PICES` (5 types: `climate`, `intorg`, `environment`, `research`,
`ocean`).

### Formal organizations in Geneva, New York, and Vienna

```sql
SELECT headquarters.city, headquarters.country, COUNT(*) AS org_count
FROM intblocks
WHERE status = 'formal'
  AND headquarters.city IN ('Geneva', 'New York', 'Vienna')
GROUP BY headquarters.city, headquarters.country
ORDER BY org_count DESC;
```

**Expected:** Geneva/CH (39), New York/US (18), Vienna/AT (16).

### Organizations by topic

```sql
SELECT DISTINCT i.id, i.name
FROM intblocks i, UNNEST(i.topics) AS t(topic)
WHERE topic.key = 'human_rights'
ORDER BY i.name;
```

**Expected:** 15 rows — includes `UNHRC`, `UNWOMEN`, `CDEM`.

Swap `topic.key` for other taxonomy keys (`nuclear`, `trade`, `ocean`, etc.).

### Wikidata-linked UN members with sparse membership

Useful for entity-linking pipelines flagging under-connected profiles:

```sql
SELECT c.code, c.name, c.wikidata_id, COUNT(DISTINCT i.id) AS org_count
FROM countries c
JOIN intblocks i ON TRUE
JOIN UNNEST(i.includes) AS t(m) ON m.id = c.code AND m.type = 'country'
WHERE c.wikidata_id IS NOT NULL AND c.un_member
GROUP BY c.code, c.name, c.wikidata_id
HAVING org_count <= 130
ORDER BY org_count ASC, c.name;
```

**Expected:** 6 rows — `KP`, `FM`, `PW`, `MH`, `LI`, `NR` (117–129 org affiliations).

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
