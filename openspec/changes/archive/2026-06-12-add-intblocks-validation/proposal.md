# Change: Add intblocks validation and build quality gates

## Why

The countries dataset has JSON Schema validation, completeness gates, CI enforcement, and a build manifest. International blocks (1,065 records across 51 categories) have `data/schemas/intblocks.schema.json` but no validator script, no completeness config, no manifest, and no CI step. Edits to intblock YAML can ship without schema or cross-reference checks.

See [docs/improvement-plan.md](../../../docs/improvement-plan.md) §1.1 and [dev/research/intblocks_missing_includes_20260528.txt](../../../dev/research/intblocks_missing_includes_20260528.txt).

## What Changes

- Add `scripts/validate_intblocks.py` (Typer CLI): JSON Schema, duplicate `id`, blocktype taxonomy, `partof` references, country `includes` resolution.
- Add `data/schemas/intblocks_completeness.yaml` with per-field `max_null_rate` and `mode` (`warn` | `error`).
- Emit `data/datasets/intblocks.manifest.json` on build (version, commit, row count, schema hash).
- Integrate intblocks validation into `scripts/builder.py` before export.
- Extend CI (`.github/workflows/validate.yml`) with intblocks validation and completeness report artifact.
- Add membership completeness audit script or extend validator with category-specific warn gates for `agreement` and `intorg`.

## Impact

- Affected specs: `intblocks-data-quality`, `intblocks-build`, `cross-dataset-integrity` (modified), `dataset-release` (modified)
- Affected code: `data/schemas/`, `scripts/builder.py`, `scripts/validate_intblocks.py`, `.github/workflows/validate.yml`, `README.md`
- Breaking: None initially (new gates start in warn mode where existing data would fail)
