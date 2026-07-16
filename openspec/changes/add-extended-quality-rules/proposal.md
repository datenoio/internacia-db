# Change: Add extended data-quality rules (field validity, temporal consistency, reciprocity)

## Why

Several source fields are still unvalidated anywhere: countries' `tld`, `calling_codes`, `timezones`, `flag_emoji`, `landlocked`, `parent_entity`, and the continents↔subregion hierarchy; intblocks' `founding_members`, `includes[].joined`/`left` dates, `last_verified`, and acronym collisions. Coordinate plausibility is limited to range checks, which let swapped lat/lng pairs pass (found in EH and TF capitals). Organizational lineage (`predecessor`/`successor`, `suborganizations`↔`partof`) is resolved but never checked for reciprocity, and topic keys are only checked against the deprecation alias list, not a canonical catalog.

## What Changes

- Add country field-validity rules: `INVALID_TLD`, `INVALID_CALLING_CODE`, `INVALID_TIMEZONE` (IANA tz database), `FLAG_EMOJI_MISMATCH`, `LANDLOCKED_INCONSISTENCY`, `REGION_HIERARCHY_MISMATCH` (canonical continent→subregion table with allowlist), and `UNRESOLVED_PARENT_ENTITY`.
- Add geographic-plausibility rules: `CAPITAL_FAR_FROM_CENTROID` and `HQ_COORDINATES_OUTSIDE_COUNTRY`, using an area-scaled great-circle distance threshold to catch swapped/mis-signed coordinates that pass range checks.
- Add intblock temporal/membership rules: `INCLUDE_DATE_INCONSISTENCY` (unparseable/future dates, `left` before `joined`, dates after `dissolved`; `joined` before `founded` is deliberately excluded — ratification commonly precedes entry into force), `FOUNDING_MEMBER_NOT_INCLUDED`, `HISTORICAL_ENTITY_ACTIVE_MEMBER` (active-status include referencing a historical entity country), and `STALE_LAST_VERIFIED`.
- Add lineage reciprocity advisories: `SUCCESSOR_RECIPROCITY` (predecessor/successor pairs must point back) and `PARTOF_SUBORG_RECIPROCITY` (child listed in `suborganizations` must declare `partof`; the parent-side inverse is intentionally not required).
- Add `DUPLICATE_ACRONYM` advisory: unrelated records sharing an English acronym and a blocktype, with `references.acronym_duplicate_allowlist` for real-world collisions.
- Add `UNKNOWN_TOPIC_KEY` backed by a new canonical topic catalog `data/schemas/topics.yaml` (seeded from current usage), complementing the existing deprecated-key check.
- Add `MOJIBAKE_TEXT` guard for control characters and double-encoded UTF-8 in name/description fields of both datasets.
- Fix data errors surfaced while baselining (EH/TF capital coordinates) and populate new allowlists for documented exceptions.
- New rules launch at MEDIUM/LOW (warn) priority except `UNRESOLVED_PARENT_ENTITY`, which is referential integrity and reports as IMPORTANT.

## Impact

- Affected specs: `countries-data-quality`, `intblocks-data-quality`, `cross-dataset-integrity`
- Affected code: `internacia_builder/validate/country_rules.py`, `intblock_rules.py`, `cross_rules.py`, `countries.py`, `intblocks.py`, `internacia_builder/build.py` (wiring, priorities, descriptions), `data/schemas/countries_completeness.yaml`, `data/schemas/intblocks_completeness.yaml`, new `data/schemas/topics.yaml`, `tests/test_quality_rules.py`, `data/countries/EH.yaml`, `data/countries/TF.yaml`
- No export format changes; consumer-visible impact is limited to new issue types in `dataquality/` reports and CLI validator warnings (documented in `CHANGELOG.md`)
