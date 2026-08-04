## 1. Dependencies and config
- [x] 1.1 Add `pytest-cov` to dev dependencies
- [x] 1.2 Configure `[tool.coverage.run]` and `[tool.coverage.report]` in `pyproject.toml`
- [x] 1.3 Measure current baseline coverage and set initial fail-under threshold

## 2. CI integration
- [x] 2.1 Add `pytest --cov=internacia_builder --cov-report=term-missing` to validate workflow
- [x] 2.2 Fail CI when coverage drops below threshold

## 3. Visibility
- [x] 3.1 (Optional) Add coverage badge or report artifact upload
