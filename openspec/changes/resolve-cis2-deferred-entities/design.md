## Context

CIS2 intblock membership includes four entities not present in the countries dataset. This was deferred during `add-countries-validation` with warn-only cross-reference checks. Consumers filtering on `code_status == official_iso3166_1` are unaffected today, but intblock-country joins on these ids fail silently.

## Goals / Non-Goals

- Goals:
  - Eliminate ambiguous warn-only behavior with an explicit documented policy.
  - Ensure cross-dataset validation reflects the chosen policy (pass, allowlist, or new records).
- Non-Goals:
  - Resolving all geopolitical recognition questions globally.
  - Changing unrelated intblock membership data.

## Decisions

### Decision: Option A — User-assigned country profiles (implemented)

Add four country YAML records with `code_status: user_assigned`, appropriate `entity_type` (`disputed_territory` for XA/XS/XT; `historical_entity` for XN), and `recognition_status` metadata. Cross-dataset validation resolves CIS2 includes without deferred warnings.

## Risks / Trade-offs

- Adding country records increases row count and may affect consumers expecting 252 records → document in CHANGELOG and manifest.
- Political sensitivity → use neutral metadata fields already in schema (`recognition_status`).

## Open Questions

- None for this change; Option A approved and applied.
