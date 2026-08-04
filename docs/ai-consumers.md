# AI consumer guide

This document is the **consumption contract** for Internacia Datasets — written for
LLM agents, enrichment pipelines, and programmatic integrators. For installation and
build instructions, see [README.md](../README.md).

## Scope

### In scope

Reference data used for entity linking, geographic classification, and organizational
membership joins:

- ISO 3166-1 identifiers and entity status metadata
- Geography (borders, continents, subregions, coordinates, centroids where present)
- Demographic reference fields (`population`, `area`, `gini`) with source/year
- World Bank-style classifications (`region`, `incomeLevel`, `lendingType`)
- Cultural reference (`languages`, `currencies`, `timezones`, `demonyms`, `flag_emoji`)
- Multilingual names and aliases (`other_names`, `common_names`, `native_names`)
- Wikidata entity links (`wikidata_id`)
- Intergovernmental organizations with membership rosters and taxonomy
- Field-level provenance on country records where enriched

### Out of scope

Do **not** infer or expect these fields — they are intentionally absent:

- HDI, GDP, GDP per capita, government type, internet penetration
- Time-series economic or governance indicators
- Real-time membership or political recognition status

Downstream consumers should enrich from separate datasets. See
[openspec/AGENTS.md](../openspec/AGENTS.md) (Dataset Scope).

## Datasets

| Dataset | Records | Primary key | Manifest |
|---------|--------:|-------------|----------|
| `countries` | 256 | `code` (alpha-2) | `data/datasets/countries.manifest.json` |
| `intblocks` | 1037 | `id` | `data/datasets/intblocks.manifest.json` |
| `blocktypes` | 78 | `id` | `data/datasets/blocktypes.manifest.json` |

All three are bundled in `data/datasets/internacia.duckdb`. Prefer DuckDB or Parquet
over reading individual YAML source files under `data/countries/` and `data/intblocks/`.

**Consistency guarantee.** CI (`scripts/check_generated_artifacts.py`) enforces that
every export format (JSONL, YAML, Parquet, DuckDB) exposes the same primary-key set
and row count per dataset, that these match the YAML source, and that all manifests,
`*.meta.json` sidecars, and the DuckDB `_meta` table share one build identity
(`version`, `git_commit`, `build_date`). You can rely on any format being complete
and interchangeable.

### Tabular and lite exports

For spreadsheet tools and context-constrained agents, each build also publishes:

| Artifact | Use |
|----------|-----|
| `countries.csv.zst` / `intblocks.csv.zst` | Flattened scalar columns (structs expanded to `population_value`, `hq_city`, etc.); decompress with `zstd -d` |
| `countries-lite.parquet` | ~12 columns: `code`, `name`, `iso3code`, `wikidata_id`, `entity_type`, `code_status`, `un_status`, `independent`, `region_id`, `subregion`, `ioc_code`, `fifa_code` |
| `intblocks-lite.parquet` | ~9 columns: `id`, `name`, `status`, `wikidata_id`, `geographic_scope`, `scope_category`, `blocktype`, `membership_count`, `legal_status` |
| `countries.json.zst` / `intblocks.json.zst` | Single JSON arrays (same records as JSONL), zstd-compressed |
| `datapackage.json` | Frictionless Data Package resource index |

Lite variants share primary keys with full exports — join on `code` or `id` to hydrate heavy fields.

## Versioning and stability

Every build writes a manifest with:

- `version` — semver (matches git tag on releases)
- `schema_hash` — changes on breaking schema migrations
- `build_date`, `git_commit`, `row_count`, `data_license`

Query version from DuckDB:

```sql
SELECT dataset, version, schema_hash, build_date FROM _meta;
```

Before upgrading:

1. Compare `schema_hash` in your cached manifest vs the new release
2. Read [CHANGELOG.md](../CHANGELOG.md) for migration notes
3. Apply intblock alias remaps from `intblocks_aliases.json` if joining on intblock `id`
4. Apply country code remaps from `countries_aliases.json` if joining on country `code` (e.g. legacy `KV` → `XK`)

**Stable join keys:** country `code` and intblock `id`. When an intblock id is renamed,
the old id appears in `intblocks_aliases.json`:

