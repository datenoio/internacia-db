## MODIFIED Requirements

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
