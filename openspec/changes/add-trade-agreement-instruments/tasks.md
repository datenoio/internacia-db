## 0. Approval gate

- [ ] 0.1 Obtain maintainer approval for `add-trade-agreement-instruments`
- [ ] 0.2 Resolve the open questions in `design.md` (per-party dates, derived columns, HS-transposition decisions)

## 1. Schema and validation

- [ ] 1.1 Add the `instruments` item definition to `data/schemas/trade_agreements.schema.json`, with the kinds, statuses, `coverage` values, `id` pattern, `additionalProperties: false` and required provenance
- [ ] 1.2 Add the rules `DUPLICATE_TRADE_AGREEMENT_INSTRUMENT` and `TRADE_AGREEMENT_INSTRUMENT_DATE` to `internacia_builder/validate/trade_agreement_rules.py`, and the report-only `TRADE_AGREEMENT_INSTRUMENT_BEFORE_AGREEMENT`; register them in `registry.py`
- [ ] 1.3 Tests for every scenario in the spec delta in `tests/test_trade_agreements.py`

## 2. Build and export

- [ ] 2.1 Build `trade_agreement_instruments` rows in `internacia_builder/trade_agreements.py` (linked records included)
- [ ] 2.2 Add `get_trade_agreement_instruments_schema` to `schemas.py`, export Parquet, JSONL and DuckDB, and list the resource in `contract.json`, `datapackage.json` and the manifests (primary and foreign keys, open enums)
- [ ] 2.3 Cover the table in `scripts/check_generated_artifacts.py` and in the contract tests
- [ ] 2.4 Bump the contract to 5.1 (MINOR) through the release train

## 3. Backfill

- [ ] 3.1 Move the MOFCOM upgrade and early harvest facts on `ACFTA`, `CHCN`, `CLCN`, `CNGE`, `CNKR`, `CNNI`, `CNNZ`, `CNPE`, `CNPK`, `CNSG` and `SACUCN` from `notes` into `instruments`, and delete the repeated sentences (after datenoio/internacia-db#211 merges)
- [ ] 3.2 Add `scripts/oneoff/import_wto_rta_changes.py`: read the `RTA Changes` sheet, skip the 232 LAIA partial-scope rows, map the 127 amendment rows by `wto_rta_id`, derive `kind`, `coverage` and dates, and write the instruments with RTA ID card provenance
- [ ] 3.3 Hand-review the kinds, split rows that notify two instruments, merge items found in both sources (`ACFTA`, `CLCN`, `CNPK`), and record date conflicts in item notes
- [ ] 3.4 Log the walk in `docs/intblock-sources.md` and list it in `scripts/oneoff/README.md`

## 4. Documentation

- [ ] 4.1 Document the field in the registry section of `docs/intblock-inclusion-policy.md` (instrument or separate record), and the table in `docs/data-contract.md` and `docs/ai-consumers.md`
- [ ] 4.2 Add a query example (the instruments of an agreement, and agreements upgraded since a date) to `docs/query-examples.md`, with a documented-query test
- [ ] 4.3 Regenerate the agent shims; add a changelog fragment

## 5. Verification

- [ ] 5.1 Rebuild with the pinned requirements; run the snapshot, artifact, doc-count and link checks
- [ ] 5.2 Run all validators, `ruff` and `pytest tests/`