```python
import json

aliases = {
    a["alias"]: a["target"]
    for a in json.load(open("data/datasets/intblocks_aliases.json"))
}
resolved = aliases.get("ASF", "ASF")  # -> "FSA"
```

A `reason` of `disambiguated` means the alias string now refers to a **different**
entity (not just a rename).

## Entity model

### Countries

256 country and territory records including 249 current ISO 3166-1 assignments plus
7 non-standard entries with explicit `code_status`. See
[country-code-policy.md](country-code-policy.md).

Key classification fields:

| Field | Use |
|-------|-----|
| `code_status` | `official_iso3166_1`, `user_assigned`, `obsolete`, `exceptionally_reserved` |
| `entity_type` | `sovereign_state`, `dependent_territory`, `disputed_territory`, etc. |
| `un_member`, `independent` | Boolean flags |
| `recognition_status` | Optional struct for dispute/recognition metadata |

**Filter current ISO countries (249 records):**

```python
df[df["code_status"] == "official_iso3166_1"]
```

### Intblocks

Organizations, treaties, alliances, federations, and similar groupings. Each record has:

- `id` — stable uppercase identifier (join key)
- `blocktype` — list of taxonomy keys (e.g. `intorg`, `trade`, `military`)
- `includes` — membership list; **`includes[].id` is authoritative** for joins
- `status`, `founded`, `dissolved`, `predecessor`, `successor` — lifecycle
- `wikidata_id`, `description`, `tags`, `topics` — linking and discovery
- `partof` — parent organization ids

Member entry shape: `{id, name, type, status, joined, role, note}`.
Use `id` for joins; `name` is a source label and may not match the canonical country name.

### Membership status (`includes[].status`)

Canonical catalog: [`data/schemas/includes_status.yaml`](../data/schemas/includes_status.yaml).

| Status | Meaning |
|--------|---------|
| `member` / `founding_member` | Current (or founding) full member |
| `observer` / `associated_observer` | Observer seat |
| `associate` / `associate_member` / `associated` | Associate-tier participation |
| `former_member` | Left; prefer `left` date when known |
| `participant` / `partner` / `cooperating` | Non-member participation |
| `recipient` / `contributor` / `funder` | Program / funding roles |
| `represented` / `validation` / `extension` | Special coverage statuses |

Filter current members with `status NOT IN ('former_member')` (and usually exclude
observers unless the question asks for them).

### Intblock `scope_category`

Optional inclusion taxonomy (`igo`, `treaty_body`, `policy_forum`, `reference_enumeration`).
`reference_enumeration` covers named geographic/set groupings (e.g. SIDS), **not** country
attribute partitions (those live on countries — see below).
See [intblock-inclusion-policy.md](intblock-inclusion-policy.md).

```sql
SELECT id, name FROM intblocks WHERE scope_category = 'igo' ORDER BY id;
```

### Country attribute fields (former attribute intblocks)

Driving side, scripts, DVD region, broadcast standards, legal traditions, and rail gauges
are country columns. Remap retired intblock ids with
`data/datasets/attribute_intblock_migrations.json`.

```sql
-- Was: members of RHTRAFFIC / LHTRAFFIC
SELECT code, name FROM countries WHERE car_side = 'left' ORDER BY code;

SELECT code, name, dvd_region FROM countries WHERE dvd_region = 1;

-- List-of-struct attributes: unnest and filter on id
SELECT c.code, c.name
FROM countries c, UNNEST(c.writing_directions) AS t(d)
WHERE d.id = 'rtl';

SELECT c.code, c.name, g.gauge_mm
FROM countries c, UNNEST(c.rail_gauges) AS t(g)
WHERE g.id = 'russian' AND g."primary" = true;
```

Vocab catalogs: `data/vocabs/`. Coverage is sparse for some fields (migrated from
attribute-partition intblocks). Government-form typology is vocab-only
(`government_forms.yaml`) and is **not** assigned on country records. Verified
recipes: [query-examples.md](query-examples.md).

### Country crosswalk ids

Optional join aids: `geonames_id`, `ioc_code`, `fifa_code`, `fips_code`, and `bbox`.

```sql
SELECT code, name, ioc_code, fifa_code FROM countries
WHERE code_status = 'official_iso3166_1' AND ioc_code IS NOT NULL;
```

### OpenAI-style tool schemas

Copy-ready function definitions for tool-calling agents:

