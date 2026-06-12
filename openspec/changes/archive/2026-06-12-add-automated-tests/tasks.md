## 1. Test infrastructure

- [x] 1.1 Add `requirements-dev.txt` with `pytest` (and optional `pytest-cov`)
- [x] 1.2 Create `tests/` directory with `conftest.py` for repo root path fixtures
- [x] 1.3 Add minimal country and intblock YAML fixtures (implemented as inline fixtures within test modules)

## 2. Unit tests

- [x] 2.1 `tests/test_clean_data.py`: boolean yes/no normalization, `partof` list normalization, whitespace stripping
- [x] 2.2 `tests/test_validate_countries.py`: schema pass/fail, duplicate detection, completeness warn/error modes
- [x] 2.3 Manifest fields and `schema_hash` stability covered in `tests/test_builder_export.py`
- [x] 2.4 `tests/test_cross_dataset.py`: country include resolution and allowlist behavior

## 3. CI integration

- [x] 3.1 Add pytest step to `.github/workflows/validate.yml`
- [x] 3.2 Ensure tests run without network access (mock or fixture-only external calls)

## 4. Validation

- [x] 4.1 Target ≥ 30 test cases (per improvement plan success metric)
- [x] 4.2 Run `openspec validate add-automated-tests --strict`
