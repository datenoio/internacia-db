### Changed

- YAML is read with libyaml's C parser (`CSafeLoader`) through
  `internacia_builder.yaml_io.safe_load`, about eight times faster than `yaml.safe_load`.
  Writing stays on PyYAML's Python emitter, so every export is byte-for-byte the same.
  `ruff` now rejects `yaml.safe_load` (`TID251`).
- `INTERNACIA_ZSTD_LEVEL` (1–22) sets the zstd level of the `*.zst` and Parquet exports. The
  default stays 22, which releases always use. The `validate` workflow builds at 3, which
  nearly halves each build.
- In the `validate` workflow, the checks that do not depend on the Python version (dependency
  audit, oldest-DuckDB read, data, documentation, staged-artifact and quality checks) run on
  Python 3.13 only, and are no longer repeated on every leg. The 3.12 leg keeps coverage and
  the SDK contract suite, and 3.11 keeps the reproducibility check. Each Python version still
  builds its own artifacts and runs the whole test suite. The CI artifacts are now named
  `validation-reports` and `quality-report`, without a `-py3.x` suffix.
