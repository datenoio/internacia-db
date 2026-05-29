# Country code and entity status policy

This document describes how `internacia-db` treats country codes, entity classification, and non-standard records. It aligns with the 2026-05-28 countries gap audit.

## Scope

The countries dataset includes **252** records: **249** with current ISO 3166-1-style alpha-2 codes plus **3** non-standard entries (`AN`, `JG`, `KV`) retained with explicit status metadata.

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

**Exclude obsolete and user-assigned:**

```python
df[~df["code_status"].isin(["obsolete", "user_assigned"])]
```

## UN M49 disclaimer

UN M49 regional groupings in `region` and `subregion` are for **statistical convenience** and do not imply political affiliation or recognition status.

## Deferred: CIS2 special entities

Four intblock references in `data/intblocks/political/CIS2.yaml` use `type: country` for codes **`XA`**, **`XS`**, **`XT`**, **`XN`** (Abkhazia, South Ossetia, Transnistria, Artsakh). These are **not** in the countries dataset. Policy options (not yet implemented):

1. Add special-status country profiles with `code_status: user_assigned`
2. Reclassify intblock includes to `disputed_entity`
3. Allowlist without profiles until a policy decision is made

Validation currently emits **warnings** for these unresolved references.

## Borders convention

The `borders` field stores **ISO 3166-1 alpha-3** land-border neighbor codes, not alpha-2.

## Related tools

- `scripts/annotate_entity_status.py` — apply or refresh entity annotations
- `scripts/validate_countries.py` — schema and policy validation at build time
