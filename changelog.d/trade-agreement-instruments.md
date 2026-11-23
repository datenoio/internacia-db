### Added

- New `trade_agreement_instruments` table (Parquet, JSONL, DuckDB; listed in
  `contract.json` and `datapackage.json`). It has one row per agreement and per instrument
  that amends or adds to the agreement: upgrade and amending protocols, CEPA Supplements,
  supplementary agreements, early harvest arrangements and Joint Committee decisions. Each
  row has a `kind`, a `status`, dates, `coverage` and provenance. The primary key is
  (`agreement_id`, `instrument_id`). This is an additive (MINOR) contract change; OpenSpec
  `add-trade-agreement-instruments`.
- Optional `instruments` list on `data/trade_agreements/*.yaml` records, validated by the
  JSON Schema and by the rules `DUPLICATE_TRADE_AGREEMENT_INSTRUMENT` and
  `TRADE_AGREEMENT_INSTRUMENT_DATE`. The quality report lists instruments signed before
  their agreement as `TRADE_AGREEMENT_INSTRUMENT_BEFORE_AGREEMENT`.
- 136 instruments on 48 records:
  - 122 come from the WTO RTA-IS `RTA Changes` sheet, checked on 2026-11-23. They are
    Joint Committee decisions of EFTA and other agreements, the Mainland–Hong Kong and
    Mainland–Macao CEPA Supplements and agreements, and amending protocols.
  - 14 come from China FTA Network (MOFCOM) releases. They are the `ACFTA` 2.0 and 3.0
    protocols, the upgrade protocols of `CHCN`, `CLCN`, `CNGE`, `CNNZ`, `CNPE` and `CNSG`,
    the `CNPK` second-phase protocol, the `CNNI` early harvest arrangement, and the
    negotiations on `CNKR` (second phase), `CNNZ` (services) and `SACUCN` (early harvest).
- `scripts/oneoff/import_trade_agreement_instruments.py`, the import that wrote them.
- Query recipes for an agreement's instruments and for agreements upgraded since a date.

### Changed

- The upgrade and early harvest sentences that the MOFCOM import put in `notes` on 11 records
  now live in `instruments`. When MOFCOM and the WTO give different dates for the same
  instrument, the item's `notes` record the WTO dates.
