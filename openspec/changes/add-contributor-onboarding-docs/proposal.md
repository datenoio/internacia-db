# Change: Add contributor onboarding docs and community templates

## Why
The deep review and implementation plan Phase 3 identify missing data dictionary, GitHub issue templates, getting-started guide, architecture diagram, and README indexes for `dev/research/` and `dev/scripts/`. These are docs-only but cross-cut multiple contributor-facing capabilities.

## What Changes
- Add generated `docs/data-dictionary.md` from JSON Schemas (with generator script).
- Add `.github/ISSUE_TEMPLATE/` for data errors, data requests, and code bugs.
- Add `docs/getting-started.md` for non-programmers.
- Add Mermaid architecture diagram in README or `docs/architecture.md`.
- Add `dev/research/README.md` and `dev/scripts/README.md`; label `data/_legacy/`.

## Impact
- Affected specs: contributor-docs
- Affected code: `docs/`, `.github/ISSUE_TEMPLATE/`, `dev/`, README, optional script under `scripts/` or `internacia_builder/`