- [`data/schemas/country_lookup.openai.json`](../data/schemas/country_lookup.openai.json)
- [`data/schemas/intblock_lookup.openai.json`](../data/schemas/intblock_lookup.openai.json)

### Schema migration files

When a release changes JSON Schema properties, `data/datasets/migration.vX.Y.Z.json`
lists added/removed/type-changed fields per dataset. Compare against your cached
`schema_hash` before upgrading.

### Blocktypes

Taxonomy definitions for intblock categories. Join `intblocks.blocktype` values to
`blocktypes.id`.

## Field semantics (countries)

### Structured metrics

`population`, `area`, and `gini` are structs, not plain numbers:

```
{value: number, year: integer|null, source: string, source_id: string}
```

- Use `.value` for the numeric field
- `year` is `null` when the source year is unknown (never `0`)

```python
import pandas as pd

# .struct requires ArrowDtype-backed columns
df = pd.read_parquet("data/datasets/countries.parquet", dtype_backend="pyarrow")
pop = df["population"].struct.field("value")
year = df["population"].struct.field("year")

# default backend: struct columns are Python dicts
df = pd.read_parquet("data/datasets/countries.parquet")
pop = df["population"].apply(lambda v: v["value"] if v is not None else None)
```

### World Bank classifications

`region`, `adminregion`, `incomeLevel`, `lendingType` are `{id, value}` structs.
Filter on the stable `id`, not on `value` — labels vary upstream (some regions carry an
`(all income levels)` suffix). `region`/`incomeLevel`/`lendingType` are absent for 8
entities the World Bank does not classify (overseas territories, special statistical areas,
non-standard codes); `adminregion` is absent for 39 records because it only covers low- and
middle-income economies. Do not treat missing values as data errors.

### Borders

`borders` is a list of **ISO 3166-1 alpha-3** land-neighbor codes (e.g. `CAN`, `MEX`),
not alpha-2. Island nations may have empty borders.

### Names and aliases

| Field | Purpose |
|-------|---------|
| `name` | Common English name |
| `official_name` | Formal name |
| `common_names` | Aliases for fuzzy matching |
| `other_names` | Translations `{id, name}` |
| `native_names` | Map of lang code → `{official, common}` |

For entity linking, search across `name`, `common_names`, `other_names`, and codes.

### Provenance

Country records may include `provenance`: list of `{field, source, retrieved_at, url, license}`.
Use this to assess data freshness and attribute upstream sources. See [ATTRIBUTION.md](../ATTRIBUTION.md).

## Field semantics (intblocks)

| Field | Notes |
|-------|-------|
| `includes[].id` | Authoritative member identifier (usually country `code`) |
| `includes[].type` | Member type (`country`, `organization`, etc.) |
| `includes[].status` | Membership status (values vary; not normalized to a small enum) |
| `membership_count` | Declared count; may differ from `len(includes)` |
| `headquarters` | `{city, country, coordinates}` — ~46% populated |
| `legal_status`, `geographic_scope` | Optional; sparsely populated |

## Query recipes

Full catalog with verified row counts: [query-examples.md](query-examples.md).

**DuckDB struct lists:** `UNNEST(column) AS t(row)` then `row.field` (e.g.
`UNNEST(i.includes) AS t(m)` → `m.id`).

### DuckDB: UN members

```sql
SELECT code, name
FROM countries
WHERE un_member = true
ORDER BY name;
```

### DuckDB: land neighbors of Thailand

`borders` stores alpha-3 codes — join on `iso3code`, not `code`.

```sql
SELECT n.code, n.name
FROM countries th,
     UNNEST(th.borders) AS b(neighbor_iso3)
JOIN countries n ON n.iso3code = b.neighbor_iso3
WHERE th.code = 'TH'
ORDER BY n.name;
```

### DuckDB: organizations that include Laos

Join on `includes[].id`, not `includes[].name`.

```sql
SELECT i.id, i.name, m.status
FROM intblocks i, UNNEST(i.includes) AS t(m)
WHERE m.id = 'LA' AND m.type = 'country'
ORDER BY i.name;
```

### DuckDB: org members (NATO)

```sql
SELECT i.id, i.name, m.id AS member_code, m.name AS member_label
FROM intblocks i, UNNEST(i.includes) AS t(m)
WHERE i.id = 'NATO' AND m.type = 'country';
```

