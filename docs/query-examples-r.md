# Query examples (R / dplyr)

Verified [dplyr](https://dplyr.tidyverse.org/) recipes against Parquet exports under
`data/datasets/`, using [arrow](https://arrow.apache.org/docs/r/) for I/O.
For scope, join keys, and field semantics see [ai-consumers.md](ai-consumers.md).
DuckDB / SQL twin: [query-examples.md](query-examples.md).
Polars twin: [query-examples-polars.md](query-examples-polars.md).
Observable / Plot twin: [query-examples-observable.md](query-examples-observable.md).

**Arrow struct and list fields:** after `collect()`, struct columns are data frames
(access with `$`); list columns work with `tidyr::unnest_longer` / `lengths()` /
`purrr::map_lgl`. On an Arrow Table (before `collect()`), dplyr can use `$` for
struct fields (`region$id`) and Arrow compute helpers such as `list_contains`.

```r
install.packages(c("arrow", "dplyr", "tidyr", "purrr", "jsonlite"))
```

```r
library(arrow)
library(dplyr)
library(tidyr)
library(purrr)

countries <- read_parquet("data/datasets/countries.parquet")
intblocks <- read_parquet("data/datasets/intblocks.parquet")
memberships <- read_parquet("data/datasets/memberships.parquet")
blocktypes <- read_parquet("data/datasets/blocktypes.parquet")
```

Prefer `memberships.parquet` for org↔country edges (already flattened). Unnest
`intblocks$includes` only when you need fields not on the edge table (e.g. `note`,
`role`). Call `collect()` when you need a tibble for tidyr/purrr list ops, or keep
the Arrow Table for simple filters and joins.

**Version check** (Parquet has no `_meta` table — use manifests):

```r
library(jsonlite)

for (name in c("countries", "intblocks", "blocktypes", "memberships")) {
  meta <- fromJSON(sprintf("data/datasets/%s.manifest.json", name))
  cat(meta$dataset, meta$version, meta$schema_hash, "\n")
}
```

## Country filters

### UN members only

```r
countries |>
  filter(un_member) |>
  select(code, name) |>
  arrange(name) |>
  collect()
```

**Expected:** 193 rows.

**Gotcha:** `un_member` is a country-level boolean. The `UN` intblock roster can differ
slightly — use the flag for a simple filter, or filter `memberships` on
`intblock_id == "UN"` when you need roster metadata (`status`, `joined`).

### Current ISO countries only (249)

```r
countries |>
  filter(code_status == "official_iso3166_1") |>
  select(code, name, iso3code) |>
  arrange(code) |>
  collect()
```

**Expected:** 249 rows. Seven non-standard codes (`AN`, `JG`, `XK`, `XA`, `XS`, `XT`,
`XN`) are excluded. See [country-code-policy.md](country-code-policy.md).

### Left-hand traffic (driving side)

```r
countries |>
  filter(car_side == "left") |>
  select(code, name) |>
  arrange(code) |>
  collect()
```

**Expected:** 74 rows.

**Gotcha:** Former `LHTRAFFIC` / `RHTRAFFIC` intblocks were retired; remap via
`attribute_intblock_migrations.json`.

### DVD region 1

```r
countries |>
  filter(dvd_region == 1) |>
  select(code, name, dvd_region) |>
  arrange(code) |>
  collect()
```

**Expected:** 8 rows (`AS`, `BM`, `CA`, `GU`, `MP`, `PR`, `US`, `VI`).

### Right-to-left writing direction

```r
countries |>
  collect() |>
  select(code, name, writing_directions) |>
  unnest_longer(writing_directions) |>
  hoist(writing_directions, direction = "id", primary = "primary") |>
  filter(direction == "rtl") |>
  select(code, name, direction, primary) |>
  arrange(code)
```

**Expected:** 28 rows.

**Gotcha:** Vocab ids are `ltr`, `rtl`, `ttb` (`data/vocabs/writing_directions.yaml`).
Empty lists yield no rows after `unnest_longer` (no sentinel null row).

### Cyrillic writing system

```r
countries |>
  collect() |>
  select(code, name, writing_systems) |>
  unnest_longer(writing_systems) |>
  hoist(writing_systems, script = "id") |>
  filter(script == "cyrillic") |>
  select(code, name) |>
  arrange(code)
```

**Expected:** 12 rows (`BA`, `BG`, `BY`, `KG`, `KZ`, `ME`, `MK`, `MN`, `RS`, `RU`,
`TJ`, `UA`).

### NTSC broadcast system

```r
countries |>
  collect() |>
  select(code, name, broadcast_systems) |>
  unnest_longer(broadcast_systems) |>
  hoist(broadcast_systems, broadcast = "id") |>
  filter(broadcast == "ntsc") |>
  select(code, name) |>
  arrange(code)
```

**Expected:** 48 rows.

### Common-law legal tradition

```r
countries |>
  collect() |>
  select(code, name, legal_systems) |>
  unnest_longer(legal_systems) |>
  hoist(legal_systems, legal_system = "id") |>
  filter(legal_system == "common_law") |>
  select(code, name) |>
  arrange(code)
```

**Expected:** 54 rows.

**Gotcha:** Legal *tradition*, not government form. Government-form typology stays
vocab-only and is **not** on country records.

### Russian rail gauge (primary)

```r
countries |>
  collect() |>
  select(code, name, rail_gauges) |>
  unnest_longer(rail_gauges) |>
  hoist(rail_gauges, gauge = "id", gauge_mm = "gauge_mm", primary = "primary") |>
  filter(gauge == "russian", primary == TRUE) |>
  select(code, name, gauge, gauge_mm) |>
  arrange(code)
```

**Expected:** 18 rows (`AM`, `AZ`, `BY`, `EE`, `FI`, `GE`, `KG`, `KP`, `KZ`, `LT`,
`LV`, `MD`, `MN`, `RU`, `TJ`, `TM`, `UA`, `UZ`).

### Sovereign states

```r
countries |>
  filter(entity_type == "sovereign_state") |>
  select(code, name, entity_type) |>
  arrange(name) |>
  collect()
```

**Expected:** 194 rows.

### Independent but not UN members

```r
countries |>
  filter(independent, !un_member) |>
  select(code, name) |>
  collect()
```

**Expected:** 1 row (`VA` Vatican City).

### Landlocked countries

```r
countries |>
  filter(landlocked) |>
  select(code, name, subregion) |>
  arrange(name) |>
  collect()
```

**Expected:** 48 rows (including landlocked non-ISO entities such as `XK`, `XS`, `XT`,
`XN`).

### By World Bank region

```r
countries |>
  filter(region$id == "ECS", code_status == "official_iso3166_1") |>
  transmute(code, name, region = region$value) |>
  arrange(name) |>
  collect()
```

**Expected:** 61 rows.

**Gotcha:** Filter on the stable `region$id` (`ECS`, `EAS`, `LCN`, …), **not** on
`value` — labels are inconsistent upstream. Structs are absent for 8 entities the World
Bank does not classify; `adminregion` is additionally absent for high-income economies
(39 records).

### By income level

```r
countries |>
  filter(incomeLevel$value == "Low income") |>
  transmute(code, name, income = incomeLevel$value) |>
  arrange(name) |>
  collect()
```

**Expected:** 41 rows.

### Structured metric fields

```r
countries |>
  transmute(
    code,
    name,
    pop = population$value,
    pop_year = population$year,
    area_km2 = area$value,
    region_name = region$value
  ) |>
  collect()
```

**Gotcha:** Arrow loads Parquet structs natively — use `$` on the struct column (no
pandas-style `dtype_backend` flag). Missing metrics are null structs / null `$value`,
never `0` as a sentinel year.

## Geography and borders

Land neighbors are **ISO 3166-1 alpha-3** codes in `borders`. Join on
`countries$iso3code`, not `code`.

### Neighbors of Thailand

```r
countries |>
  filter(code == "TH") |>
  select(borders) |>
  collect() |>
  unnest_longer(borders) |>
  inner_join(
    countries |> collect() |> select(code, name, iso3code),
    by = c("borders" = "iso3code")
  ) |>
  select(code, name, iso3code) |>
  arrange(name)
```

**Expected:** 4 rows — `KH` Cambodia, `LA` Lao PDR, `MM` Myanmar, `MY` Malaysia.

### Reverse lookup: who borders Laos?

```r
countries |>
  collect() |>
  filter(map_lgl(borders, ~ "LAO" %in% .x)) |>
  select(code, name) |>
  arrange(name)
```

Arrow-native alternative (no `collect` until the end):

```r
countries |>
  filter(list_contains(borders, "LAO")) |>
  select(code, name) |>
  arrange(name) |>
  collect()
```

**Expected:** 5 rows (China, Cambodia, Myanmar, Thailand, Vietnam).

### Countries with the most land borders

```r
countries |>
  collect() |>
  mutate(border_count = lengths(borders)) |>
  filter(border_count > 0) |>
  select(code, name, border_count) |>
  arrange(desc(border_count)) |>
  slice_head(n = 10)
```

**Expected top:** `CN` (16), `RU` (14), `BR` (10).

### Landlocked in Southeast Asia

```r
countries |>
  filter(landlocked, subregion == "South-Eastern Asia") |>
  select(code, name) |>
  collect()
```

**Expected:** 1 row (`LA` Lao PDR).

### Island nations and territories (no land borders)

```r
countries |>
  collect() |>
  filter(lengths(borders) == 0) |>
  select(code, name) |>
  arrange(name)
```

**Expected:** 92 rows. Empty list, not `NULL`.

## Intblocks and membership

Join on member `id` / `country_code` (usually country alpha-2). **`includes[].name` is a
display label only** — do not use it for joins.

### Helper: unnest `includes` without column clashes

`includes` structs also have `id` and `name`. Rename the intblock columns first:

```r
country_memberships <- function(intblocks) {
  intblocks |>
    select(intblock_id = id, intblock_name = name, includes) |>
    collect() |>
    unnest_longer(includes) |>
    hoist(
      includes,
      id = "id",
      name = "name",
      type = "type",
      status = "status",
      joined = "joined",
      left = "left",
      note = "note"
    ) |>
    filter(type == "country")
}
```

Prefer the pre-built edge table when you only need id / status / dates:

```r
memberships  # intblock_id, country_code, include_type, status, joined, left
```

**Gotcha:** the edge column is named `left` (departure date). Quote it in dplyr with
backticks: `` `left` `` — otherwise R resolves the base `left()` function.

### Organizations that include Laos

```r
memberships |>
  filter(country_code == "LA") |>
  left_join(
    intblocks |> select(id, name),
    by = c("intblock_id" = "id")
  ) |>
  select(intblock_id, name, status, joined) |>
  arrange(name) |>
  collect()
```

**Expected:** 191 rows.

ASEAN roster:

```r
memberships |>
  filter(intblock_id == "ASEAN") |>
  select(country_code, status) |>
  arrange(country_code) |>
  collect()
```

**Expected:** 11 ASEAN member states.

### NATO members

```r
memberships |>
  filter(intblock_id == "NATO", status == "member") |>
  select(country_code, status, joined) |>
  arrange(country_code) |>
  collect()
```

**Expected:** 32 rows.

### EU members

```r
memberships |>
  filter(intblock_id == "EU") |>
  select(country_code, status) |>
  arrange(country_code) |>
  collect()
```

**Expected:** 27 rows.

### Observer members of an organization

```r
country_memberships(intblocks) |>
  filter(intblock_id == "BSEC", status == "observer") |>
  select(intblock_id, intblock_name, member_code = id, name) |>
  arrange(member_code)
```

**Expected:** 14 observer entries for BSEC.

### Trade blocs by taxonomy

```r
intblocks |>
  collect() |>
  filter(map_lgl(blocktype, ~ "trade" %in% .x)) |>
  select(id, name, blocktype) |>
  arrange(name)
```

**Expected:** 11 rows.

Or join the taxonomy table after unnesting `blocktype`:

```r
intblocks |>
  select(id, name, blocktype) |>
  collect() |>
  unnest_longer(blocktype) |>
  filter(blocktype == "trade") |>
  left_join(
    blocktypes |> collect() |> select(bt_id = id, category = name),
    by = c("blocktype" = "bt_id")
  ) |>
  select(id, name, category) |>
  arrange(name)
```

### Formal organizations headquartered in Switzerland

```r
intblocks |>
  filter(headquarters$country == "CH", status == "formal") |>
  transmute(id, name, city = headquarters$city) |>
  arrange(name) |>
  collect()
```

**Expected:** 58 rows.

### Child organizations of the UN

```r
intblocks |>
  collect() |>
  filter(map_lgl(partof, ~ "UN" %in% .x)) |>
  select(id, name, partof) |>
  arrange(name)
```

**Expected:** 37 rows.

### Multilingual intblock names

```r
intblocks |>
  select(id, name, other_names) |>
  collect() |>
  unnest_longer(other_names) |>
  hoist(other_names, translated_name = "name", lang = "id") |>
  filter(lang == "fr") |>
  select(id, name, translated_name, lang) |>
  arrange(id) |>
  slice_head(n = 20)
```

### Resolve intblock id aliases before join

```r
aliases <- read_parquet("data/datasets/intblocks_aliases.parquet")
# columns: alias, target, reason, since, note

blocks <- intblocks |>
  left_join(aliases, by = c("id" = "alias")) |>
  mutate(id_resolved = coalesce(target, id)) |>
  collect()
```

## Cross-dataset joins

### UN members not in the EU

```r
eu_codes <- memberships |>
  filter(intblock_id == "EU") |>
  select(country_code) |>
  collect()

countries |>
  filter(un_member) |>
  collect() |>
  anti_join(eu_codes, by = c("code" = "country_code")) |>
  select(code, name) |>
  arrange(name)
```

**Expected:** 166 rows.

### Countries in both NATO and EU

```r
nato <- memberships |>
  filter(intblock_id == "NATO") |>
  select(code = country_code) |>
  collect()

eu <- memberships |>
  filter(intblock_id == "EU") |>
  select(country_code) |>
  collect()

countries |>
  collect() |>
  inner_join(nato, by = "code") |>
  inner_join(eu, by = c("code" = "country_code")) |>
  select(code, name) |>
  arrange(name)
```

**Expected:** 23 rows.

### Compare UN member flag vs UN intblock roster

```r
flag_n <- countries |> filter(un_member) |> collect() |> nrow()
roster_n <- memberships |>
  filter(intblock_id == "UN", include_type == "country") |>
  collect() |>
  nrow()
c(flag_n, roster_n)  # both 193
```

### Organizations a country belongs to

```r
memberships |>
  filter(country_code == "FR") |>
  left_join(
    intblocks |> select(id, name, blocktype),
    by = c("intblock_id" = "id")
  ) |>
  select(intblock_id, name, blocktype) |>
  arrange(name) |>
  collect()
```

### Russia: former memberships only

```r
country_memberships(intblocks) |>
  filter(id == "RU", status == "former_member") |>
  select(intblock_id, intblock_name, status, joined, left, note) |>
  arrange(joined)
```

**Expected:** 11 rows (`BEACST`, `DANUBECOM`, `EASTERNBLOC`, `ECHR`, `EUA`, `GRECO`,
`ICES`, `JCPOA`, `NSS`, `OPENSKY`, `RAMSAR`).

**Gotcha:** Current Parquet exports include `includes[].left` and `memberships.left`.
Prefer Parquet / `memberships` when you need departure dates.

### Russia: departed around March 2022

```r
country_memberships(intblocks) |>
  filter(
    id == "RU",
    status == "former_member",
    startsWith(coalesce(left, ""), "2022-03") |
      grepl("March 2022", coalesce(note, ""), ignore.case = TRUE)
  ) |>
  transmute(
    intblock_id,
    organization = intblock_name,
    status,
    joined,
    departed = left,
    note
  ) |>
  arrange(departed)
```

**Expected:** 3 rows (`ECHR`, `EUA`, `ICES`).

## Membership overlap and set logic

### NATO members outside the EU

```r
nato <- memberships |>
  filter(intblock_id == "NATO") |>
  select(country_code) |>
  collect()

eu <- memberships |>
  filter(intblock_id == "EU") |>
  select(country_code) |>
  collect()

nato |>
  anti_join(eu, by = "country_code") |>
  inner_join(
    countries |> collect() |> select(code, name),
    by = c("country_code" = "code")
  ) |>
  select(country_code, name) |>
  arrange(country_code)
```

**Expected:** 9 rows.

### EU members outside the eurozone

Euro area intblock id is `EMU`:

```r
eu <- memberships |>
  filter(intblock_id == "EU") |>
  select(country_code) |>
  collect()

emu <- memberships |>
  filter(intblock_id == "EMU") |>
  select(country_code) |>
  collect()

eu |>
  anti_join(emu, by = "country_code") |>
  inner_join(
    countries |> collect() |> select(code, name),
    by = c("country_code" = "code")
  ) |>
  select(country_code, name) |>
  arrange(country_code)
```

**Expected:** 7 rows (`BG`, `CZ`, `DK`, `HU`, `PL`, `RO`, `SE`).

### Jaccard similarity between organization rosters

```r
nato <- memberships |>
  filter(intblock_id == "NATO") |>
  collect() |>
  pull(country_code)

eu <- memberships |>
  filter(intblock_id == "EU") |>
  collect() |>
  pull(country_code)

jaccard <- round(length(intersect(nato, eu)) / length(union(nato, eu)), 2)
# 0.64
```

## Organization density

### Most organization-dense UN members

```r
memberships |>
  filter(include_type == "country") |>
  collect() |>
  count(country_code, name = "org_count") |>
  inner_join(
    countries |> filter(un_member) |> collect() |> select(code, name),
    by = c("country_code" = "code")
  ) |>
  arrange(desc(org_count)) |>
  slice_head(n = 10)
```

### Least organization-dense UN members

```r
memberships |>
  filter(include_type == "country") |>
  collect() |>
  count(country_code, name = "org_count") |>
  inner_join(
    countries |> filter(un_member) |> collect() |> select(code, name),
    by = c("country_code" = "code")
  ) |>
  arrange(org_count) |>
  slice_head(n = 10)
```

## Organization lifecycle

### Predecessor and successor chains

```r
intblocks |>
  collect() |>
  filter(!is.na(predecessor) | !is.na(successor)) |>
  select(id, predecessor, successor, dissolved) |>
  arrange(id)
```

**Expected:** 24 rows.

### Former members with join and departure dates

```r
memberships |>
  filter(status == "former_member", !is.na(`left`)) |>
  select(intblock_id, country_code, joined, `left`) |>
  arrange(desc(`left`)) |>
  slice_head(n = 20) |>
  collect()
```

## Policy-researcher recipes

### NATO ∩ EU members

```r
nato <- memberships |>
  filter(
    intblock_id == "NATO",
    coalesce(status, "member") != "former_member"
  ) |>
  select(code = country_code) |>
  collect()

eu <- memberships |>
  filter(
    intblock_id == "EU",
    coalesce(status, "member") != "former_member"
  ) |>
  select(country_code) |>
  collect()

nato |>
  inner_join(eu, by = c("code" = "country_code")) |>
  arrange(code)
```

**Expected:** 23 codes.

### Regional economic communities overlapping a country

```r
memberships |>
  filter(
    country_code == "KE",
    coalesce(status, "member") != "former_member"
  ) |>
  left_join(
    intblocks |> select(id, name, blocktype),
    by = c("intblock_id" = "id")
  ) |>
  collect() |>
  filter(map_lgl(blocktype, ~ "economic" %in% .x)) |>
  select(intblock_id, name) |>
  arrange(intblock_id)
```

## Embedding / RAG recipes

Prefer **lite** exports for retrieval corpora; hydrate full records by primary key.

```r
lite <- read_parquet("data/datasets/intblocks-lite.parquet")
rows <- lite |>
  filter(status == "formal", scope_category == "igo") |>
  transmute(id, name, text = coalesce(description, "")) |>
  collect()
# Embed paste0(id, ": ", name, ". ", substr(text, 1, 500)) then retrieve; join full row on id.
```

Countries lite path for entity linking:

```r
read_parquet("data/datasets/countries-lite.parquet") |>
  filter(code_status == "official_iso3166_1") |>
  select(code, name, iso3code, wikidata_id, entity_type, code_status) |>
  collect()
```

## Other access paths

- **DuckDB SQL:** [query-examples.md](query-examples.md) — `data/datasets/internacia.duckdb`
- **Polars:** [query-examples-polars.md](query-examples-polars.md) — same Parquet exports
- **Observable / Plot:** [query-examples-observable.md](query-examples-observable.md) — DuckDB-Wasm + Plot
- **[internacia-python](https://github.com/datenoio/internacia-python)** — typed lookups
  without writing frame code
- **[internacia-api](https://github.com/datenoio/internacia-api)** — HTTP access without
  local dataset files

## Related documentation

- [ai-consumers.md](ai-consumers.md) — consumption contract and common mistakes
- [query-examples.md](query-examples.md) — verified DuckDB recipes
- [query-examples-polars.md](query-examples-polars.md) — verified Polars recipes
- [query-examples-observable.md](query-examples-observable.md) — Observable / Plot recipes
- [country-code-policy.md](country-code-policy.md) — entity status and code filtering
- [intblock-inclusion-policy.md](intblock-inclusion-policy.md) — scope_category taxonomy
- [getting-started.md](getting-started.md) — non-programmer path
- [llms.txt](../llms.txt) — compact index for LLM context windows
