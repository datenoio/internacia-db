# Change: Consolidate intblock topic taxonomy

## Why

The Manus data-quality report (`dev/research/report_manus_20260615.md`) found 177 unique topic keys with significant synonym fragmentation (11 redundant groups), 19 sport-specific keys for a single domain, and 69 records (6.5%) with no topics assigned. Inconsistent topics undermine filtering, analytics, and cross-record comparison.

## What Changes

- Consolidate the 11 synonym groups identified in the report into canonical keys (e.g. `climate_change`, `arms_control`, `economy`, `law`, `transport`, `humanitarian`).
- Restructure sports-related topics under `sports` (and `sports_governance` for governing bodies).
- Assign at least one topic to all 69 records currently lacking topics (including all 21 `acronym` records).
- Document a formal governance process for adding, merging, and deprecating topic keys in CONTRIBUTING or `docs/topic-taxonomy.md`.
- Add validator rules (warn mode initially) for deprecated topic keys and records with empty `topics`.

## Impact

- Affected specs: `intblocks-data-quality` (modified)
- Affected code: `data/intblocks/**/*.yaml`, `scripts/validate_intblocks.py`, contributor docs
- Breaking: Topic key renames affect consumers filtering on legacy keys; document migration in CHANGELOG
