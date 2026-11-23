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
- Intblocks `EUEACEPA` (`pta`) and `EUADSM` (`fta`), the rosters of those two 3-party
  agreements. The registry records now link to them.
  - `EUEACEPA`: the EU, Kenya and Rwanda are `member`; Burundi, Tanzania and Uganda,
    which have not signed, are `partner`.
  - `EUADSM`: the EU, Andorra and San Marino are `founding_member`, joined 2026-10-19.
  - Neither agreement has a Wikidata item, so both are listed in
    `data/schemas/wikidata_exclusions.yaml`.

### Changed

- `EUID` (EU-Indonesia CEPA) is `signed` (2026-11-21), and `EUKR-DIGITAL` (EU-Korea
  Digital Trade Agreement) is `signed` (2026-06-10).
- `EUAU`, `EUIN`, `EUMY` and `EUTH` now have notes with the dates when negotiations were
  concluded, paused or resumed, as the European Commission gives them. These records,
  `EUID`, `EUKR-DIGITAL` and `EUCL` are now `verification: official`.
- `EUCL` is named `EU-Chile Interim Trade Agreement`.
- 19 EU agreements have notes that tell provisional application apart from full entry
  into force. The dates are not changed: `in_force` keeps the date from which trade
  provisions first applied.
  - The Western Balkans SAAs (`EUAL`, `EUBA`, `EUME`, `EURS`, `EUMK`) get their entry
    into force dates from EUR-Lex. The Commission gives the dates for `EULB`, `EUGE`,
    `EUMD` and `EUAM`.
  - `EUUA` gets the 2025 DCFTA upgrade.
  - `EUCENTRALAMERICA` gets its staggered 2013 provisional application by country and
    full application from 2024-05-01.
  - `EUANDEAN`, `EUCARIFORUMEPA`, `EUPACIFICEPA`, `EUESAEPA`, `EUSADCEPA`, `EUCI`,
    `EUGH` and `EUMERCOSUR` are marked as still provisionally applied.
  - Where the Commission's overview disagrees with the record (Papua New Guinea,
    Namibia, Côte d'Ivoire), the note gives both dates.

### Fixed

- `EUWESTAFRICAEPA`: the regional EU-West Africa EPA is `signed`, not `in_force`.
  - The intblock no longer has the `active_period` start of 2016-12-15. That date
    belongs to the Côte d'Ivoire and Ghana stepping-stone EPAs (`EUCI`, `EUGH`).
  - The 13 West African signatories listed by the European Commission are now `member`,
    not `partner`. Nigeria, which has not signed, stays `partner`.
