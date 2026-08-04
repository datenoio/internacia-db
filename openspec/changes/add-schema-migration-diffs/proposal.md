# Change: Generate machine-readable schema migration diffs per release

## Why
Consumers detect breaking changes via `schema_hash` in manifests but must manually read CHANGELOG. The deep review recommends `migration.vX.Y.Z.json` files with field-level diffs for programmatic SDK/API adaptation.

## What Changes
- Extend build/release pipeline to emit `data/datasets/migration.vX.Y.Z.json` when schema_hash changes.
- Include added, removed, renamed, and type-changed fields per dataset (countries, intblocks).
- Document consumption in `docs/ai-consumers.md`.

## Impact
- Affected specs: dataset-release
- Affected code: `internacia_builder/build.py`, release workflow, docs
