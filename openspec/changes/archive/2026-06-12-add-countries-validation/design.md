## Context

Audit of `countries.parquet` (2026-05-28) found structural completeness but critical content gaps. The repository already has JSON Schema for a core country subset and PyArrow schema in the builder, but they are not enforced at build time. International blocks reference four country IDs (`XA`, `XS`, `XT`, `XN`) absent from the countries dataset.

## Goals / Non-Goals

- Goals:
  - Fail builds on schema violations, malformed ISO identifiers, and duplicate codes.
  - Normalize categorical strings (strip trailing whitespace) during build.
  - Establish configurable completeness thresholds with warn-then-error rollout.
  - Clarify and document `borders` identifier semantics.
- Non-Goals:
  - Populating empty profile fields (Change 2: `fill-countries-core-fields`).
  - Entity status modeling for `AN`, `JG`, `KV` (Change 3).
  - Resolving CIS2 disputed-entity references (deferred).

## Decisions

### Decision: Border identifier contract

Keep YAML field name `borders` storing **ISO 3166-1 alpha-3** codes (current data: 644 references such as `CAN`, `MEX`). Document explicitly in README and JSON Schema as land-border neighbors in alpha-3 form. Do **not** rename the field in this change to avoid a breaking YAML migration; add schema `description` noting the alpha-3 convention.

Future optional addition: `borders_alpha2` parallel list in a later change if consumers require alpha-2 joins without lookup.

**Alternatives considered:**
- Migrate `borders` to alpha-2: breaks no consumers of parquet if we dual-write, but requires regenerating all 252 YAML files.
- Rename to `border_iso3codes`: clearer but breaking for YAML consumers.

### Decision: Completeness gate rollout

`countries_completeness.yaml` lists advertised fields with `mode: warn | error` and `max_null_rate`.

For Change 1, the five 100%-empty fields (`population`, `area`, `gini`, `timezones`, `native_names`) use `mode: warn`. Change 2 switches them to `mode: error` after backfill.

### Decision: CIS2 special entities (deferred)

`XA`, `XS`, `XT`, `XN` in `data/intblocks/political/CIS2.yaml` are validated as **warn-only** unresolved references. `special_entity_allowlist` in completeness config starts empty. Policy decision deferred to Change 3 design discussion.

## Risks / Trade-offs

- Warn-mode completeness may allow releases with empty critical fields → mitigated by explicit CHANGELOG note and Change 2 dependency.
- Cross-dataset warnings on CIS2 may be noisy → single aggregated warning in validator output.

## Migration Plan

1. Ship validator in warn mode; fix any schema violations discovered in existing YAML.
2. Enable builder integration (non-zero exit on schema/identifier errors only).
3. Change 2 enables error mode for profile fields after enrichment.

## Open Questions

- Should we add `borders_alpha2` in Change 2 or Change 4? (Leaning: only if a consumer requests it.)
- Final policy for `XA`/`XS`/`XT`/`XN`: add profiles vs reclassify intblock `type` (deferred).
