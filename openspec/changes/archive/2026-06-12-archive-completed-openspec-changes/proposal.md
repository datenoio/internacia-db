# Change: Archive completed countries OpenSpec changes

## Why

Four countries-domain changes (`add-countries-validation`, `fill-countries-core-fields`, `add-countries-entity-status`, `add-countries-release-governance`) are implemented and marked complete but remain in `openspec/changes/`. Canonical specs in `openspec/specs/` are empty, causing spec drift.

See [docs/improvement-plan.md](../../../docs/improvement-plan.md) §4.1.

## What Changes

- Archive all four completed changes to `openspec/changes/archive/YYYY-MM-DD-<change-id>/`.
- Promote spec deltas to `openspec/specs/{capability}/spec.md` as canonical truth.
- Run `openspec validate --strict` after archival.
- Update improvement plan review log.

## Impact

- Affected specs: all countries capabilities promoted to `openspec/specs/`
- Affected code: `openspec/` directory only
- Breaking: None (governance only)
