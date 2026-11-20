## 0. Approval gate

- [x] 0.1 Resolve the open questions in `design.md` (field name, `mandate` values, pilot cohort)
- [x] 0.2 Obtain approval for `add-intblock-institutional-design` before any schema, code, or data change

## 1. Contract and catalog

The schema, catalog, and documentation land together, so consumers never see an undocumented value.

- [x] 1.1 Add the optional `institutional_design` object and its seven subfields to `data/schemas/intblocks.schema.json`, with `additionalProperties: false`
- [x] 1.2 Add `data/schemas/institutional_design.yaml` with a definition, positive criteria, and boundary examples for every value
- [x] 1.3 Add a test that the JSON Schema enums and the catalog keys are identical
- [x] 1.4 Confirm `contract.json` lists the subfield enums as open (`institutional_design.mandate`, `institutional_design.independent_organs[]`, and the others)

## 2. Validation

- [x] 2.1 Reject `none` combined with any other value in `independent_organs` or `enforcement`
- [x] 2.2 Reject duplicate list values
- [x] 2.3 Reject `veto_holders` codes that are not current country members of the record
- [x] 2.4 Warn when `veto_holders` is non-empty and `decision_rule` is `consensus` or `unanimity`
- [x] 2.5 Reject `institutional_design` on `reference_enumeration` and `non_state_organization` records
- [x] 2.6 Reject `institutional_design` without a `provenance` entry whose `field` is `institutional_design` or starts with `institutional_design.`
- [x] 2.7 Register the new rules in the shared quality-rule registry, so the validator and the quality report agree
- [x] 2.8 Report `institutional_design` coverage in the completeness report, without a threshold gate
- [x] 2.9 Add unit tests for every rule, including a valid record, each rejection, and the warning

## 3. Exports

- [x] 3.1 Add the `institutional_design` struct to the intblocks Arrow schema in `internacia_builder/schemas.py`
- [x] 3.2 Keep the schema-parity test green, with no new allowlist entries
- [x] 3.3 Flatten the struct into `design_*` columns in the CSV export in `internacia_builder/export.py`, following the `headquarters` pattern; leave the lite exports unchanged
- [x] 3.4 Add export tests for Parquet, DuckDB, JSONL, and CSV, with a populated record and an absent one

## 4. Pilot backfill

- [x] 4.1 Add `data/schemas/institutional_design_pilot.yaml` with the reviewed IDs, values, and a primary-source URL per record (34 applied, 2 deferred with reasons)
- [x] 4.2 Add a dry-run-first backfill script: whole-cohort validation, conflict blocking, idempotence, provenance insertion, and a JSON report
- [x] 4.3 Add unit tests for dry run, conflict, idempotence, and an unknown ID
- [x] 4.4 Review each of the 36 candidates against its founding instrument or rules of procedure
- [x] 4.5 Run the dry run and review the full JSON report
- [x] 4.6 Apply, then confirm that exactly 34 source files changed and that no roster, name, or hierarchy changed
- [x] 4.7 Run both validators with zero errors

## 5. Recipes and documentation

- [x] 5.1 Add the authority-level recipe to `docs/query-examples.md` and back it with `tests/test_documented_queries.py`
- [x] 5.2 Add the member-capacity-concentration recipe (world share, largest member, HHI, effective members, population years) and back it with a test
- [x] 5.3 Document the external-indicator join pattern on `iso3code` in `docs/ai-consumers.md`, and state that no indicator data ships
- [x] 5.4 Add a section on `institutional_design` to `docs/intblock-inclusion-policy.md`
- [x] 5.5 Update `docs/when-to-use-internacia.md`: authority facts are in scope; capacity indicators stay downstream
- [x] 5.6 Regenerate `docs/data-dictionary.md`, update `llms.txt`, and regenerate the agent shims from `templates/`
- [x] 5.7 Add a MINOR-release entry to `CHANGELOG.md`

## 6. Verification

- [x] 6.1 Run `python scripts/builder.py build` and confirm artifact consistency
- [x] 6.2 Run `python scripts/validate_intblocks.py --json` and `python scripts/validate_countries.py --json`
- [x] 6.3 Run `pytest tests/`
- [x] 6.4 Confirm `countries.schema.json` gains no property