### DuckDB: countries in a World Bank region

```sql
SELECT code, name, region.value AS region
FROM countries
WHERE region.value = 'Europe & Central Asia'
  AND code_status = 'official_iso3166_1';
```

### Pandas: resolve intblock alias before join

```python
import json
import pandas as pd

aliases = {a["alias"]: a["target"] for a in json.load(open("data/datasets/intblocks_aliases.json"))}
blocks = pd.read_parquet("data/datasets/intblocks.parquet")
blocks["id"] = blocks["id"].map(lambda x: aliases.get(x, x))
```

## Access paths

| Method | When to use |
|--------|-------------|
| `internacia.duckdb` | SQL analytics, multi-table joins, version check via `_meta` |
| Parquet | Pandas/Polars/Arrow pipelines |
| JSONL.zst | Streaming, language-agnostic JSON consumers |
| [internacia-python](https://github.com/datenoio/internacia-python) | Typed lookups, fuzzy search, filters |
| [internacia-api](https://github.com/datenoio/internacia-api) | HTTP access without local files |
| Source YAML | **Maintainers only** — editing and validation |

Decompress zstd: `zstd -d data/datasets/countries.jsonl.zst`

## Licensing and attribution

- **Data:** CC BY 4.0 — see [DATA_LICENSE](../DATA_LICENSE)
- **Code:** MIT — see [LICENSE](../LICENSE)
- **Upstream:** World Bank (CC BY 4.0), Wikidata (CC0), IANA tzdata (public domain),
  mledoze/countries (ODbL-1.0, `centroid` field only — see the compatibility note in ATTRIBUTION.md)
- **DOI:** [10.5281/zenodo.21452328](https://doi.org/10.5281/zenodo.21452328) (Zenodo concept DOI,
  always resolves to the latest version); machine-readable metadata in [CITATION.cff](../CITATION.cff)

When redistributing or citing, cite the DOI plus the version from the manifest, and credit
upstream sources per [ATTRIBUTION.md](../ATTRIBUTION.md).

## Common mistakes

1. **Parsing YAML sources** instead of exported datasets — slower, may miss build-time normalization
2. **Joining intblocks on `includes[].name`** — use `includes[].id`
3. **Using alpha-2 in borders joins** — borders are alpha-3; join on `iso3code`
4. **Treating missing World Bank fields as errors** — expected for territories outside WB taxonomy
5. **Assuming all 256 codes are ISO official** — filter on `code_status`
6. **Ignoring `schema_hash` on upgrade** — structured fields and types change between releases
7. **Requesting socioeconomic enrichment from this dataset** — out of scope; enrich downstream

## Related documentation

- [docs/agents/query.md](agents/query.md) — query and join workflow (all platforms)
- [docs/agents/zh/query.md](agents/zh/query.md) — 中文查询工作流
- [docs/query-examples.zh.md](query-examples.zh.md) — 已验证中文 DuckDB 示例
- [llms.zh.txt](../llms.zh.txt) — 中文紧凑索引
- [AGENTS.zh.md](../AGENTS.zh.md) — 中文智能体入口
- [query-examples.md](query-examples.md) — verified DuckDB and Pandas query cookbook
- [query-examples-polars.md](query-examples-polars.md) — verified Polars / Parquet query cookbook
- [query-examples-r.md](query-examples-r.md) — verified R / dplyr / Parquet query cookbook
- [query-examples-observable.md](query-examples-observable.md) — Observable Framework / Plot cookbook
- [llms.txt](../llms.txt) — compact index for LLM context windows
- [llms-full.txt](../llms-full.txt) — extended index for crawlers
- [AGENTS.md](../AGENTS.md) — root routing hub
- [README.md](../README.md) — full schema tables and build pipeline
- [country-code-policy.md](country-code-policy.md) — non-standard codes and filtering
- [enrichment.md](enrichment.md) — how profile fields are sourced (maintainers)
- [CHANGELOG.md](../CHANGELOG.md) — breaking changes and migration notes
- [data/schemas/countries.schema.json](../data/schemas/countries.schema.json) — field descriptions for countries
- [data/schemas/intblocks.schema.json](../data/schemas/intblocks.schema.json) — field descriptions for intblocks
