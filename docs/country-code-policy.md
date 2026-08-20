# Country code and entity status policy

This document describes how `internacia-db` treats country codes, entity classification, and non-standard records. It aligns with the 2026-05-28 countries gap audit.

## Scope

The countries dataset includes **256** records: **249** with current ISO 3166-1-style alpha-2 codes plus **7** non-standard entries retained with explicit status metadata.

## Code status (`code_status`)

| Value | Meaning |
|-------|---------|
| `official_iso3166_1` | Current ISO 3166-1 alpha-2 assignment |
| `user_assigned` | Repository or community code, not ISO official |
| `obsolete` | Former ISO code, retained for historical reference |
| `exceptionally_reserved` | ISO exceptionally reserved element |

### Non-standard records

| Code | Name | `code_status` | Notes |
|------|------|---------------|-------|
| `AN` | Netherlands Antilles | `obsolete` | Dissolved; successors include `CW`, `SX`, `BQ` |
| `JG` | Channel Islands | `user_assigned` | Collective grouping; **`GG` (Guernsey) and `JE` (Jersey) are canonical territory codes** for constituents |
| `XK` | Kosovo | `user_assigned` | De facto standard (EU, IMF, SWIFT, CLDR); not ISO 3166-1 official. Former codes `KV`/`KSV` in `countries_aliases.json` |
| `XA` | Abkhazia | `user_assigned` | CIS2 membership reference; `entity_type: disputed_territory` |
| `XS` | South Ossetia | `user_assigned` | CIS2 membership reference; `entity_type: disputed_territory` |
| `XT` | Transnistria | `user_assigned` | CIS2 membership reference; `entity_type: disputed_territory` |
| `XN` | Artsakh | `user_assigned` | CIS2 historical reference; `entity_type: historical_entity` (dissolved 2023) |

All seven non-standard records carry **explicit** `un_member`, `un_status`, `independent`, and
`landlocked` values so that consumers never need to interpret a missing field.

### Disputed-territory inclusion rule

User-assigned records for de facto states exist **only where an intblock in this repository
references the entity as a member** and a join target is therefore required (currently
CIS2 references to `XA`, `XS`, `XT`, `XN`, and Kosovo (`XK`, formerly `KV`)). De facto
states that no intblock references — for example **Somaliland** and **Northern Cyprus** — do
not receive records, regardless of their degree of de facto autonomy. If a future intblock
addition references such an entity, a user-assigned record (e.g. `XL`, `XC`) is added in the
same change. This rule is deliberately mechanical: inclusion signals join-resolution need,
not any position on recognition.

### `JG` aggregation warning

`JG` (Channel Islands) is a **collective grouping** whose World Bank population figure is not
the exact sum of `GG` (Guernsey) and `JE` (Jersey), which are sourced separately. Consumers
summing populations over all records will **double-count** the Channel Islands if they
include `JG` together with `GG`/`JE` — include either the grouping or the constituents,
never both.

### Exceptionally reserved codes

ISO 3166-1 exceptionally reserved elements (`EU`, `EZ`, `UN`, etc.) are **not** country
records in this dataset. The European Union appears as the intblock `economic/EU.yaml`;
join organization-level references there instead.

## Entity type (`entity_type`)

| Value | Typical use |
|-------|-------------|
| `sovereign_state` | Independent states |
| `dependent_territory` | Non-sovereign territories and dependencies |
| `special_administrative_region` | e.g. Hong Kong (`HK`), Macao (`MO`) |
| `disputed_territory` | Partially recognized or disputed areas |
| `historical_entity` | Dissolved political entities |
| `supranational_grouping` | Collective groupings, not a single territory |
| `statistical_area` | Statistical or M49-only areas |

## Display names

`name` follows **World Bank short-name style** (for example `Egypt, Arab Rep.`). It can
lag official English short-form changes (North Macedonia, Eswatini, Cabo Verde, Türkiye).
Put the modern short form in `common_names` and translations in `other_names`. Use
`official_name` for the formal long form. Do not "correct" `name` to a journalist-style
label without a sourced World Bank (or documented alternative) update.

