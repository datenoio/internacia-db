## 0. Approval gate

- [ ] 0.1 Resolve the open questions in `design.md`
- [ ] 0.2 Record the maintainer decision on whether border crossing status is in scope; if not, split section 3 into its own change
- [ ] 0.3 Obtain approval for `add-transit-dependence-layer` before any schema, code, or data change

## 1. Infrastructure roles: contract

- [ ] 1.1 Declare `includes[].role` in `data/schemas/intblocks.schema.json` with the `origin`, `transit`, `destination` enum
- [ ] 1.2 Add `data/schemas/include_roles.yaml` with a definition and boundary examples for every role, and a test that its keys equal the schema enum
- [ ] 1.3 Confirm `contract.json` lists `includes[].role` as an open enum
- [ ] 1.4 Add validation: role only on `gaspipeline` records; all-or-none roles on a record's current country entries; at least one `origin` and one `destination`; provenance with `field: includes`
- [ ] 1.5 Register the rules in the shared registry with issue types, priorities and descriptions, and add unit tests

## 2. Infrastructure roles: pilot

- [ ] 2.1 Add a reviewed manifest with a role for every country entry of the 25 `gaspipeline` records and a source URL per record; defer records whose route the sources do not settle
- [ ] 2.2 Add a dry-run-first backfill script (or extend the institutional-design one) with whole-cohort validation, conflict blocking, idempotence and provenance insertion, plus tests
- [ ] 2.3 Run the dry run, review the report, apply, and confirm only `includes[].role` and provenance changed

## 3. Border crossing status

- [ ] 3.1 Add `data/schemas/border_status.schema.json` and `data/borders/border_status.yaml`
- [ ] 3.2 Add validation: sorted resolvable pair, adjacency in both countries' `borders`, no overlapping periods, `since` not after `until`, required provenance; register the rules and add tests
- [ ] 3.3 Export the `border_status` table (Parquet, JSONL, DuckDB) with a manifest, a primary key and foreign keys in `contract.json`
- [ ] 3.4 Add the `country_borders` view to the DuckDB export and the contract
- [ ] 3.5 Add a reviewed pilot manifest for the candidate closures with official sources; defer candidates without one; apply

## 4. Recipes and documentation

- [ ] 4.1 Add the sea-access gateway recipe to `docs/query-examples.md`, with lower-bound wording and the Kyrgyzstan counter-example, backed by `tests/test_documented_queries.py`
- [ ] 4.2 Document trade dependence measures, sources and their terms, and the external join pattern in `docs/ai-consumers.md`
- [ ] 4.3 Document `includes[].role` in `docs/intblock-inclusion-policy.md` and `docs/ai-consumers.md`; document `border_status` and `country_borders` in `docs/data-contract.md`
- [ ] 4.4 Update `docs/when-to-use-internacia.md`, regenerate `docs/data-dictionary.md`, update `llms.txt`, regenerate agent shims, and add a MINOR entry to `CHANGELOG.md`

## 5. Verification

- [ ] 5.1 Rebuild with the pinned requirements and run the committed-snapshot, reproducibility, artifact and release-bundle checks
- [ ] 5.2 Run both validators, `pytest tests/`, the quality gate and the SDK contract suite
- [ ] 5.3 Confirm `countries.schema.json` gains no property
