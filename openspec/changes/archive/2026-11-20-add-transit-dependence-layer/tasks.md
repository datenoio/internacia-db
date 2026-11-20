## 0. Approval gate

- [x] 0.1 Resolve the open questions in `design.md` (2026-11-20)
- [x] 0.2 Record the maintainer decision on whether border crossing status is in scope; if not, split section 3 into its own change (in scope, 2026-11-20)
- [x] 0.3 Obtain approval for `add-transit-dependence-layer` before any schema, code, or data change (2026-11-20)

## 1. Infrastructure roles: contract

- [x] 1.1 Declare `includes[].role` in `data/schemas/intblocks.schema.json` with the `origin`, `transit`, `destination`, `terminal` enum, and add the `oilpipeline` and `corridor` blocktypes
- [x] 1.2 Add `data/schemas/include_roles.yaml` with a definition and boundary examples for every role, and a test that its keys equal the schema enum
- [x] 1.3 Confirm `contract.json` lists `includes[].role` as an open enum
- [x] 1.4 Add validation: role only on `gaspipeline`, `oilpipeline` and `corridor` records; role values by kind; all-or-none roles on a record's current country entries; at least one `origin` and one `destination` on pipelines, at least two `terminal` on corridors; provenance with `field: includes`
- [x] 1.5 Register the rules in the shared registry with issue types, priorities and descriptions, and add unit tests

## 2. Infrastructure roles: pilot

- [x] 2.1 Add a reviewed manifest with a role for every country entry of the 25 `gaspipeline` records and the corridor records, and a source URL per record; defer records whose route the sources do not settle
- [x] 2.1a Add sourced `oilpipeline` records for the candidate crude-oil pipelines, with roles; defer candidates without a qualifying source
- [x] 2.2 Add a dry-run-first backfill script (or extend the institutional-design one) with whole-cohort validation, conflict blocking, idempotence and provenance insertion, plus tests
- [x] 2.3 Run the dry run, review the report, apply, and confirm only `includes[].role` and provenance changed

## 3. Border crossing status

- [x] 3.1 Add `data/schemas/border_status.schema.json` and `data/borders/border_status.yaml`
- [x] 3.2 Add validation: sorted resolvable pair, adjacency in both countries' `borders`, no overlapping periods, `since` not after `until`, required provenance; register the rules and add tests
- [x] 3.3 Export `border_status` like the alias artifacts (committed JSON, Parquet, DuckDB table, datapackage) with a primary key and foreign keys in `contract.json`
- [x] 3.4 Add the `country_borders` view to the DuckDB export and the contract
- [x] 3.5 Add a reviewed pilot manifest for the candidate closures with official sources; defer candidates without one; apply

## 4. Recipes and documentation

- [x] 4.1 Add the sea-access gateway recipe to `docs/query-examples.md`, with lower-bound wording and the Kyrgyzstan counter-example, backed by `tests/test_documented_queries.py`
- [x] 4.2 Document trade dependence measures, sources and their terms, and the external join pattern in `docs/ai-consumers.md`
- [x] 4.3 Document `includes[].role` in `docs/intblock-inclusion-policy.md` and `docs/ai-consumers.md`; document `border_status` and `country_borders` in `docs/data-contract.md`
- [x] 4.4 Update `docs/when-to-use-internacia.md`, regenerate `docs/data-dictionary.md`, update `llms.txt`, regenerate agent shims, and add a MINOR entry to `CHANGELOG.md`

## 5. Verification

- [x] 5.1 Rebuild with the pinned requirements and run the committed-snapshot, reproducibility, artifact and release-bundle checks
- [x] 5.2 Run both validators, `pytest tests/`, the quality gate and the SDK contract suite
- [x] 5.3 Confirm `countries.schema.json` gains no property
