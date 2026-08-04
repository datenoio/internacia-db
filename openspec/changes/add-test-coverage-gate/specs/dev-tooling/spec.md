## ADDED Requirements

### Requirement: Test coverage reporting in CI

Pull request CI SHALL run pytest with coverage reporting for `internacia_builder` and fail when line coverage falls below a configured minimum threshold documented in `pyproject.toml`.

#### Scenario: Coverage reported on PR

- **WHEN** CI runs on a pull request modifying Python code
- **THEN** the workflow output includes a coverage summary for `internacia_builder`

#### Scenario: Coverage regression fails CI

- **WHEN** a change reduces coverage below the configured fail-under threshold
- **THEN** the validate workflow fails
