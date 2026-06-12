# Change: Add automated test suite

## Why

The repository has no `tests/` directory and no pytest in CI. Validation and build logic in `scripts/builder.py` and `scripts/validate_countries.py` are only exercised indirectly via CI smoke tests. Breaking schema changes (e.g. v1.2.0 population struct migration) lack unit and golden-file coverage.

See [docs/improvement-plan.md](../../../docs/improvement-plan.md) §2.1.

## What Changes

- Add `tests/` with pytest covering `clean_data()`, completeness gates, manifest generation, and cross-dataset include resolution.
- Add minimal YAML fixtures under `tests/fixtures/`.
- Add `pytest` to dev dependencies (`requirements-dev.txt` or `pyproject.toml`).
- Extend CI to run `pytest tests/ -q` on pull requests affecting `scripts/` or `data/schemas/`.
- Document test conventions in `CONTRIBUTING.md` (or cross-reference `add-contributor-docs`).

## Impact

- Affected specs: `countries-build`, `countries-data-quality`, `dev-tooling` (new)
- Affected code: `tests/`, `.github/workflows/validate.yml`, dependency files
- Breaking: None
