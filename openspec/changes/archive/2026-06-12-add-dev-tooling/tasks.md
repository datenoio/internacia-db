## 1. Configuration

- [x] 1.1 Add `pyproject.toml` with `[tool.ruff]` (line length, target Python 3.11, select rules)
- [x] 1.2 Add `.pre-commit-config.yaml` with ruff check/format and basic YAML validation
- [x] 1.3 Optional `[tool.mypy]` skipped for now (ruff covers current needs)

## 2. CI integration

- [x] 2.1 Add ruff check step to `.github/workflows/validate.yml`
- [x] 2.2 Fix or noqa any blocking violations in `scripts/` (minimal scope)

## 3. Documentation

- [x] 3.1 Document pre-commit setup in `CONTRIBUTING.md`
- [x] 3.2 Run `openspec validate add-dev-tooling --strict`
