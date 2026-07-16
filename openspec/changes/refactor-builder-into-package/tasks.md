## 1. Extract build logic
- [x] 1.1 Move export schemas, `clean_data`, format writers, and manifest/sidecar/`_meta` writers into `internacia_builder/build.py`
- [x] 1.2 Reduce `scripts/builder.py` `build`/`info` commands to thin CLI wrappers over the package API
- [x] 1.3 Preserve existing CLI behavior and flags (backwards compatible)

## 2. Extract quality analyzer
- [x] 2.1 Move the quality analyzer into the package (`internacia_builder/build.py`, exposed via `internacia_builder/quality.py`)
- [ ] 2.2 Replace duplicated border/indicator/duplicate/ref checks with calls to `internacia_builder.validate.*` or shared rule functions — deferred: analyzer relocated into the package but still carries its own rule copies; deduplication against `internacia_builder.validate.*` is a follow-up
- [x] 2.3 Keep `scripts/builder.py analyze-quality` as a thin wrapper

## 3. Shared HTTP and entry points
- [x] 3.1 Migrate `enrich_countries.py` and `enrich_intblocks.py` to `internacia_builder.http`
- [x] 3.2 Add `internacia-build` and `internacia-analyze-quality` console entry points to `pyproject.toml`
- [x] 3.3 Set a documented package version policy and update `internacia_builder.__version__`

## 4. Tests
- [x] 4.1 Add tests for `save_jsonl_zst` and `save_yaml_zst`
- [x] 4.2 Add a cross-format export equivalence test (row and primary-key parity across formats)
- [x] 4.3 Add a full-dataset manifest consistency test and update stale fixture counts
- [x] 4.4 Run `pytest tests/`, `ruff check`, and `openspec validate refactor-builder-into-package --strict`
