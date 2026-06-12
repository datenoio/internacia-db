## ADDED Requirements

### Requirement: Ruff lint and format configuration

The repository SHALL include ruff configuration in `pyproject.toml` enforcing consistent Python style for scripts.

#### Scenario: Ruff check passes on main

- **WHEN** a developer runs `ruff check scripts/`
- **THEN** no errors are reported on the default branch after initial cleanup

#### Scenario: Ruff runs in CI

- **WHEN** a pull request modifies Python files under `scripts/`
- **THEN** CI runs ruff and fails on new lint violations

### Requirement: Pre-commit hooks

The repository SHALL provide `.pre-commit-config.yaml` so contributors can run lint checks before commit.

#### Scenario: Pre-commit install documented

- **WHEN** a contributor follows `CONTRIBUTING.md` setup instructions
- **THEN** they can run `pre-commit install` and hooks execute on commit

### Requirement: Type checking configuration

The repository SHALL include mypy configuration for incremental adoption on new and test modules.

#### Scenario: Mypy config present

- **WHEN** mypy is installed and run against configured paths
- **THEN** configuration file exists and documents excluded legacy modules
