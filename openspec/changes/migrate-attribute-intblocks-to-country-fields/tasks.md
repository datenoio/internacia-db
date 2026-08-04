## 1. Schema and vocab foundations

- [x] 1.1 Add country fields to `data/schemas/countries.schema.json`: `writing_directions`, `writing_systems`, `dvd_region`, `broadcast_systems`, `legal_systems`, `rail_gauges` (keep existing `car_side`)
- [x] 1.2 Create `data/vocabs/` catalogs for writing directions/systems, DVD regions, broadcast systems, legal systems, rail gauges (and optional government forms vocab without country binding)
- [x] 1.3 Map legacy intblock ids → vocab ids in a documented mapping table used by the invert script
- [x] 1.4 Extend countries completeness config with warn-mode thresholds for the new fields

## 2. Policy and consumer docs

- [x] 2.1 Update `docs/intblock-inclusion-policy.md` to exclude attribute partitions from intblocks; clarify geographic vs attribute `reference_enumeration`
- [x] 2.2 Update `openspec/project.md` countries in-scope list to name the new attribute fields (still excluding government type)
- [x] 2.3 Document fields and migration in `docs/ai-consumers.md`, `docs/data-dictionary.md`, `llms.txt`, and README field tables
- [x] 2.4 Add/adjust DuckDB query examples that filter on country columns instead of attribute intblocks

## 3. Migration tooling and invert

- [x] 3.1 Implement invert script: read attribute intblock `includes` → write country YAML fields; emit conflict report for `car_side` vs `traffichand`
- [x] 3.2 Run invert for all in-scope blocktypes; resolve reported conflicts; leave intentional gaps omitted rather than inventing values
- [x] 3.3 Add `data/attribute_intblock_migrations.yaml` covering every retired attribute intblock id → country field/value predicate
- [x] 3.4 Wire builder export of `data/datasets/attribute_intblock_migrations.json` (and optional Parquet)

## 4. Retire attribute intblocks

- [x] 4.1 Delete `data/intblocks/{dvdregion,lawsystem,railgauge,teleregion,traffichand,writingdirection,writingsystem,govform}/`
- [x] 4.2 Remove corresponding entries from `data/blocktypes/blocktypes.yaml`
- [x] 4.3 Remove these directories from `scripts/label_scope_category.py` and any blocktype allowlists/exemptions that become obsolete
- [x] 4.4 Ensure validators no longer expect these blocktypes; orphan-blocktype cleanup passes

## 5. Validation, build, and release notes

- [x] 5.1 Add unit/integration tests for schema shapes, vocab id resolution, migration artifact integrity, and `car_side` reconciliation
- [x] 5.2 Run `validate_countries.py --json`, `validate_intblocks.py --json`, and pytest; fix regressions
- [x] 5.3 Rebuild datasets; update `migration.vUnreleased.json` (countries added fields; intblocks/blocktypes removals)
- [x] 5.4 Write CHANGELOG BREAKING entry with before/after query examples for retired ids

## 6. OpenSpec closure

- [x] 6.1 Confirm all tasks done after approval and implementation
- [ ] 6.2 Archive this change after the implementing release lands
