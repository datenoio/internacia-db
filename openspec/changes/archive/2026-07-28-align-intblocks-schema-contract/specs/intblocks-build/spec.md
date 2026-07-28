## ADDED Requirements

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
