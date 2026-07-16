# Change: Expand data quality rules and unify the checker layer

## Why

The quality analyzer (`analyze-quality`) and the CI validators (`internacia_builder/validate/`) have drifted: six rules run only in CI validation and never surface in `dataquality/` reports (currency codes, provenance freshness, centroid coordinates, filename↔id alignment, directory↔blocktype alignment, deprecated topic keys). Beyond that, whole classes of errors are not checked anywhere: `borders` entries are only format-checked and can reference non-existent countries, `predecessor`/`successor`/`suborganizations` references are never resolved, two records can silently share a `wikidata_id`, and intblock lifecycle dates are not checked for chronology.

## What Changes

- Consolidate rule implementations into a single shared checker layer used by both `analyze-quality` and the `validate_countries`/`validate_intblocks` CLIs, eliminating the duplicated logic in `internacia_builder/build.py`.
- Add cross-dataset referential integrity rules: border resolution and self-reference, border reciprocity advisory, intblock organizational reference resolution (`predecessor`, `successor`, `suborganizations`), headquarters country resolution, and `wikidata_id` uniqueness.
- Add intblock internal-consistency rules: duplicate `includes` entries, `membership_count` mismatch, `membership_applicability` contradiction, and founded/dissolved chronology (including `status: historical` without a `dissolved` date).
- Add country plausibility rules: indicator value ranges (`population`, `area`, `gini`) and entity flag consistency (`un_member`/`independent` vs `entity_type`).
- Surface the existing CI-only rules in `dataquality/` reports (report parity).
- Promote `scripts/report_country_include_names.py` to a LOW advisory rule and retire the standalone script.
- New rules launch at MEDIUM/LOW (warn) priority except referential integrity rules, which report as IMPORTANT.

## Impact

- Affected specs: `countries-data-quality`, `intblocks-data-quality`, `cross-dataset-integrity`
- Affected code: `internacia_builder/build.py` (checker functions extracted), `internacia_builder/validate/countries.py`, `internacia_builder/validate/intblocks.py`, new shared rules module, `data/schemas/countries_completeness.yaml`, `data/schemas/intblocks_completeness.yaml` (allowlists/thresholds for new rules), `tests/`, `scripts/report_country_include_names.py` (retired)
- No schema or export format changes; consumer-visible impact is limited to new issue types in `dataquality/` reports (documented in `CHANGELOG.md`)
