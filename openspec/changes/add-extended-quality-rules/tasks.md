## 1. Country field-validity rules

- [x] 1.1 `INVALID_TLD`: `tld` must match `.xx`-style lowercase format
- [x] 1.2 `INVALID_CALLING_CODE`: `calling_codes` entries must match `+digits`
- [x] 1.3 `INVALID_TIMEZONE`: `timezones` entries must exist in the IANA tz database (skipped when the database is unavailable)
- [x] 1.4 `FLAG_EMOJI_MISMATCH`: `flag_emoji` must equal the regional-indicator pair derived from `code` (official ISO codes only)
- [x] 1.5 `LANDLOCKED_INCONSISTENCY`: `landlocked: true` requires a non-empty `borders` list
- [x] 1.6 `REGION_HIERARCHY_MISMATCH`: `subregion` must belong to one of the record's `continents` per the canonical table, with `region_hierarchy.allowlist` in `countries_completeness.yaml`
- [x] 1.7 `UNRESOLVED_PARENT_ENTITY`: `parent_entity.code` must resolve to an existing country record

## 2. Geographic plausibility rules

- [x] 2.1 `CAPITAL_FAR_FROM_CENTROID`: area-scaled great-circle threshold with `geography.capital_distance` config (min_km, area_multiplier, allowlist)
- [x] 2.2 `HQ_COORDINATES_OUTSIDE_COUNTRY`: same threshold model for `headquarters.coordinates` vs the HQ country's centroid
- [x] 2.3 Fix the swapped/incorrect capital coordinates surfaced by baselining (`EH`, `TF`); allowlist legitimate outliers (`UM`, `PF`)

## 3. Intblock temporal and membership rules

- [x] 3.1 `INCLUDE_DATE_INCONSISTENCY`: unparseable/future `joined`/`left`, `left` before `joined`, dates after `dissolved` (precision-aware; `joined` before `founded` deliberately excluded)
- [x] 3.2 `FOUNDING_MEMBER_NOT_INCLUDED`: `founding_members` entries must resolve to country codes and appear in `includes`
- [x] 3.3 `HISTORICAL_ENTITY_ACTIVE_MEMBER`: active-status include referencing a country with `entity_type: historical_entity`
- [x] 3.4 `STALE_LAST_VERIFIED`: `last_verified` older than `quality.last_verified_max_age_months`

## 4. Lineage, naming, and text rules

- [x] 4.1 `SUCCESSOR_RECIPROCITY`: resolved `predecessor`/`successor` pairs must point back at each other; fix the six existing lineage gaps (G7/G8, GATT/WTO, ICSU/ISC, NORDEL/ENTSOE, IPEEC/EEHUB)
- [x] 4.2 `PARTOF_SUBORG_RECIPROCITY`: a child listed in `suborganizations` must declare the parent in `partof` (parent-side inverse not required)
- [x] 4.3 `DUPLICATE_ACRONYM`: unrelated records sharing an English acronym and a blocktype, with `references.acronym_duplicate_allowlist`
- [x] 4.4 `UNKNOWN_TOPIC_KEY`: topic keys must exist in the new canonical catalog `data/schemas/topics.yaml` (seeded from current usage)
- [x] 4.5 `MOJIBAKE_TEXT`: control characters, U+FFFD, and double-encoded UTF-8 markers in name/description fields of both datasets

## 5. Wiring, tests, and baseline

- [x] 5.1 Register all new issue types in `ISSUE_PRIORITY_MAP` and `RULE_DESCRIPTIONS`; wire checkers into `analyze_quality` and the `validate_countries`/`validate_intblocks` CLIs (warn tier)
- [x] 5.2 Add config keys and allowlists to `countries_completeness.yaml` and `intblocks_completeness.yaml`
- [x] 5.3 Unit tests for each rule in `tests/test_quality_rules.py`; `pytest` and `ruff check` pass
- [x] 5.4 Run `analyze-quality`, triage counts, regenerate `dataquality/` reports
- [x] 5.5 Update `CHANGELOG.md` under `[Unreleased]`
