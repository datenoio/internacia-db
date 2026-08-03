# Change: Disambiguate membership_count semantics with a unit qualifier

## Why
A programmatic scan (2026-08-02) found 204 of 1,054 intblock records where `membership_count` disagrees with the `includes` roster length. Two distinct causes are conflated: genuine drift (stale counts, incomplete rosters such as `AIIB` 111 vs 35), and records where the count intentionally measures something other than country members — companies (`WNA` ≈ 3,000), individuals (`IGA` ≈ 10,000), standards bodies (`ETSI` ≈ 900), corporate members (`WEF` ≈ 1,000). Consumers cannot tell which unit a count is in, and the existing `MEMBERSHIP_COUNT_MISMATCH` rule cannot distinguish legitimate non-country counts from drift.

## What Changes
- Add an optional `membership_count_type` field to `data/schemas/intblocks.schema.json` (enum: `countries`, `organizations`, `companies`, `individuals`, `mixed`; default semantics when absent: `countries`).
- Set `membership_count_type` on records whose count is not a country-member roster count (WNA, IGA, ETSI, WEF, and peers found by the scan).
- Tighten the `MEMBERSHIP_COUNT_MISMATCH` rule: when `membership_count_type` is absent or `countries`, the count MUST match the current-member roster within the configured tolerance; records with a non-country type are exempt from roster comparison but MUST have a provenance entry for the count.
- Reconcile the remaining genuine-drift records surfaced by the scan (fix count or roster).
- Document the qualifier in `docs/ai-consumers.md` and the schema.

## Impact
- Affected specs: intblocks-data-quality
- Affected code: `data/schemas/intblocks.schema.json`, `internacia_builder/validate/intblock_rules.py`, `data/schemas/intblocks_completeness.yaml`, affected `data/intblocks/**/*.yaml`, `docs/ai-consumers.md`
