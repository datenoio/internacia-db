## ADDED Requirements

### Requirement: Quality analysis runs in CI

Pull request CI SHALL run the dataset quality analyzer and publish its report as a workflow artifact. The step SHALL fail only when CRITICAL or IMPORTANT priority issues are present, with the failing threshold configurable.

#### Scenario: Report published on every run

- **WHEN** CI runs the quality analyzer on a pull request
- **THEN** the analyzer report is available as a downloadable workflow artifact

#### Scenario: Critical issue fails the build

- **WHEN** the analyzer reports at least one CRITICAL issue
- **THEN** the CI quality step fails

#### Scenario: Low-priority issues do not fail the build

- **WHEN** the analyzer reports only MEDIUM and LOW issues
- **THEN** the CI quality step passes while still publishing the report

### Requirement: Quality report freshness

Checked-in quality reports under `dataquality/` SHALL be regenerated on release or published as CI artifacts rather than committed as stale copies. Any report that remains tracked SHALL have its header record counts validated against current source counts, and there SHALL NOT be parallel stale and fresh report directories.

#### Scenario: Stale tracked report detected

- **WHEN** a tracked quality report header count no longer matches the current source record count
- **THEN** the freshness check reports the mismatch

#### Scenario: No parallel report directories

- **WHEN** the repository is inspected for quality reports
- **THEN** there is a single canonical report location, not both a stale directory and a `fresh_run/` directory
