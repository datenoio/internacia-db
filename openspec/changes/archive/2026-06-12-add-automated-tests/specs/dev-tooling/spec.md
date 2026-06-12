## ADDED Requirements

### Requirement: Automated unit test suite

The repository SHALL include a `tests/` directory with pytest tests covering core build and validation logic.

#### Scenario: Tests run locally

- **WHEN** a developer runs `pytest tests/ -q` after installing dev dependencies
- **THEN** all tests pass on a clean checkout of `main`

#### Scenario: Tests run in CI

- **WHEN** a pull request modifies `scripts/` or `data/schemas/`
- **THEN** CI executes pytest and fails on test failures

### Requirement: Clean data normalization tests

Tests SHALL cover `clean_data()` edge cases including YAML boolean strings, None-to-default conversion, and list field normalization.

#### Scenario: Boolean string normalized

- **WHEN** source data contains the string `"yes"` for a boolean field
- **THEN** `clean_data()` produces a boolean `True` in exported records

### Requirement: Manifest generation tests

Tests SHALL verify that build manifest output includes required keys and stable `schema_hash` for unchanged PyArrow schemas.

#### Scenario: Manifest contains required fields

- **WHEN** a test invokes manifest generation for countries
- **THEN** output includes `version`, `build_date`, `git_commit`, `row_count`, and `schema_hash`

### Requirement: Offline test execution

The test suite SHALL NOT require network access to external APIs.

#### Scenario: CI pytest without network

- **WHEN** pytest runs in CI with network restricted
- **THEN** all tests pass without HTTP calls to Wikidata or World Bank
