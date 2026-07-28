## 1. Consolidate the checker layer

- [x] 1.1 Extract country rule functions from `internacia_builder/build.py` into the `internacia_builder/validate/` package (shared with `validate_countries` CLI), returning structured issue dicts
- [x] 1.2 Extract intblock and cross-dataset rule functions the same way (shared with `validate_intblocks` CLI)
- [x] 1.3 Point `analyze_quality` at the shared checkers; delete the duplicated implementations in `build.py`
- [x] 1.4 Verify parity: `full_report.jsonl` before and after the refactor is identical for existing rules on the current dataset; `pytest tests/` and `ruff check` pass

## 2. Report parity for existing CI-only rules

- [x] 2.1 Surface `INVALID_CURRENCY_CODE`, `INVALID_COORDINATES` (centroid + `capital_city`), `STALE_PROVENANCE`, and countries `FILENAME_ID_MISMATCH` in `analyze-quality`
- [x] 2.2 Surface intblock `FILENAME_ID_MISMATCH`, `DIRECTORY_BLOCKTYPE_MISMATCH`, and `DEPRECATED_TOPIC_KEY` in `analyze-quality`
- [x] 2.3 Register all new issue types in `ISSUE_PRIORITY_MAP` and `RULE_DESCRIPTIONS`

## 3. New referential integrity rules (IMPORTANT)

- [x] 3.1 `UNRESOLVED_BORDER_REFERENCE`: borders resolve to existing `iso3code`, no self-reference
- [x] 3.2 `UNRESOLVED_ORG_REF`: `predecessor`/`successor`/`suborganizations[].id` resolve to intblock ids or aliases
- [x] 3.3 `UNRESOLVED_HQ_COUNTRY`: `headquarters.country` resolves to a country file or `special_entity_allowlist`
- [x] 3.4 `DUPLICATE_WIKIDATA_ID`: Q-id uniqueness across countries and intblocks
- [x] 3.5 Unit tests for each rule following the `tests/test_cross_dataset.py` pattern

## 4. New consistency and plausibility rules (MEDIUM/LOW)

- [x] 4.1 `DUPLICATE_INCLUDE_ENTRY`, `MEMBERSHIP_COUNT_MISMATCH` (tolerance in `intblocks_completeness.yaml`), `CONTRADICTORY_APPLICABILITY`
- [x] 4.2 `CHRONOLOGY_ERROR` and extended `LIFECYCLE_INCONSISTENCY` (historical without dissolved)
- [x] 4.3 `INVALID_INDICATOR_VALUE` (population/area/gini ranges, future years) and `INCONSISTENT_ENTITY_FLAGS`
- [x] 4.4 `NONRECIPROCAL_BORDER` with reciprocity allowlist in `countries_completeness.yaml`
- [x] 4.5 `PROVENANCE_INTEGRITY` (unknown field references, invalid/future `retrieved_at`) for both datasets
- [x] 4.6 `INCLUDE_NAME_MISMATCH` advisory rule; retire `scripts/report_country_include_names.py`
- [x] 4.7 Unit tests for each rule

## 5. Baseline, tune, and document

- [x] 5.1 Run `analyze-quality` on the full dataset; triage new issue counts and populate allowlists for legitimate exceptions
- [x] 5.2 Regenerate `dataquality/` reports and commit the new baseline
- [x] 5.3 Update `CONTRIBUTING.md`, `.cursor/skills/internacia-contribute/SKILL.md`, and `CHANGELOG.md` under `[Unreleased]`
- [x] 5.4 Confirm `.github/workflows/validate.yml` exercises the shared checker layer; new rules stay warn-tier (no CI failures) pending baseline review
