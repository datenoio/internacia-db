# Entity classification policy

This document explains how Internacia classifies politically sensitive or non-standard
entities. It complements [country-code-policy.md](country-code-policy.md) and applies to
country records only — not intblock membership politics.

## Principles

1. **Reference data, not recognition judgments.** Fields describe how the entity is modeled
   for join resolution, not diplomatic recognition.
2. **Explicit over implicit.** Non-standard codes carry `code_status`, `entity_type`,
   `un_status`, and `independent` so consumers never infer from absence.
3. **Mechanical inclusion.** User-assigned country records exist when an intblock roster in
   this repository requires a join target.

## Edge cases

| Code | Entity | `entity_type` | Notes |
|------|--------|---------------|-------|
| `TW` | Taiwan | `dependent_territory` | Listed for geographic/reference joins; not a UN member (`un_status: non_member`). |
| `PS` | Palestine | `disputed_territory` | Observer state at UN; `capital_city` uses Ramallah (de facto administrative seat). |
| `XK` | Kosovo | `disputed_territory` | User-assigned `XK`/`XKX` (de facto EU/IMF/SWIFT standard); former `KV`/`KSV` in `countries_aliases.json`. |
| `EH` | Western Sahara | `disputed_territory` | Included where intblock rosters require it (e.g. African Union). |
| `VA` | Vatican City | `sovereign_state` | UN non-member observer; `independent: true`. |
| `CK` | Cook Islands | `dependent_territory` | Associated state of New Zealand; in free association, not UN member. |
| `NU` | Niue | `dependent_territory` | Same free-association status as Cook Islands. |
| `XA`–`XN` | CIS2 de facto states | `disputed_territory` / `historical_entity` | Present because `CIS2` roster references them; see CIS2 section in country-code-policy. |

## Consumer filters

**Official ISO countries only:**

```sql
SELECT * FROM countries WHERE code_status = 'official_iso3166_1';
```

**Exclude all user-assigned and obsolete codes:**

```sql
SELECT * FROM countries
WHERE code_status NOT IN ('obsolete', 'user_assigned');
```

**Remap legacy Kosovo code:**

```python
aliases = {a["alias"]: a["target"] for a in json.load(open("data/datasets/countries_aliases.json"))}
code = aliases.get("KV", "XK")  # KV → XK
```

## Related documents

- [country-code-policy.md](country-code-policy.md) — code status table and CIS2 build inclusion
- [ai-consumers.md](ai-consumers.md) — consumption contract and join keys