## `parent_entity`

The schema allows `parent_entity: {code, name}` for dependent territories and SARs
(for example GL→DK, PR→US, HK/MO→CN). It is **optional and currently unused** (zero
records). Populate it only when the administering state is unambiguous and sourced;
do not invent a parent for disputed territories. Absence is not a validation error.

## Filtering examples

**Current ISO countries only** (249 records):

```python
df[df["code_status"] == "official_iso3166_1"]
```

**DuckDB equivalent:**

```sql
SELECT code, name FROM countries WHERE code_status = 'official_iso3166_1';
```

**Exclude obsolete and user-assigned:**

```python
df[~df["code_status"].isin(["obsolete", "user_assigned"])]
```

**DuckDB equivalent:**

```sql
SELECT code, name FROM countries
WHERE code_status NOT IN ('obsolete', 'user_assigned');
```

For UN members, border neighbors, and intblock membership joins, see
[query-examples.md](query-examples.md).

## UN M49 disclaimer

UN M49 regional groupings in `region` and `subregion` are for **statistical convenience** and do not imply political affiliation or recognition status.

## CIS2 special entities

Four intblock references in `data/intblocks/political/CIS2.yaml` use `type: country` for codes **`XA`**, **`XS`**, **`XT`**, **`XN`** (Abkhazia, South Ossetia, Transnistria, Artsakh). These have **user-assigned** country profiles in the dataset for cross-dataset join resolution.

Consumers excluding non-standard codes:

```python
df[~df["code"].isin(["AN", "JG", "XK", "XA", "XS", "XT", "XN"])]
```

Or filter on `code_status == "official_iso3166_1"` for the 249 ISO records only.

## Country code aliases

Retired or renamed country codes are mapped in `data/datasets/countries_aliases.json`
(source: `data/countries_aliases.yaml`). When upgrading across releases, remap legacy
codes before joining on `countries.code`:

```python
aliases = {a["alias"]: a["target"] for a in json.load(open("data/datasets/countries_aliases.json"))}
code = aliases.get(raw_code, raw_code)
```

Current entries: `KV` → `XK`, `KSV` → `XKX` (Unreleased).

Entity classification edge cases (Taiwan, Palestine, Kosovo, Western Sahara, etc.) are
documented in [entity-classification-policy.md](entity-classification-policy.md).

## Borders convention

The `borders` field stores **ISO 3166-1 alpha-3** land-border neighbor codes, not alpha-2.

## Capital city exclusions

Most entities populate `capital_city` (name + coordinates) with a `provenance`
entry; de-facto seats of government are used where no formally recognized capital
exists (e.g. `IL` Jerusalem, `PS` Ramallah, `TW` Taipei, `HK`/`MO` administrative
seats, and the disputed `XA`/`XS`/`XT` capitals). The following entities have **no
capital by design** and are expected exclusions rather than data gaps:

- `AQ` Antarctica, `BV` Bouvet Island, `HM` Heard Island and McDonald Islands — uninhabited territories.
- `JG` Channel Islands — a grouping (Jersey and Guernsey are separate entities), not a single administrative unit.
- `XN` Artsakh — historical entity dissolved in 2023; retained for join resolution only.

## World Bank classification gaps

World Bank `region`, `incomeLevel`, and `lendingType` are absent for 8 entities (overseas territories, special statistical areas, and non-standard codes) because the World Bank does not classify them. `adminregion` is absent for 39 entities — by World Bank convention it only covers low- and middle-income economies, so its absence for high-income economies (US, GB, DE, …) is expected, not a gap.

For these records, enrichment MAY source regional classifications from **UN M49** with provenance documenting the alternative authority. Expected absences for uninhabited territories and special entities should not fail validation when documented in the record's provenance.

## Related tools

- `scripts/annotate_entity_status.py` — apply or refresh entity annotations
- `scripts/validate_countries.py` — schema and policy validation at build time
