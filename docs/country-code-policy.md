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
| `KV` | Kosovo | `user_assigned` | Commonly used code; not ISO 3166-1 official |
| `XA` | Abkhazia | `user_assigned` | CIS2 membership reference; `entity_type: disputed_territory` |
| `XS` | South Ossetia | `user_assigned` | CIS2 membership reference; `entity_type: disputed_territory` |
| `XT` | Transnistria | `user_assigned` | CIS2 membership reference; `entity_type: disputed_territory` |
| `XN` | Artsakh | `user_assigned` | CIS2 historical reference; `entity_type: historical_entity` (dissolved 2023) |

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
df[~df["code"].isin(["AN", "JG", "KV", "XA", "XS", "XT", "XN"])]
```

Or filter on `code_status == "official_iso3166_1"` for the 249 ISO records only.

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

World Bank `region`, `incomeLevel`, and `lendingType` are absent for ~33 entities (high-income OECD members, overseas territories, and special statistical areas) because the World Bank does not classify them. `adminregion` may also be missing for high-income economies outside the Bank's administrative taxonomy.

For these records, enrichment MAY source regional classifications from **UN M49** with provenance documenting the alternative authority. Expected absences for uninhabited territories and special entities should not fail validation when documented in the record's provenance.

## Related tools

- `scripts/annotate_entity_status.py` — apply or refresh entity annotations
- `scripts/validate_countries.py` — schema and policy validation at build time
