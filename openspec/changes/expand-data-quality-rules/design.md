## Context

Rule logic exists in two places: `internacia_builder/build.py` (feeds `analyze-quality` reports in `dataquality/`) and `internacia_builder/validate/` (feeds CI gates). The two copies have drifted, so the checked-in quality reports understate known issues. This change adds new rules and must not widen the drift, so consolidation comes first. The `refactor-builder-into-package` change (in flight) already moves builder code into the package; this change builds on that layout rather than duplicating it.

## Goals / Non-Goals

- Goals: one implementation per rule; new referential-integrity, consistency, and plausibility rules; parity between CI validation and `dataquality/` reports.
- Non-Goals: timezone-vs-IANA validation (requires vendoring tzdata for marginal benefit); description quality NLP beyond the existing boilerplate regex; any change to dataset schemas or export formats; network-dependent checks by default (`--check-http` / `--check-wikidata` stay opt-in).

## Decisions

- **Shared checker layer**: extract rule functions from `build.py` into the `internacia_builder/validate/` package (module per dataset plus a cross-dataset module). Each checker returns structured issue dicts (`issue_type`, `field`, `current_value`, `suggested_action`); `analyze-quality` attaches priorities via `ISSUE_PRIORITY_MAP`, the CLI validators map the same issues to errors/warnings. Alternative considered: keep two code paths and add rules to both — rejected as the root cause of the current drift.
- **Warn-first rollout**: new rules that depend on editorial judgment (reciprocity, entity flags, membership counts) start at MEDIUM/LOW and never fail CI initially. Referential-integrity rules (unresolved border/org/hq references, duplicate `wikidata_id`) report as IMPORTANT since they break joins.
- **Allowlists in completeness configs**: border reciprocity exceptions (territories administered separately) live in `countries_completeness.yaml`; the existing `special_entity_allowlist` mechanism is reused for headquarters-country resolution.
- **Baseline before enforcement**: after implementation, run the analyzer on the full dataset and tune suppressions (as was done for `DUPLICATE_LINK`) before any rule graduates to a CI-failing mode.

## Risks / Trade-offs

- Refactor touches ~700 lines of `build.py` → mitigate with the existing test suite plus a before/after diff of `full_report.jsonl` on the current dataset (must be identical for pre-existing rules).
- New rules may produce noisy first runs (border reciprocity especially) → warn-first rollout plus allowlists; triage the baseline before merging report updates.

## Migration Plan

1. Extract shared checkers with unchanged behavior; verify report parity for existing rules.
2. Add new rules behind the shared layer with tests.
3. Regenerate `dataquality/`, triage the baseline, tune allowlists.
4. Retire `scripts/report_country_include_names.py` once `INCLUDE_NAME_MISMATCH` ships.

Rollback: the change is additive to reports; reverting the rules module entries restores prior report content.

## Open Questions

- Should `MEMBERSHIP_COUNT_MISMATCH` compare against all `includes` entries or only member-class statuses (`member`, `founding_member`)? Baseline data will inform the tolerance.
