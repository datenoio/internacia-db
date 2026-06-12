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

### Decision: Policy options (choose one at implementation)

**Option A — User-assigned country profiles:** Add four country YAML records with `code_status: user_assigned`, `entity_type: disputed_territory`, and `recognition_status` metadata.

**Option B — Typed includes:** Change CIS2 includes to a non-country type (e.g. `disputed_territory`) with documented allowlist; validators accept allowlisted ids without country files.

**Option C — Permanent deferred allowlist:** Keep no country files; add explicit allowlist in completeness config with documented permanent deferral.

**Recommendation:** Option A or B for explicit consumer join paths.

## Risks / Trade-offs

- Adding country records increases row count and may affect consumers expecting 252 records → document in CHANGELOG and manifest.
- Political sensitivity → use neutral metadata fields already in schema (`recognition_status`).

## Open Questions

- Which option do Dateno / internacia-api consumers prefer for join behavior?
