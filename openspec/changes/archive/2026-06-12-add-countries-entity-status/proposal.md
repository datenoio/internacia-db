# Change: Add countries entity status modeling

## Why

The dataset includes three codes outside the current ISO 3166-1 set (`AN`, `JG`, `KV`) without explicit status metadata. Consumers cannot filter "current ISO countries" vs historical, user-assigned, or collective entities. Four intblock references (`XA`, `XS`, `XT`, `XN`) use `type: country` but have no country profiles—policy for these is **deferred** and documented only.

Depends on **fill-countries-core-fields**.

See [dev/research/countries_gaps_,manus_20260528.md](../../../dev/research/countries_gaps_,manus_20260528.md).

## What Changes

- Add `entity_type` and `code_status` enums to country YAML schema, JSON Schema, and PyArrow.
- Annotate `AN`, `JG`, `KV` per audit recommendations.
- Add optional `recognition_status` and `parent_entity` for dependent/disputed cases.
- Add `docs/country-code-policy.md`.
- Builder validation: any non-`official_iso3166_1` code MUST have `code_status` set.
- Update `cross-dataset-integrity` allowlist semantics (still warn-only for deferred `XA`–`XN`).

## Impact

- Affected specs: `countries-entity-model`, `cross-dataset-integrity` (modified)
- Affected code: `data/countries/AN.yaml`, `JG.yaml`, `KV.yaml`, schemas, builder, docs
- Breaking: None for existing `code` values; additive fields
