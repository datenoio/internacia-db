# Change: Add scheduled link and Wikidata validation

## Why

`scripts/validate_links.py` checks intblock URL accessibility and Wikidata entity consistency but runs manually only—excluded from PR CI due to network dependency. Link rot and Wikidata drift accumulate without periodic checks.

See [docs/improvement-plan.md](../../../docs/improvement-plan.md) §1.6.

## What Changes

- Add `.github/workflows/validate-links-scheduled.yml` running weekly on `main` (cron).
- Upload validation report as workflow artifact; non-blocking for merges.
- Optionally require clean link report before semver tag (coordinate with `add-github-release-workflow`).
- Document manual run and scheduled cadence in README and CONTRIBUTING.

## Impact

- Affected specs: `intblocks-data-quality` (modified)
- Affected code: `.github/workflows/`, `scripts/validate_links.py` (report output improvements), documentation
- Breaking: None
