### Added

- `provisional_application` on trade agreement records and parties, and as a column of
  `trade_agreements`, `trade_agreement_parties` and `country_trade_agreements`: the date an
  agreement began to apply provisionally. `in_force` is now the definitive entry into force;
  an agreement applied only provisionally keeps `status = 'in_force'` with an empty `in_force`.
  Use `coalesce(provisional_application, in_force)` for "applies since". OpenSpec change
  `add-trade-agreement-provisional-application`.
- Five UK trade agreements from gov.uk, checked on 2026-11-23: `GBUA-DTA` (UK-Ukraine Digital
  Trade Agreement, in force since 1 September 2024) and four under negotiation, three of them
  concluded: `GCCGB` (UK-Gulf Cooperation Council FTA, concluded 20 May 2026), `GBKR-2025`
  (upgraded UK-Korea FTA, concluded 15 December 2025), `CHGB-2026` (enhanced UK-Switzerland
  FTA, concluded 13 July 2026) and `GBTR-2024` (enhanced UK-Turkey FTA).

### Changed

- 34 UK trade agreement records are checked against gov.uk and the UK Treaty Series and are
  now `verification: official`, with the gov.uk name (the catalogue name stays in
  `other_names`), the agreement collection link and the treaty series numbers in `notes`.
  Entry into force dates follow the Treaty Series: 31 December 2020 instead of 1 January 2021
  for 12 continuity agreements, and later dates for `CAGB`, `CMGB`, `EGGB`, `GBISLINO`, `GBKE`,
  `GBMK`, `GBRS` and `GBTR`, several of which applied provisionally from 1 January 2021.
  `GBMA`, `UKCARIFORUM` and `UKPACIFICEPA` are applied provisionally only and have no
  `in_force` date.
- `CPTPP`: the United Kingdom's entry gives the date its accession entered into force with each
  partner.

### Fixed

- `GBGE` signature date (21 October 2019, not 1 January 2014), `GBLB` signature date
  (19 September 2019), `CAGB` (9 December 2020) and `CMGB` (9 March 2021), from the treaty texts.
- `UKESA` lists Madagascar as a party; `UKCARIFORUM` no longer lists Haiti, which has not signed.
