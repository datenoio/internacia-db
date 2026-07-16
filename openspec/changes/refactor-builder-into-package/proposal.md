# Change: Move build and quality logic into the installable package

## Why
`scripts/builder.py` is a 2,260-line monolith (~35% of all Python LOC) mixing export schemas, data cleaning, manifest writing, and the entire quality analyzer, which duplicates validation logic already in `internacia_builder.validate.*`. The `refactor-scripts-package` change migrated validation only; enrichment scripts still use raw `urllib` instead of the shared `internacia_builder.http` client, and there are no cross-format export equivalence tests. This structure invites hidden drift between validators, quality reports, and export behavior.

## What Changes
- Move build/export/manifest logic into `internacia_builder.build` and the quality analyzer into `internacia_builder.quality`; reduce `scripts/builder.py` to a thin CLI shim.
- Replace duplicated validation logic in the analyzer with calls to `internacia_builder.validate.*` or shared rule functions.
- Migrate `enrich_countries.py` and `enrich_intblocks.py` to the shared `internacia_builder.http` client (completes the open `refactor-scripts-package` HTTP task).
- Add console entry points `internacia-build` and `internacia-analyze-quality` in `pyproject.toml`, and set a documented package version policy (align `internacia_builder.__version__` with dataset releases instead of `0.0.0`).
- Add tests for JSONL/YAML.zst export, cross-format row/primary-key equivalence, and full-dataset manifest consistency; update stale fixture counts (252/1057 → current).

## Impact
- Affected specs: dev-tooling
- Affected code: `internacia_builder/build.py` (new), `internacia_builder/quality.py` (new), `scripts/builder.py`, `scripts/enrich_countries.py`, `scripts/enrich_intblocks.py`, `internacia_builder/__init__.py`, `pyproject.toml`, `tests/`
