# Change: Add developer tooling (lint, format, pre-commit)

## Why

The repository has no ruff, mypy, or pre-commit configuration despite `.gitignore` entries anticipating those tools. Code style is inconsistent (`builder.py` uses legacy `typing.List` while newer scripts use modern annotations).

See [docs/improvement-plan.md](../../../docs/improvement-plan.md) §2.3.

## What Changes

- Add `pyproject.toml` with `[tool.ruff]` lint and format settings matching project conventions.
- Add `.pre-commit-config.yaml` with ruff and YAML/JSON sanity checks.
- Add optional mypy configuration for new modules (strict on `tests/` and new package code).
- Add ruff check to CI (non-blocking warn first, then required).
- Gradually modernize type annotations in touched files (no mass refactor required in this change).

## Impact

- Affected specs: `dev-tooling` (modified)
- Affected code: `pyproject.toml`, `.pre-commit-config.yaml`, `.github/workflows/`, selected scripts
- Breaking: None
