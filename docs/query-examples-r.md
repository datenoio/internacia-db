# Query examples (R / dplyr)

[dplyr](https://dplyr.tidyverse.org/) recipes against Parquet exports under
`data/datasets/`, using [arrow](https://arrow.apache.org/docs/r/) for I/O.
For scope, join keys, and field semantics see [ai-consumers.md](ai-consumers.md).
DuckDB / SQL twin: [query-examples.md](query-examples.md).
Polars twin: [query-examples-polars.md](query-examples-polars.md).
Observable / Plot twin: [query-examples-observable.md](query-examples-observable.md).

Expected results were checked by running these recipes against internacia-db 5.2.0
(R 4.6, arrow 26, dplyr 1.2, tidyr 1.3). This cookbook is not run in CI, so counts can
drift as the data changes; see the
[cookbook coverage policy](query-examples.md#cookbook-coverage-parity-policy).

**Arrow struct and list fields:** `read_parquet()` returns a tibble. Struct columns are
data-frame columns (access with `$`, e.g. `region$id`); list columns are lists (use
`lengths()` / `purrr::map_lgl`); lists of structs are lists of tibbles (expand with
`tidyr::unnest`). On an Arrow Table (`read_parquet(..., as_data_frame = FALSE)`), dplyr
verbs and struct `$` access run in Arrow, but list columns need `collect()` first: arrow
has no list-membership helper such as `list_contains`, and Arrow joins cannot carry list
columns (e.g. `blocktype`).

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
`intblocks$includes` only when you need fields not on the edge table (e.g. `note`). On
the tibbles loaded above, `collect()` is a no-op; the recipes keep it so they also run
on Arrow Tables (`as_data_frame = FALSE`), except the two joins that carry `blocktype`.

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

**Gotcha:** `un_member` is a country-level boolean. The `UN` intblock has 193 full
members and two observer seats. Filter `memberships` by `intblock_id == "UN"`
and status `member` / `founding_member` for full-member roster metadata.

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
  unnest(writing_directions) |>
  filter(id == "rtl") |>
  select(code, name, direction = id, primary) |>
  arrange(code)
```

**Expected:** 28 rows.

**Gotcha:** Vocab ids are `ltr`, `rtl`, `ttb` (`data/vocabs/writing_directions.yaml`).
Countries without values have a null list and yield no rows after `unnest` (no sentinel
null row); pass `keep_empty = TRUE` to keep them.

### Cyrillic writing system

```r
countries |>
  collect() |>
  select(code, name, writing_systems) |>
  unnest(writing_systems) |>
  filter(id == "cyrillic") |>
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
  unnest(broadcast_systems) |>
  filter(id == "ntsc") |>
  select(code, name) |>
  arrange(code)
```

**Expected:** 48 rows.

### Common-law legal tradition

```r
countries |>
  collect() |>
  select(code, name, legal_systems) |>
  unnest(legal_systems) |>
  filter(id == "common_law") |>
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
  unnest(rail_gauges) |>
  filter(id == "russian", primary == TRUE) |>
  select(code, name, gauge = id, gauge_mm) |>
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
`value` — the World Bank renames regions. Structs are absent for 8 entities the World
Bank does not classify; `adminregion` is additionally absent for high-income economies
(119 records in all).

### By income level

```r
countries |>
  filter(incomeLevel$value == "Low income") |>
  transmute(code, name, income = incomeLevel$value) |>
  arrange(name) |>
  collect()
```

**Expected:** 25 rows.

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
  select(code, name, iso3code = borders) |>
  arrange(name)
```

**Expected:** 4 rows — `KH` Cambodia, `LA` Lao PDR, `MY` Malaysia, `MM` Myanmar.

### Reverse lookup: who borders Laos?

```r
countries |>
  collect() |>
  filter(map_lgl(borders, ~ "LAO" %in% .x)) |>
  select(code, name) |>
  arrange(name)
```

**Expected:** 5 rows (Cambodia, China, Myanmar, Thailand, Vietnam).

**Gotcha:** arrow has no `list_contains` for dplyr queries; `collect()` first and test
list membership with `purrr::map_lgl`.

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
    unnest(includes) |>  # id, name, type, status, joined, left, role, note
    filter(type == "country")
}
```

Prefer the pre-built edge table when you only need id / status / dates:

```r
memberships  # intblock_id, country_code, include_type, status, joined, left, role
```

**Gotcha:** the edge column is named `left` (departure date as a string). It is not a
reserved word, so bare `left` works in dplyr verbs; the backticks used below
(`` `left` ``) are optional.

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

**Expected:** 291 rows.

ASEAN roster:

```r
memberships |>
  filter(intblock_id == "ASEAN", status == "member") |>
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

**Expected:** 55 rows.

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

**Expected:** 129 rows.

### Child organizations of the UN

```r
intblocks |>
  collect() |>
  filter(map_lgl(partof, ~ "UN" %in% .x)) |>
  select(id, name, partof) |>
  arrange(name)
```

**Expected:** 46 rows.

### Multilingual intblock names

```r
intblocks |>
  select(id, name, other_names) |>
  collect() |>
  unnest(other_names, names_sep = "_") |>
  rename(translated_name = other_names_name, lang = other_names_id) |>
  filter(lang == "fr") |>
  select(id, name, translated_name, lang) |>
  arrange(id) |>
  slice_head(n = 20)
```

### Resolve intblock id aliases before join

```r
aliases <- read_parquet("data/datasets/intblocks_aliases.parquet")
# columns: alias, target, reason, since, note, target_dataset

stored <- tibble(id = c("USAN", "EU"))

stored |>
  left_join(
    aliases |> filter(reason != "disambiguated"),
    by = c("id" = "alias")
  ) |>
  transmute(stored_id = id, current_id = coalesce(target, id), target_dataset)
```

**Expected:** `USAN` → `UNASUR`, `EU` → `EU`. Do not follow `disambiguated` aliases
blindly: the old ID now names a different organization (`ASF` and `CAF` are live intblock
ids again). Aliases with `reason == "moved"` have `target_dataset == "trade_agreements"`:
the id now lives in the trade agreements registry, not in `intblocks`.

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
  filter(intblock_id == "UN", include_type == "country",
         status %in% c("member", "founding_member")) |>
  collect() |>
  nrow()
c(flag_n, roster_n)  # both 193
```

Without the status filter, the UN roster has 195 entries, including two observers.

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

**Expected:** 18 rows (`BEACST`, `CBSS`, `COE`, `CTBT`, `DANUBECOM`, `EASTERNBLOC`, `ECHR`, `ECPT`,
`ESCREVISED`, `FCNM`, `GRECO`, `ICES`, `ISTC`, `JCPOA`, `MONEYVAL`, `NSS`, `OPENSKY`, `RAMSAR`).

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

**Expected:** 5 rows (`COE`, `ECHR`, `ESCREVISED`, `ICES`, `MONEYVAL`).

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

Eurozone membership is tracked via the `EUROAREA` currency record (`EMU` is the World Bank
aggregate with the same roster):

```r
eu <- memberships |>
  filter(intblock_id == "EU") |>
  select(country_code) |>
  collect()

euroarea <- memberships |>
  filter(intblock_id == "EUROAREA") |>
  select(country_code) |>
  collect()

eu |>
  anti_join(euroarea, by = "country_code") |>
  inner_join(
    countries |> collect() |> select(code, name),
    by = c("country_code" = "code")
  ) |>
  select(country_code, name) |>
  arrange(country_code)
```

**Expected:** 6 rows (`CZ`, `DK`, `HU`, `PL`, `RO`, `SE`). Bulgaria joined the euro area on
1 January 2026.

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

**Expected:** 42 rows.

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
  left_join(intblocks |> select(id, description), by = "id") |>
  transmute(id, name, text = coalesce(description, "")) |>
  collect()
# Embed paste0(id, ": ", name, ". ", substr(text, 1, 500)) then retrieve; join full row on id.
```

Lite exports omit `description`; the join above hydrates it from the full table.

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
- [discovery.md](discovery.md) — how to search catalogues and improve records
- [intblock-sources.md](intblock-sources.md) — catalogues searched and roster authorities
- [getting-started.md](getting-started.md) — non-programmer path
- [llms.txt](../llms.txt) — compact index for LLM context windows
