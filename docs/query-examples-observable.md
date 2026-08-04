# Query examples (Observable / Observable Plot)

Visualization-oriented twin of the verified DuckDB recipes in
[query-examples.md](query-examples.md). Uses [Observable Framework](https://observablehq.com/framework/)
(or classic Observable notebooks) with **DuckDB-Wasm** for joins and
[Observable Plot](https://observablehq.com/plot/) for charts.

Polars twin: [query-examples-polars.md](query-examples-polars.md).
R / dplyr twin: [query-examples-r.md](query-examples-r.md).

This file is a **focused Plot cookbook**, not a line-for-line port of every SQL recipe.
Prefer tables (`Inputs.table`) for roster lookups; use Plot for rankings, distributions,
set sizes, timelines, and centroid maps.

For scope, join keys, and field semantics see [ai-consumers.md](ai-consumers.md).

## Setup

Ship or attach these build artifacts (do not parse source YAML):

| File | Role |
|------|------|
| `countries.parquet` | Filters, borders, centroids, World Bank structs |
| `memberships.parquet` | Org↔country edges (`intblock_id`, `country_code`, `status`, `joined`, `left`) |
| `intblocks.parquet` | Names, HQ, `blocktype`, lifecycle fields |
| `countries-lite.parquet` | Smaller map / entity-linking loads |

**Observable Framework** (`DuckDBClient` is built-in; Plot from npm):

```js
import * as Plot from "npm:@observablehq/plot";

const db = DuckDBClient.of({
  countries: FileAttachment("countries.parquet"),
  memberships: FileAttachment("memberships.parquet"),
  intblocks: FileAttachment("intblocks.parquet")
});
```

Alternatively attach the bundled database as a schema:

```js
const db = await DuckDBClient.of({
  internacia: FileAttachment("internacia.duckdb")
});
// then qualify tables: internacia.countries, internacia.memberships, …
```

Classic notebooks can use the same `DuckDBClient.of({…})` pattern after attaching the files.
Flat columns also load via `FileAttachment("….parquet").parquet()`, but nested structs
(`region`, `incomeLevel`, `centroid`, `borders`) are easier through DuckDB-Wasm SQL.

**Version check** (Parquet has no `_meta` table — use manifests):

```js
const meta = await FileAttachment("countries.manifest.json").json();
display(`${meta.dataset} ${meta.version} ${meta.schema_hash}`);
```

**Gotchas (same as SQL cookbook):**

- Join memberships on `country_code` ↔ `countries.code` (alpha-2).
- `borders` stores **alpha-3**; join neighbors on `iso3code`.
- Filter World Bank region on `region.id` (e.g. `'ECS'`), not the display `value`.
- Prefer `memberships` over exploding `intblocks.includes` in the browser.
- Org-density counts below use `memberships` (same surface as the Polars twin).

---

## Country filters (table + optional map)

### UN members only

```js
const un = await db.query(`
  SELECT code, name
  FROM countries
  WHERE un_member = true
  ORDER BY name
`);
```

**Expected:** 193 rows. Render with `Inputs.table(un)`.

### Left-hand traffic — centroid map

```js
const leftHand = await db.query(`
  SELECT code, name, centroid.lat AS lat, centroid.lng AS lng
  FROM countries
  WHERE car_side = 'left' AND centroid.lat IS NOT NULL
`);

Plot.plot({
  projection: "equirectangular",
  marks: [
    Plot.dot(leftHand, {x: "lng", y: "lat", r: 3, tip: true, title: (d) => `${d.code} ${d.name}`})
  ]
})
```

**Expected:** 74 dots.

### Landlocked countries — centroid map

```js
const landlocked = await db.query(`
  SELECT code, name, centroid.lat AS lat, centroid.lng AS lng
  FROM countries
  WHERE landlocked AND centroid.lat IS NOT NULL
`);

Plot.plot({
  projection: "equirectangular",
  marks: [
    Plot.dot(landlocked, {x: "lng", y: "lat", r: 3, fill: "currentColor", tip: true})
  ]
})
```

**Expected:** 48 dots (including non-ISO landlocked entities such as `XK`).

### Income level distribution (ISO countries)

```js
const byIncome = await db.query(`
  SELECT incomeLevel.id AS income_id,
         incomeLevel.value AS income,
         COUNT(*)::INTEGER AS n
  FROM countries
  WHERE code_status = 'official_iso3166_1'
    AND incomeLevel.id IS NOT NULL
  GROUP BY 1, 2
  ORDER BY n DESC
`);

Plot.plot({
  marginLeft: 140,
  x: {label: "Countries"},
  y: {label: null},
  marks: [
    Plot.barX(byIncome, {x: "n", y: "income", sort: {y: "-x"}, tip: true})
  ]
})
```

**Expected bars (ISO only):** High income: nonOECD 60, Lower middle 58, Upper middle 50,
Low income 41, High income: OECD 30, High income 5.

### World Bank region distribution (ISO countries)

```js
const byRegion = await db.query(`
  SELECT region.id AS region_id,
         region.value AS region,
         COUNT(*)::INTEGER AS n
  FROM countries
  WHERE code_status = 'official_iso3166_1'
    AND region.id IS NOT NULL
  GROUP BY 1, 2
  ORDER BY n DESC
`);

Plot.plot({
  marginLeft: 220,
  marks: [
    Plot.barX(byRegion, {x: "n", y: "region", sort: {y: "-x"}, tip: true})
  ]
})
```

**Gotcha:** Labels include upstream suffixes such as `(all income levels)`. Filter downstream
on `region_id` (`ECS`, `SSF`, …), not the label string.

---

## Geography and borders

### Countries with the most land borders

```js
const topBorders = await db.query(`
  SELECT code, name, len(borders)::INTEGER AS border_count
  FROM countries
  WHERE len(borders) > 0
  ORDER BY border_count DESC
  LIMIT 10
`);

Plot.plot({
  marginLeft: 100,
  marks: [
    Plot.barX(topBorders, {x: "border_count", y: "name", sort: {y: "-x"}, tip: true})
  ]
})
```

**Expected top:** `CN` (16), `RU` (14), `BR` (10).

### Neighbors of Thailand (table)

```js
const thNeighbors = await db.query(`
  SELECT n.code, n.name, n.iso3code
  FROM countries th,
       UNNEST(th.borders) AS b(neighbor_iso3)
  JOIN countries n ON n.iso3code = b.neighbor_iso3
  WHERE th.code = 'TH'
  ORDER BY n.name
`);
```

**Expected:** 4 rows — `KH`, `LA`, `MM`, `MY`.

---

## Membership rosters (tables)

### NATO / EU members

```js
const nato = await db.query(`
  SELECT country_code AS code, status, joined
  FROM memberships
  WHERE intblock_id = 'NATO' AND status = 'member'
  ORDER BY code
`);

const eu = await db.query(`
  SELECT country_code AS code, status
  FROM memberships
  WHERE intblock_id = 'EU'
  ORDER BY code
`);
```

**Expected:** NATO 32, EU 27.

### Organizations that include Laos

```js
const laosOrgs = await db.query(`
  SELECT m.intblock_id AS id, i.name, m.status, m.joined
  FROM memberships m
  JOIN intblocks i ON i.id = m.intblock_id
  WHERE m.country_code = 'LA'
  ORDER BY i.name
`);
```

**Expected:** 191 rows.

---

## Membership overlap (Plot)

### NATO ∩ EU and NATO outside EU

```js
const overlap = await db.query(`
  WITH nato AS (
    SELECT country_code AS code
    FROM memberships
    WHERE intblock_id = 'NATO'
      AND COALESCE(status, 'member') != 'former_member'
  ),
  eu AS (
    SELECT country_code AS code
    FROM memberships
    WHERE intblock_id = 'EU'
      AND COALESCE(status, 'member') != 'former_member'
  )
  SELECT 'NATO ∩ EU' AS set_name, COUNT(*)::INTEGER AS n
  FROM nato JOIN eu USING (code)
  UNION ALL
  SELECT 'NATO \\ EU', COUNT(*)::INTEGER
  FROM nato WHERE code NOT IN (SELECT code FROM eu)
  UNION ALL
  SELECT 'EU \\ NATO', COUNT(*)::INTEGER
  FROM eu WHERE code NOT IN (SELECT code FROM nato)
`);

Plot.plot({
  marginLeft: 90,
  marks: [Plot.barX(overlap, {x: "n", y: "set_name", tip: true})]
})
```

**Expected:** NATO ∩ EU = 23; NATO \\ EU = 9 (`AL`, `CA`, `GB`, `IS`, `ME`, `MK`, `NO`, `TR`, `US`).

List the intersection:

```js
const natoEu = await db.query(`
  SELECT n.country_code AS code
  FROM memberships n
  JOIN memberships e ON e.country_code = n.country_code
  WHERE n.intblock_id = 'NATO' AND e.intblock_id = 'EU'
    AND COALESCE(n.status, 'member') != 'former_member'
    AND COALESCE(e.status, 'member') != 'former_member'
  ORDER BY 1
`);
```

### Jaccard similarity (NATO vs EU)

```js
const [{jaccard}] = await db.query(`
  WITH a AS (
    SELECT country_code AS id FROM memberships WHERE intblock_id = 'NATO'
  ),
  b AS (
    SELECT country_code AS id FROM memberships WHERE intblock_id = 'EU'
  )
  SELECT ROUND(
    (SELECT COUNT(*) FROM (SELECT id FROM a INTERSECT SELECT id FROM b)) * 1.0
    / NULLIF((SELECT COUNT(*) FROM (SELECT id FROM a UNION SELECT id FROM b)), 0),
    2
  ) AS jaccard
`);
// → 0.64
```

---

## Organization density (Plot)

### Most / least organization-dense UN members

```js
const densest = await db.query(`
  SELECT c.code, c.name, COUNT(*)::INTEGER AS org_count
  FROM memberships m
  JOIN countries c ON c.code = m.country_code
  WHERE m.include_type = 'country' AND c.un_member
  GROUP BY c.code, c.name
  ORDER BY org_count DESC
  LIMIT 10
`);

const sparsest = await db.query(`
  SELECT c.code, c.name, COUNT(*)::INTEGER AS org_count
  FROM memberships m
  JOIN countries c ON c.code = m.country_code
  WHERE m.include_type = 'country' AND c.un_member
  GROUP BY c.code, c.name
  ORDER BY org_count ASC
  LIMIT 10
`);

Plot.plot({
  marginLeft: 100,
  title: "Most organization-dense UN members",
  marks: [
    Plot.barX(densest, {x: "org_count", y: "name", sort: {y: "-x"}, tip: true})
  ]
})
```

**Expected top (memberships):** `FR` (~394), `GB` (~379), `DE` (~372).
**Expected bottom:** `KP` (~110), `FM` (~115), `PW` (~121).

Absolute counts drift as rosters are enriched; relative ranking is the useful signal.

### Org density on a centroid map

```js
const densityMap = await db.query(`
  SELECT c.code, c.name,
         c.centroid.lat AS lat, c.centroid.lng AS lng,
         COUNT(*)::INTEGER AS org_count
  FROM memberships m
  JOIN countries c ON c.code = m.country_code
  WHERE m.include_type = 'country'
    AND c.un_member
    AND c.centroid.lat IS NOT NULL
  GROUP BY 1, 2, 3, 4
`);

Plot.plot({
  projection: "equirectangular",
  r: {range: [1, 12]},
  marks: [
    Plot.dot(densityMap, {
      x: "lng",
      y: "lat",
      r: "org_count",
      fillOpacity: 0.5,
      tip: true,
      title: (d) => `${d.code}: ${d.org_count} orgs`
    })
  ]
})
```

### Countries with many observer seats

```js
const observers = await db.query(`
  SELECT c.code, c.name, COUNT(*)::INTEGER AS observer_count
  FROM memberships m
  JOIN countries c ON c.code = m.country_code
  WHERE m.status = 'observer' AND m.include_type = 'country'
  GROUP BY c.code, c.name
  HAVING observer_count >= 5
  ORDER BY observer_count DESC, c.name
`);

Plot.plot({
  marginLeft: 100,
  marks: [
    Plot.barX(observers, {x: "observer_count", y: "name", sort: {y: "-x"}, tip: true})
  ]
})
```

**Expected:** 13 rows — `HU`, `IN`, `MD`, `TH`, `UA` each with 6.

---

## Near-universal coverage without China / US (Plot)

Intblocks covering more than half of UN members (`un_member = true`, 193) but missing
China, the US, or both. Active country participants only (`former_member` excluded):

```js
const nearUniversal = await db.query(`
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
      COUNT(DISTINCT m.country_code) FILTER (
        WHERE m.country_code IN (SELECT code FROM un)
          AND COALESCE(m.status, 'member') != 'former_member'
      ) AS un_members_in_roster,
      bool_or(m.country_code = 'CN' AND COALESCE(m.status, 'member') != 'former_member') AS has_china,
      bool_or(m.country_code = 'US' AND COALESCE(m.status, 'member') != 'former_member') AS has_usa
    FROM memberships m
    JOIN intblocks i ON i.id = m.intblock_id
    WHERE m.include_type = 'country'
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
  ORDER BY pct_un_members DESC, b.name
`);

Plot.plot({
  color: {legend: true, label: "Absent"},
  x: {label: "% of UN members in roster"},
  y: {axis: null},
  marks: [
    Plot.dot(nearUniversal, {
      x: "pct_un_members",
      y: "id",
      fill: "absent",
      tip: true,
      title: (d) => `${d.id}: ${d.name}`
    })
  ]
})
```

**Expected:** on the order of ~29 rows (counts move with enrichment). Inspect `blocktype` /
`status` before treating informal groupings as formal organizations.

---

## Headquarters and lifecycle (Plot)

### Formal organizations in Geneva, New York, and Vienna

```js
const hqCities = await db.query(`
  SELECT headquarters.city AS city,
         headquarters.country AS country,
         COUNT(*)::INTEGER AS org_count
  FROM intblocks
  WHERE status = 'formal'
    AND headquarters.city IN ('Geneva', 'New York', 'Vienna')
  GROUP BY 1, 2
  ORDER BY org_count DESC
`);

Plot.plot({
  marks: [
    Plot.barY(hqCities, {x: "city", y: "org_count", tip: true})
  ]
})
```

**Expected:** Geneva/CH 39, New York/US 19, Vienna/AT 16.

### Former members with departure dates (timeline)

```js
const departed = await db.query(`
  SELECT intblock_id,
         country_code,
         joined,
         "left" AS departed
  FROM memberships
  WHERE status = 'former_member'
    AND "left" IS NOT NULL
  ORDER BY "left" DESC
  LIMIT 40
`);

// Plot needs comparable dates — coerce year-month strings where possible
const timeline = departed.map((d) => ({
  ...d,
  t: new Date(String(d.departed).length === 7 ? `${d.departed}-01` : d.departed)
})).filter((d) => !Number.isNaN(+d.t));

Plot.plot({
  x: {label: "Departure"},
  marks: [
    Plot.ruleX(timeline, {x: "t", strokeOpacity: 0.3}),
    Plot.dot(timeline, {
      x: "t",
      y: "intblock_id",
      tip: true,
      title: (d) => `${d.country_code} left ${d.intblock_id} (${d.departed})`
    })
  ]
})
```

**Gotcha:** Quote `"left"` in SQL — it is a reserved word. Precision varies (`YYYY`,
`YYYY-MM`, `YYYY-MM-DD`).

### Predecessor / successor chains (table)

```js
const succession = await db.query(`
  SELECT id, name, predecessor, successor, dissolved
  FROM intblocks
  WHERE predecessor IS NOT NULL OR successor IS NOT NULL
  ORDER BY id
`);
```

**Expected:** 24 rows — e.g. `BRIC` → `BRICS`, `GATT` → `WTO`, `NAFTA` → `USMCA`.

---

## Suggested notebook outline

A compact Observable Framework page can wire the recipes above as sections:

1. Load `DuckDBClient` + version manifests  
2. Income / region bars  
3. Top land borders bar  
4. Org-density bars + centroid bubble map  
5. NATO/EU overlap bars + intersection table  
6. Near-universal coverage dots (color by absent CN/US)  
7. HQ city bars + former-member timeline  

Keep roster dumps behind `Inputs.table` / `Inputs.search` so the first viewport stays visual.

---

## Other access paths

- **DuckDB SQL:** [query-examples.md](query-examples.md) — `data/datasets/internacia.duckdb`
- **Polars:** [query-examples-polars.md](query-examples-polars.md) — same Parquet exports
- **R / dplyr:** [query-examples-r.md](query-examples-r.md) — same Parquet exports
- **[internacia-python](https://github.com/datenoio/internacia-python)** — typed lookups without frame code
- **[internacia-api](https://github.com/datenoio/internacia-api)** — HTTP access without local files

## Related documentation

- [ai-consumers.md](ai-consumers.md) — consumption contract and common mistakes
- [query-examples.md](query-examples.md) — verified DuckDB recipes (source of truth for counts)
- [country-code-policy.md](country-code-policy.md) — entity status and code filtering
- [intblock-inclusion-policy.md](intblock-inclusion-policy.md) — `scope_category` taxonomy
- [getting-started.md](getting-started.md) — non-programmer path
- [llms.txt](../llms.txt) — compact index for LLM context windows
