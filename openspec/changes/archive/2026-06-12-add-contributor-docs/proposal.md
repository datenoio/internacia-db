# Change: Add contributor documentation and README fixes

## Why

Documentation has known inconsistencies: README filename typo, missing scripts in the table, promised CI badges absent, no `CONTRIBUTING.md`, and stale counts in `openspec/project.md`. Phase 0 quick wins from the improvement plan.

See [docs/improvement-plan.md](../../../docs/improvement-plan.md) §4.2.

## What Changes

- Add `CONTRIBUTING.md` with YAML authoring guide, validation workflow, and PR checklist.
- Fix README typo (`countries_gaps_,manus_20260528.md`), add missing scripts, add CI status badge.
- Update `openspec/project.md` intblocks count (1,065) and testing strategy section.
- Clarify or document `data/_legacy/` purpose in README or remove if unused.
- Link improvement plan and OpenSpec workflow from CONTRIBUTING.

## Impact

- Affected specs: `contributor-docs` (new)
- Affected code: `README.md`, `CONTRIBUTING.md`, `openspec/project.md`, optionally `data/_legacy/`
- Breaking: None
