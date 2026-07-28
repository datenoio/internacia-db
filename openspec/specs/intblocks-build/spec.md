# intblocks-build Specification

## Purpose
TBD - created by archiving change add-intblocks-validation. Update Purpose after archive.
## Requirements
### Requirement: Intblocks validation before export

The dataset builder SHALL run intblock validation before writing intblocks derived artifacts. Intblock validation logic SHALL be covered by automated tests.

#### Scenario: Build fails on intblock schema error

- **WHEN** `scripts/builder.py build` runs and an intblock YAML file fails schema validation
- **THEN** the build exits with non-zero status and does not overwrite intblocks outputs

#### Scenario: Build succeeds when intblocks valid

- **WHEN** all intblock YAML files pass validation
- **THEN** the build proceeds to export intblocks artifacts

#### Scenario: Intblock validator covered by tests

- **WHEN** `validate_intblocks.py` exists
- **THEN** pytest includes tests for schema pass/fail and duplicate id detection

### Requirement: Intblocks build manifest

Each successful intblocks dataset build SHALL write `data/datasets/intblocks.manifest.json` containing at minimum: `version`, `build_date` (ISO 8601), `git_commit` (short SHA or `unknown`), `row_count`, and `schema_hash`.

#### Scenario: Manifest written after build

- **WHEN** `scripts/builder.py` completes an intblocks export
- **THEN** `intblocks.manifest.json` exists with `row_count` matching the number of intblock source files

#### Scenario: Schema hash changes on schema migration

- **WHEN** PyArrow schema for intblocks changes
- **THEN** `schema_hash` in the manifest differs from the previous build

### Requirement: Intblock filename matches id

Each intblock YAML file SHALL be named `{id}.yaml` where `{id}` matches the record's `id` field exactly, including case. Validation SHALL fail when a filename stem differs from the record `id`.

#### Scenario: Matching filename and id passes

- **WHEN** `data/intblocks/political/UfM.yaml` contains a record with `id: UfM`
- **THEN** filename validation passes for that file

#### Scenario: Case mismatch between filename and id fails

- **WHEN** a file named `UFM.yaml` contains a record with `id: UfM`
- **THEN** validation reports a filename/id mismatch and exits with non-zero status

### Requirement: Category directory matches primary blocktype

Each intblock's parent category directory name SHALL appear in the record's `blocktype` list. Validation SHALL treat a directory-vs-blocktype mismatch as an error.

#### Scenario: Directory present in blocktype list passes

- **WHEN** a record under `data/intblocks/space/` has `space` in its `blocktype` list
- **THEN** directory-alignment validation passes for that record

#### Scenario: Directory missing from blocktype list fails

- **WHEN** a record under `data/intblocks/space/` does not include `space` in its `blocktype` list
- **THEN** validation reports a directory-alignment error and exits with non-zero status

