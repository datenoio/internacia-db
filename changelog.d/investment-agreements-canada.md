### Added

- `trade_agreements` accepts `agreement_type: investment` for standalone investment treaties, such as bilateral investment treaties and Canada's FIPAs. Investment records have ids ending in `-BIT`, or `-BIT-YYYY` for a further treaty between the same parties. The new validator rule `TRADE_AGREEMENT_ID_SUFFIX` checks the suffix (OpenSpec `add-investment-agreements`).
- 65 Canadian investment treaty records (`AMCA-BIT`, `CACN-BIT`, `CAUA-BIT` and others), all `verification: official`:
  - 59 rows of the Global Affairs Canada agreements table, with signature, entry into force and suspension dates from the Canada Treaty Series;
  - six Canada Treaty Series treaties that the table omits (El Salvador, South Africa, Uruguay 1991, Czechoslovakia 1990, Latvia 1995, Romania 1996).

  Imported with `scripts/oneoff/import_canada_fipas.py`, checked on 2026-11-23.

### Changed

- The `services` agreement type now means services-only agreements. Investment treaties use `investment`.
- `country_trade_agreements` and `trade_agreement_parties` now include investment treaties. Filter on `agreement_type` to count trade agreements only.
