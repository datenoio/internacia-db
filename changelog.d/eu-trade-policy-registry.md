### Added

- Ten EU trade agreements from the European Commission's negotiations and agreements
  overview (DG Trade, checked on 2026-11-23), all `verification: official`:
  - `EUXK`: EU-Kosovo Stabilisation and Association Agreement, in force since 2016-04-01.
  - `EUSG-DTA`: EU-Singapore Digital Trade Agreement, in force since 2026-02-01.
  - `EUCA-DTA`: EU-Canada Digital Trade Agreement, concluded on 2026-10-30 and not yet
    signed (`negotiating`).
  - `EUMX-MGA` and `EUMX-ITA`: the EU-Mexico Modernised Global Agreement and Interim
    Trade Agreement, both signed on 2026-05-22.
  - `EUCL-AFA`: EU-Chile Advanced Framework Agreement, signed on 2023-12-13.
  - `EUAE`: EU-United Arab Emirates FTA, under negotiation since 2025-05-28.
  - `EUGCC`: EU-GCC FTA, launched in 1990 and suspended since 2008. It keeps the
    `negotiating` status, and a note records the suspension.
  - `EUEACEPA`: the regional EU-EAC Economic Partnership Agreement. Kenya and Rwanda
    signed it in September 2016, and it has never been applied.
  - `EUADSM`: the EU-Andorra-San Marino Association Agreement, signed on 2026-10-19.

### Changed

- `EUID` (EU-Indonesia CEPA) is `signed` (2026-11-21), and `EUKR-DIGITAL` (EU-Korea
  Digital Trade Agreement) is `signed` (2026-06-10).
- `EUAU`, `EUIN`, `EUMY` and `EUTH` now have notes with the dates when negotiations were
  concluded, paused or resumed, as the European Commission gives them. These records,
  `EUID`, `EUKR-DIGITAL` and `EUCL` are now `verification: official`.
- `EUCL` is named `EU-Chile Interim Trade Agreement`.

### Fixed

- `EUWESTAFRICAEPA`: the regional EU-West Africa EPA is `signed`, not `in_force`.
  - The intblock no longer has the `active_period` start of 2016-12-15. That date
    belongs to the Côte d'Ivoire and Ghana stepping-stone EPAs (`EUCI`, `EUGH`).
  - The 13 West African signatories listed by the European Commission are now `member`,
    not `partner`. Nigeria, which has not signed, stays `partner`.
