### Added

- `trade_agreements.dta_id`: the agreement id (`WB ID`) in the World Bank Deep Trade Agreements
  (DTA) database, the key of the DTA content files. Set on the registry records that DTA lists,
  mapped by `scripts/oneoff/import_dta.py` from the version 2 files of 2024-01-23 (OpenSpec
  change `add-dta-catalogue-links`). The registry does not ship the DTA content data.

### Changed

- The validator also reports a `dta_id` set on two records as `DUPLICATE_IDENTIFIER`.
