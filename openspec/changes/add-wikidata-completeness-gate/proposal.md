# Change: Wikidata completeness gate with verified exclusion list

## Why
~113 intblocks lack `wikidata_id`; ~90% are orgs with no Wikidata item (INTOSAI branches, ICAO RSOOs). Countries have 100% coverage. The deep review recommends a CI gate plus a verified exclusion list rather than blind failure or ignoring the gap.

## What Changes
- Maintain `data/schemas/wikidata_exclusions.yaml` (or JSON) listing intblock ids verified absent from Wikidata.
- Add CI rule: every intblock MUST have `wikidata_id` OR appear on the exclusion list with reason and verified_at.
- Run deferred backfill from `enrich-intblock-profile-depth` for fixable misses (e.g., ACAO Q22686285).
- Document exclusion policy in `docs/intblock-inclusion-policy.md` or enrichment docs.

## Impact
- Affected specs: intblocks-data-quality
- Affected code: `internacia_builder/validate/intblock_rules.py`, exclusion list file, enrichment scripts
