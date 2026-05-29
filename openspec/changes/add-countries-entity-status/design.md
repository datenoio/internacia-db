## Context

Audit found 249 current ISO-style alpha-2 codes plus three extra records. CIS2 intblock lists four user-assigned codes as `type: country` without matching country YAML files.

## Goals / Non-Goals

- Goals:
  - Explicit machine-readable status for `AN`, `JG`, `KV`.
  - Document policy for ISO vs user-assigned vs obsolete codes.
  - Enforce `code_status` on non-standard codes at build time.
- Non-Goals:
  - Adding `XA`, `XS`, `XT`, `XN` country profiles (**deferred**).
  - Reclassifying CIS2 includes (deferred).
  - Removing `AN`, `JG`, or `KV` from the dataset.

## Decisions

### Decision: Enum values

**`entity_type`:** `sovereign_state`, `dependent_territory`, `special_administrative_region`, `disputed_territory`, `historical_entity`, `supranational_grouping`, `statistical_area`

**`code_status`:** `official_iso3166_1`, `user_assigned`, `obsolete`, `exceptionally_reserved`

Default for standard ISO entries: `entity_type: sovereign_state` or `dependent_territory` as appropriate; `code_status: official_iso3166_1`.

### Decision: Record-specific policy

| Code | entity_type | code_status | Notes |
|------|-------------|-------------|-------|
| AN | historical_entity | obsolete | Netherlands Antilles dissolved; successors CW, SX, BQ |
| JG | supranational_grouping | user_assigned | Channel Islands collective; GG and JE are canonical territories |
| KV | disputed_territory | user_assigned | Kosovo; `recognition_status: disputed_or_partially_recognized` |

### Decision: Deferred CIS2 entities

Options documented but **not implemented** in this change:

1. Add `data/countries/XA.yaml` etc. with `code_status: user_assigned`.
2. Change CIS2 `includes[].type` to `disputed_entity`.
3. Add `special_entity_allowlist` entries without profiles.

Until decided, validator continues warn-only for `XA`, `XS`, `XT`, `XN`.

## Risks / Trade-offs

- Filtering by `code_status` changes effective row counts for consumers expecting 252 → document 249 "current ISO" filter.
- Political sensitivity on `KV` and deferred entities → neutral metadata only, cite sources in policy doc.

## Open Questions

- Should `JG` remain a country row or move to a separate groupings dataset?
- Final resolution for CIS2 members (deferred).
- ISO 3166-3 formal linkage for `AN` (future enhancement).
