## ADDED Requirements

### Requirement: Validator warnings gate CI

Pull request CI SHALL run `validate_countries.py` and `validate_intblocks.py` with `--fail-on-warning`, so any validator warning fails the run. Warnings from dated rules, which compare a recorded date with the current date (`last_verified` age, provenance age, border status age), SHALL be reported and counted but SHALL NOT fail `--fail-on-warning`.

#### Scenario: New warning fails CI

- **WHEN** a pull request introduces a record that raises a validator warning from a rule that is not dated
- **THEN** the validation step in CI fails

#### Scenario: Ageing dates do not fail CI

- **WHEN** a recorded `last_verified` or provenance date passes its configured maximum age while the data is unchanged
- **THEN** the validator reports the staleness warning and still exits 0 under `--fail-on-warning`
