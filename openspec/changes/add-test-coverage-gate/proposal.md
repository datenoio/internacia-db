# Change: Add pytest coverage gate in CI

## Why
The repository has 14 test files but no coverage metrics. The deep review recommends `pytest-cov` with a published floor to prevent silent test-quality regression.

## What Changes
- Add `pytest-cov` to dev dependencies.
- Configure coverage in `pyproject.toml` with a minimum threshold starting at the current measured baseline.
- Add `pytest --cov` step to `.github/workflows/validate.yml`.
- Optionally add coverage badge to README.

## Impact
- Affected specs: dev-tooling
- Affected code: `pyproject.toml`, `.github/workflows/validate.yml`, `README.md`
