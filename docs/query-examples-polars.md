# Query examples (Polars)

Verified [Polars](https://pola.rs/) recipes against Parquet exports under `data/datasets/`.
For scope, join keys, and field semantics see [ai-consumers.md](ai-consumers.md).
DuckDB / SQL twin: [query-examples.md](query-examples.md).

**Polars struct and list fields:** use `.struct.field("…")` on struct columns and
`.list.contains` / `.list.len` / `.explode(..., empty_as_null=True)` on lists.

```bash
pip install polars
```

```python
import polars as pl

countries = pl.read_parquet("data/datasets/countries.parquet")
intblocks = pl.read_parquet("data/datasets/intblocks.parquet")
memberships = pl.read_parquet("data/datasets/memberships.parquet")
blocktypes = pl.read_parquet("data/datasets/blocktypes.parquet")
```

Prefer `memberships.parquet` for org↔country edges (already flattened). Explode
`intblocks.includes` only when you need fields not on the edge table (e.g. `note`,
`role`). Lazy scans work the same way: `pl.scan_parquet(...).filter(...).collect()`.

**Version check** (Parquet has no `_meta` table — use manifests):

```python
import json
from pathlib import Path

for name in ("countries", "intblocks", "blocktypes", "memberships"):
    meta = json.loads(Path(f"data/datasets/{name}.manifest.json").read_text())
    print(meta["dataset"], meta["version"], meta["schema_hash"])
```

## Country filters

### UN members only

```python
(
    countries
    .filter(pl.col("un_member"))
    .select("code", "name")
    .sort("name")
)
```

**Expected:** 193 rows.

**Gotcha:** `un_member` is a country-level boolean. The `UN` intblock roster can differ
slightly — use the flag for a simple filter, or filter `memberships` on `intblock_id ==
"UN"` when you need roster metadata (`status`, `joined`).

### Current ISO countries only (249)

```python
(
    countries
    .filter(pl.col("code_status") == "official_iso3166_1")
    .select("code", "name", "iso3code")
    .sort("code")
)
```

**Expected:** 249 rows. Seven non-standard codes (`AN`, `JG`, `XK`, `XA`, `XS`, `XT`,
`XN`) are excluded. See [country-code-policy.md](country-code-policy.md).

### Left-hand traffic (driving side)

```python
(
    countries
    .filter(pl.col("car_side") == "left")
    .select("code", "name")
    .sort("code")
)
```

**Expected:** 74 rows.

**Gotcha:** Former `LHTRAFFIC` / `RHTRAFFIC` intblocks were retired; remap via
`attribute_intblock_migrations.json`.

### DVD region 1

```python
(
    countries
    .filter(pl.col("dvd_region") == 1)
    .select("code", "name", "dvd_region")
    .sort("code")
)
```

**Expected:** 8 rows (`AS`, `BM`, `CA`, `GU`, `MP`, `PR`, `US`, `VI`).

### Right-to-left writing direction

```python
(
    countries
    .explode("writing_directions", empty_as_null=True)
    .drop_nulls("writing_directions")
    .filter(pl.col("writing_directions").struct.field("id") == "rtl")
    .select(
        "code",
        "name",
        pl.col("writing_directions").struct.field("id").alias("direction"),
        pl.col("writing_directions").struct.field("primary").alias("primary"),
    )
    .sort("code")
)
```

**Expected:** 28 rows.

**Gotcha:** Vocab ids are `ltr`, `rtl`, `ttb` (`data/vocabs/writing_directions.yaml`).
Pass `empty_as_null=True` on `.explode` (Polars 2.0 default changes).

### Cyrillic writing system

```python
(
    countries
    .explode("writing_systems", empty_as_null=True)
    .drop_nulls("writing_systems")
    .filter(pl.col("writing_systems").struct.field("id") == "cyrillic")
    .select("code", "name")
    .sort("code")
)
```

**Expected:** 12 rows (`BA`, `BG`, `BY`, `KG`, `KZ`, `ME`, `MK`, `MN`, `RS`, `RU`,
`TJ`, `UA`).

### NTSC broadcast system

```python
(
    countries
    .explode("broadcast_systems", empty_as_null=True)
    .drop_nulls("broadcast_systems")
    .filter(pl.col("broadcast_systems").struct.field("id") == "ntsc")
    .select("code", "name")
    .sort("code")
)
```

**Expected:** 48 rows.

### Common-law legal tradition

```python
(
    countries
    .explode("legal_systems", empty_as_null=True)
    .drop_nulls("legal_systems")
    .filter(pl.col("legal_systems").struct.field("id") == "common_law")
    .select("code", "name")
    .sort("code")
)
```

**Expected:** 54 rows.

**Gotcha:** Legal *tradition*, not government form. Government-form typology stays
vocab-only and is **not** on country records.

### Russian rail gauge (primary)

```python
(
    countries
    .explode("rail_gauges", empty_as_null=True)
    .drop_nulls("rail_gauges")
    .filter(
        (pl.col("rail_gauges").struct.field("id") == "russian")
        & (pl.col("rail_gauges").struct.field("primary") == True)
    )
    .select(
        "code",
        "name",
        pl.col("rail_gauges").struct.field("id").alias("gauge"),
        pl.col("rail_gauges").struct.field("gauge_mm").alias("gauge_mm"),
    )
    .sort("code")
)
```

**Expected:** 18 rows (`AM`, `AZ`, `BY`, `EE`, `FI`, `GE`, `KG`, `KP`, `KZ`, `LT`,
`LV`, `MD`, `MN`, `RU`, `TJ`, `TM`, `UA`, `UZ`).

### Sovereign states

```python
(
    countries
    .filter(pl.col("entity_type") == "sovereign_state")
    .select("code", "name", "entity_type")
    .sort("name")
)
```

**Expected:** 194 rows.

### Independent but not UN members

```python
countries.filter(pl.col("independent") & ~pl.col("un_member")).select("code", "name")
```

**Expected:** 1 row (`VA` Vatican City).

### Landlocked countries

```python
(
    countries
    .filter(pl.col("landlocked"))
    .select("code", "name", "subregion")
    .sort("name")
)
```

**Expected:** 48 rows (including landlocked non-ISO entities such as `XK`, `XS`, `XT`,
`XN`).

### By World Bank region

```python
(
    countries
    .filter(
        (pl.col("region").struct.field("id") == "ECS")
        & (pl.col("code_status") == "official_iso3166_1")
    )
    .select(
        "code",
        "name",
        pl.col("region").struct.field("value").alias("region"),
    )
    .sort("name")
)
```

**Expected:** 61 rows.

**Gotcha:** Filter on the stable `region.id` (`ECS`, `EAS`, `LCN`, …), **not** on
`value` — labels are inconsistent upstream. Structs are absent for 8 entities the World
Bank does not classify; `adminregion` is additionally absent for high-income economies
(39 records).

### By income level

```python
(
    countries
    .filter(pl.col("incomeLevel").struct.field("value") == "Low income")
    .select(
        "code",
        "name",
        pl.col("incomeLevel").struct.field("value").alias("income"),
    )
    .sort("name")
)
```

**Expected:** 41 rows.

### Structured metric fields

```python
(
    countries
    .select(
        "code",
        "name",
        pl.col("population").struct.field("value").alias("pop"),
        pl.col("population").struct.field("year").alias("pop_year"),
        pl.col("area").struct.field("value").alias("area_km2"),
        pl.col("region").struct.field("value").alias("region_name"),
    )
)
```

**Gotcha:** Polars loads Parquet structs natively — no `dtype_backend` flag (unlike
pandas). Missing metrics are null structs / null `.value`, never `0` as a sentinel year.

## Geography and borders

Land neighbors are **ISO 3166-1 alpha-3** codes in `borders`. Join on
`countries.iso3code`, not `code`.

### Neighbors of Thailand

```python
(
    countries
    .filter(pl.col("code") == "TH")
    .select("borders")
    .explode("borders", empty_as_null=True)
    .join(countries, left_on="borders", right_on="iso3code")
    .select("code", "name", "iso3code")
    .sort("name")
)
```

**Expected:** 4 rows — `KH` Cambodia, `LA` Lao PDR, `MM` Myanmar, `MY` Malaysia.

### Reverse lookup: who borders Laos?

```python
(
    countries
    .filter(pl.col("borders").list.contains("LAO"))
    .select("code", "name")
    .sort("name")
)
```

**Expected:** 5 rows (China, Cambodia, Myanmar, Thailand, Vietnam).

### Countries with the most land borders

```python
(
    countries
    .with_columns(pl.col("borders").list.len().alias("border_count"))
    .filter(pl.col("border_count") > 0)
    .select("code", "name", "border_count")
    .sort("border_count", descending=True)
    .head(10)
)
```

**Expected top:** `CN` (16), `RU` (14), `BR` (10).

### Landlocked in Southeast Asia

```python
countries.filter(
    pl.col("landlocked") & (pl.col("subregion") == "South-Eastern Asia")
).select("code", "name")
```

**Expected:** 1 row (`LA` Lao PDR).

### Island nations and territories (no land borders)

```python
(
    countries
    .filter(pl.col("borders").list.len() == 0)
    .select("code", "name")
    .sort("name")
)
```

**Expected:** 92 rows. Empty list, not `NULL`.

## Intblocks and membership

Join on member `id` / `country_code` (usually country alpha-2). **`includes[].name` is a
display label only** — do not use it for joins.

### Helper: explode `includes` without column clashes

`includes` structs also have `id` and `name`. Rename the intblock columns first:

```python
def country_memberships(intblocks: pl.DataFrame) -> pl.DataFrame:
    return (
        intblocks
        .select(
            pl.col("id").alias("intblock_id"),
            pl.col("name").alias("intblock_name"),
            "includes",
        )
        .explode("includes", empty_as_null=True)
        .drop_nulls("includes")
        .unnest("includes")
        .filter(pl.col("type") == "country")
    )
```

Prefer the pre-built edge table when you only need id / status / dates:

```python
memberships  # intblock_id, country_code, include_type, status, joined, left
```

### Organizations that include Laos

```python
(
    memberships
    .filter(pl.col("country_code") == "LA")
    .join(intblocks.select("id", "name"), left_on="intblock_id", right_on="id")
    .select("intblock_id", "name", "status", "joined")
    .sort("name")
)
```

**Expected:** 191 rows.

ASEAN roster:

```python
(
    memberships
    .filter(pl.col("intblock_id") == "ASEAN")
    .select("country_code", "status")
    .sort("country_code")
)
```

**Expected:** 11 ASEAN member states.

### NATO members

```python
(
    memberships
    .filter((pl.col("intblock_id") == "NATO") & (pl.col("status") == "member"))
    .select("country_code", "status", "joined")
    .sort("country_code")
)
```

**Expected:** 32 rows.

### EU members

```python
(
    memberships
    .filter(pl.col("intblock_id") == "EU")
    .select("country_code", "status")
    .sort("country_code")
)
```

**Expected:** 27 rows.

### Observer members of an organization

```python
(
    country_memberships(intblocks)
    .filter((pl.col("intblock_id") == "BSEC") & (pl.col("status") == "observer"))
    .select("intblock_id", "intblock_name", pl.col("id").alias("member_code"), "name")
    .sort("member_code")
)
```

**Expected:** 14 observer entries for BSEC.

### Trade blocs by taxonomy

```python
(
    intblocks
    .filter(pl.col("blocktype").list.contains("trade"))
    .select("id", "name", "blocktype")
    .sort("name")
)
```

**Expected:** 11 rows.

Or join the taxonomy table after exploding `blocktype`:

```python
(
    intblocks
    .explode("blocktype", empty_as_null=True)
    .drop_nulls("blocktype")
    .join(blocktypes, left_on="blocktype", right_on="id")
    .filter(pl.col("blocktype") == "trade")
    .select(pl.col("id"), pl.col("name"), pl.col("name_right").alias("category"))
    .sort("name")
)
```

### Formal organizations headquartered in Switzerland

```python
(
    intblocks
    .filter(
        (pl.col("headquarters").struct.field("country") == "CH")
        & (pl.col("status") == "formal")
    )
    .select("id", "name", pl.col("headquarters").struct.field("city").alias("city"))
    .sort("name")
)
```

**Expected:** 58 rows.

### Child organizations of the UN

```python
(
    intblocks
    .filter(pl.col("partof").list.contains("UN"))
    .select("id", "name", "partof")
    .sort("name")
)
```

**Expected:** 37 rows.

### Multilingual intblock names

```python
(
    intblocks
    .explode("other_names", empty_as_null=True)
    .drop_nulls("other_names")
    .filter(pl.col("other_names").struct.field("id") == "fr")
    .select(
        "id",
        "name",
        pl.col("other_names").struct.field("name").alias("translated_name"),
        pl.col("other_names").struct.field("id").alias("lang"),
    )
    .sort("id")
    .head(20)
)
```

### Resolve intblock id aliases before join

```python
aliases = pl.read_parquet("data/datasets/intblocks_aliases.parquet")
# columns: alias, target, reason, since, note

blocks = (
    intblocks
    .join(aliases, left_on="id", right_on="alias", how="left")
    .with_columns(pl.coalesce(pl.col("target"), pl.col("id")).alias("id_resolved"))
)
```

## Cross-dataset joins

### UN members not in the EU

```python
(
    countries
    .filter(pl.col("un_member"))
    .join(
        memberships.filter(pl.col("intblock_id") == "EU").select("country_code"),
        left_on="code",
        right_on="country_code",
        how="anti",
    )
    .select("code", "name")
    .sort("name")
)
```

**Expected:** 166 rows.

### Countries in both NATO and EU

```python
nato = memberships.filter(pl.col("intblock_id") == "NATO").select(
    pl.col("country_code").alias("code")
)
eu = memberships.filter(pl.col("intblock_id") == "EU").select("country_code")

(
    countries
    .join(nato, on="code")
    .join(eu, left_on="code", right_on="country_code")
    .select("code", "name")
    .sort("name")
)
```

**Expected:** 23 rows.

### Compare UN member flag vs UN intblock roster

```python
flag_n = countries.filter(pl.col("un_member")).height
roster_n = memberships.filter(
    (pl.col("intblock_id") == "UN") & (pl.col("include_type") == "country")
).height
print(flag_n, roster_n)  # both 193
```

### Organizations a country belongs to

```python
(
    memberships
    .filter(pl.col("country_code") == "FR")
    .join(intblocks.select("id", "name", "blocktype"), left_on="intblock_id", right_on="id")
    .select("intblock_id", "name", "blocktype")
    .sort("name")
)
```

### Russia: former memberships only

```python
(
    country_memberships(intblocks)
    .filter((pl.col("id") == "RU") & (pl.col("status") == "former_member"))
    .select("intblock_id", "intblock_name", "status", "joined", "left", "note")
    .sort("joined", nulls_last=True)
)
```

**Expected:** 11 rows (`BEACST`, `DANUBECOM`, `EASTERNBLOC`, `ECHR`, `EUA`, `GRECO`,
`ICES`, `JCPOA`, `NSS`, `OPENSKY`, `RAMSAR`).

**Gotcha:** Current Parquet exports include `includes[].left` and `memberships.left`.
Older cookbook notes about omitting departure dates apply to some historical DuckDB
builds — prefer Parquet / `memberships` when you need `left`.

### Russia: departed around March 2022

```python
(
    country_memberships(intblocks)
    .filter(
        (pl.col("id") == "RU")
        & (pl.col("status") == "former_member")
        & (
            pl.col("left").str.starts_with("2022-03")
            | pl.col("note").str.contains("(?i)March 2022")
        )
    )
    .select(
        "intblock_id",
        pl.col("intblock_name").alias("organization"),
        "status",
        "joined",
        pl.col("left").alias("departed"),
        "note",
    )
    .sort("departed")
)
```

**Expected:** 3 rows (`ECHR`, `EUA`, `ICES`).

## Membership overlap and set logic

### NATO members outside the EU

```python
(
    memberships
    .filter(pl.col("intblock_id") == "NATO")
    .select("country_code")
    .join(
        memberships.filter(pl.col("intblock_id") == "EU").select("country_code"),
        on="country_code",
        how="anti",
    )
    .join(countries.select("code", "name"), left_on="country_code", right_on="code")
    .select("country_code", "name")
    .sort("country_code")
)
```

**Expected:** 9 rows.

### EU members outside the eurozone

Euro area intblock id is `EMU`:

```python
(
    memberships
    .filter(pl.col("intblock_id") == "EU")
    .select("country_code")
    .join(
        memberships.filter(pl.col("intblock_id") == "EMU").select("country_code"),
        on="country_code",
        how="anti",
    )
    .join(countries.select("code", "name"), left_on="country_code", right_on="code")
    .select("country_code", "name")
    .sort("country_code")
)
```

**Expected:** 7 rows (`BG`, `CZ`, `DK`, `HU`, `PL`, `RO`, `SE`).

### Jaccard similarity between organization rosters

```python
nato = set(
    memberships.filter(pl.col("intblock_id") == "NATO")["country_code"].to_list()
)
eu = set(memberships.filter(pl.col("intblock_id") == "EU")["country_code"].to_list())
jaccard = round(len(nato & eu) / len(nato | eu), 2)
# 0.64
```

## Organization density

### Most organization-dense UN members

```python
(
    memberships
    .filter(pl.col("include_type") == "country")
    .group_by("country_code")
    .len()
    .join(
        countries.filter(pl.col("un_member")).select("code", "name"),
        left_on="country_code",
        right_on="code",
    )
    .sort("len", descending=True)
    .head(10)
)
```

### Least organization-dense UN members

```python
(
    memberships
    .filter(pl.col("include_type") == "country")
    .group_by("country_code")
    .len()
    .join(
        countries.filter(pl.col("un_member")).select("code", "name"),
        left_on="country_code",
        right_on="code",
    )
    .sort("len")
    .head(10)
)
```

## Organization lifecycle

### Predecessor and successor chains

```python
(
    intblocks
    .filter(pl.col("predecessor").is_not_null() | pl.col("successor").is_not_null())
    .select("id", "predecessor", "successor", "dissolved")
    .sort("id")
)
```

**Expected:** 24 rows.

### Former members with join and departure dates

```python
(
    memberships
    .filter((pl.col("status") == "former_member") & pl.col("left").is_not_null())
    .select("intblock_id", "country_code", "joined", "left")
    .sort("left", descending=True)
    .head(20)
)
```

## Policy-researcher recipes

### NATO ∩ EU members

```python
(
    memberships
    .filter(
        (pl.col("intblock_id") == "NATO")
        & (pl.col("status").fill_null("member") != "former_member")
    )
    .select(pl.col("country_code").alias("code"))
    .join(
        memberships.filter(
            (pl.col("intblock_id") == "EU")
            & (pl.col("status").fill_null("member") != "former_member")
        ).select("country_code"),
        left_on="code",
        right_on="country_code",
    )
    .sort("code")
)
```

**Expected:** 23 codes.

### Regional economic communities overlapping a country

```python
(
    memberships
    .filter(
        (pl.col("country_code") == "KE")
        & (pl.col("status").fill_null("member") != "former_member")
    )
    .join(intblocks.select("id", "name", "blocktype"), left_on="intblock_id", right_on="id")
    .filter(pl.col("blocktype").list.contains("economic"))
    .select("intblock_id", "name")
    .sort("intblock_id")
)
```

## Embedding / RAG recipes

Prefer **lite** exports for retrieval corpora; hydrate full records by primary key.

```python
lite = pl.read_parquet("data/datasets/intblocks-lite.parquet")
rows = (
    lite
    .filter((pl.col("status") == "formal") & (pl.col("scope_category") == "igo"))
    .select("id", "name", pl.col("description").fill_null(""))
)
# Embed f"{id}: {name}. {text[:500]}" then retrieve; join full row on id.
```

Countries lite path for entity linking:

```python
(
    pl.read_parquet("data/datasets/countries-lite.parquet")
    .filter(pl.col("code_status") == "official_iso3166_1")
    .select("code", "name", "iso3code", "wikidata_id", "entity_type", "code_status")
)
```

## Other access paths

- **DuckDB SQL:** [query-examples.md](query-examples.md) — `data/datasets/internacia.duckdb`
- **[internacia-python](https://github.com/datenoio/internacia-python)** — typed lookups
  without writing frame code
- **[internacia-api](https://github.com/datenoio/internacia-api)** — HTTP access without
  local dataset files

## Related documentation

- [ai-consumers.md](ai-consumers.md) — consumption contract and common mistakes
- [query-examples.md](query-examples.md) — verified DuckDB recipes
- [country-code-policy.md](country-code-policy.md) — entity status and code filtering
- [intblock-inclusion-policy.md](intblock-inclusion-policy.md) — scope_category taxonomy
- [getting-started.md](getting-started.md) — non-programmer path
- [llms.txt](../llms.txt) — compact index for LLM context windows
