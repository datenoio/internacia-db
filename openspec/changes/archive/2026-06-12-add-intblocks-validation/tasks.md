## 1. Schema and configuration

- [x] 1.1 Review and tighten `data/schemas/intblocks.schema.json` for builder-exported fields
- [x] 1.2 Add `data/schemas/intblocks_completeness.yaml` with thresholds for `wikidata_id`, `includes`, `description`, `headquarters`, `links`
- [x] 1.3 Document intblock `includes` contract (`id` authoritative, `name` is source label) in README

## 2. Validation tooling

- [x] 2.1 Create `scripts/validate_intblocks.py` (Typer CLI): JSON Schema validation per YAML file
- [x] 2.2 Add checks: duplicate `id`, blocktype values exist in `blocktypes.yaml`, `partof` references resolve
- [x] 2.3 Country `includes` cross-reference kept in `validate_countries.py` (runs in same CI job)
- [x] 2.4 Add membership completeness report for categories with known gaps (`agreement`, `intorg`)

## 3. Build integration

- [x] 3.1 Call intblocks validator from `scripts/builder.py` before export
- [x] 3.2 Write `data/datasets/intblocks.manifest.json` on successful intblocks export
- [x] 3.3 Extended `scripts/diff_countries_baseline.py` to diff the intblocks manifest

## 4. CI and documentation

- [x] 4.1 Extend `.github/workflows/validate.yml` with intblocks validation step and report artifact
- [x] 4.2 Update README scripts table and intblocks quality section
- [x] 4.3 Run `openspec validate add-intblocks-validation --strict`
