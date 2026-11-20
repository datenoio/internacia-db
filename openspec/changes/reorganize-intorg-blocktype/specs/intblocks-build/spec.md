## MODIFIED Requirements

### Requirement: Category directory matches primary blocktype

Each intblock's parent category directory name SHALL be the first value of the record's `blocktype` list. Validation SHALL treat a directory-vs-blocktype mismatch as an error.

#### Scenario: Directory is the first blocktype

- **WHEN** a record under `data/intblocks/space/` has `blocktype: [space, intorg]`
- **THEN** directory-alignment validation passes for that record

#### Scenario: Directory is not the first blocktype

- **WHEN** a record under `data/intblocks/space/` has `blocktype: [intorg, space]`
- **THEN** validation reports a directory-alignment error and exits with non-zero status

#### Scenario: Directory missing from blocktype list fails

- **WHEN** a record under `data/intblocks/space/` does not include `space` in its `blocktype` list
- **THEN** validation reports a directory-alignment error and exits with non-zero status
