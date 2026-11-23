## 0. Approval gate

- [x] 0.1 Obtain maintainer approval for `add-trade-agreement-instruments` (approved on 2026-11-23)
- [x] 0.2 Resolve the open questions in `design.md` (approved with the defaults: one date plus a note, no derived columns, every notified decision kept)

## 1. Schema and validation

- [x] 1.1 Add the `instruments` item definition to `data/schemas/trade_agreements.schema.json`, with the kinds, statuses, `coverage` values, `id` pattern, `additionalProperties: false` and required provenance
- [x] 1.2 Add the rules `DUPLICATE_TRADE_AGREEMENT_INSTRUMENT` and `TRADE_AGREEMENT_INSTRUMENT_DATE` to `internacia_builder/validate/trade_agreement_rules.py`, and the report-only `TRADE_AGREEMENT_INSTRUMENT_BEFORE_AGREEMENT`; register them in `registry.py`
- [x] 1.3 Tests for every scenario in the spec delta in `tests/test_trade_agreements.py`

## 2. Build and export

- [x] 2.1 Build `trade_agreement_instruments` rows in `internacia_builder/trade_agreements.py` (linked records included)
- [x] 2.2 Add `get_trade_agreement_instruments_schema` to `schemas.py`, export Parquet, JSONL and DuckDB, and list the resource in `contract.json`, `datapackage.json` and the manifests (primary and foreign keys, open enums)
- [x] 2.3 Cover the table in `scripts/check_generated_artifacts.py` and in the contract tests
- [ ] 2.4 Bump the contract to 5.1 (MINOR) through the release train (at release time)

## 3. Backfill

- [x] 3.1 Move the MOFCOM upgrade and early harvest facts on `ACFTA`, `CHCN`, `CLCN`, `CNGE`, `CNKR`, `CNNI`, `CNNZ`, `CNPE`, `CNPK`, `CNSG` and `SACUCN` from `notes` into `instruments`, and delete the repeated sentences (after datenoio/internacia-db#211 merges)
- [x] 3.2 Add `scripts/oneoff/import_trade_agreement_instruments.py`: read the `RTA Changes` sheet, skip the 232 LAIA partial-scope rows, map the 127 amendment rows by `wto_rta_id`, derive `kind`, `coverage` and dates, and write the instruments with RTA ID card provenance
- [x] 3.3 Hand-review the kinds, split rows that notify two instruments, merge items found in both sources (`ACFTA`, `CLCN`, `CNPK`), and record date conflicts in item notes
- [x] 3.4 Log the walk in `docs/intblock-sources.md` and list it in `scripts/oneoff/README.md`

## 4. Documentation

- [x] 4.1 Document the field in the registry section of `docs/intblock-inclusion-policy.md` (instrument or separate record), and the table in `docs/data-contract.md` and `docs/ai-consumers.md`
- [x] 4.2 Add a query example (the instruments of an agreement, and agreements upgraded since a date) to `docs/query-examples.md`, with a documented-query test
- [x] 4.3 Regenerate the agent shims; add a changelog fragment

## 5. Verification

- [x] 5.1 Rebuild with the pinned requirements; run the snapshot, artifact, doc-count and link checks
- [x] 5.2 Run all validators, `ruff` and `pytest tests/`
