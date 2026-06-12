## ADDED Requirements

### Requirement: Contributing guide

The repository SHALL include `CONTRIBUTING.md` describing development setup, validation commands, and pull request expectations.

#### Scenario: New contributor finds setup steps

- **WHEN** a contributor opens `CONTRIBUTING.md`
- **THEN** they find instructions to install dependencies, run validation, and build datasets

#### Scenario: PR checklist documented

- **WHEN** a contributor prepares a data change pull request
- **THEN** CONTRIBUTING lists required checks (validate countries, builder, pytest when available)

### Requirement: README accuracy

README SHALL list all maintained utility scripts and link to gap analysis files with correct paths.

#### Scenario: Scripts table complete

- **WHEN** a reader checks the README scripts table
- **THEN** all non-deprecated scripts under `scripts/` are listed with purpose

#### Scenario: Gap analysis link valid

- **WHEN** a reader follows the gap analysis link in README Notes
- **THEN** the linked file path exists and has no typographical errors

### Requirement: CI status visibility

README SHALL display a CI workflow status badge for the validate workflow.

#### Scenario: Badge present

- **WHEN** a reader views README on the default branch
- **THEN** a badge reflects the status of `.github/workflows/validate.yml`
