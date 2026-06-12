## ADDED Requirements

### Requirement: Intblocks build manifest

Each successful intblocks dataset build SHALL write `data/datasets/intblocks.manifest.json` containing at minimum: `version`, `build_date` (ISO 8601), `git_commit` (short SHA or `unknown`), `row_count`, and `schema_hash`.

#### Scenario: Manifest written after build

- **WHEN** `scripts/builder.py` completes an intblocks export
- **THEN** `intblocks.manifest.json` exists with `row_count` matching the intblock source file count

#### Scenario: Schema hash changes on schema migration

- **WHEN** PyArrow schema for intblocks changes
- **THEN** `schema_hash` in the manifest differs from the previous build
