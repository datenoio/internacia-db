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

- 62 EU trade agreements move from `verification: catalogue` to `official`. Their
  signature and entry-into-force dates are checked against EUR-Lex metadata from the
  Publications Office Cellar SPARQL endpoint, and each record cites the CELEX document
  in `provenance` and `links`.
  - `EUGE`, `EUMD`, `EUAM` and `EUCL-2002` keep the provisional-application date in
    `in_force`; their notes give the EUR-Lex date of full entry into force.
  - `EUPH` is confirmed by the Commission's negotiations overview.
- 14 EU records stay `catalogue`: EUR-Lex gives different dates, and their notes quote
  the EUR-Lex values for review. They are `EUAT`, `EUCI`, `EUCZSK`, `EUSI`,
  `EUSI-1996-2`, `EUEE`, `EULT`, `EULV`, `EUEG-1972`, `EULB-1972`, `EULB-1977`, `EUAD`,
  `EUMX` and `EUTR`.

### Fixed

- Dates corrected to EUR-Lex:
  - `EUIS` signed 1972-07-22 (was 1972-12-19);
  - `EUTN` signed 1995-07-17 (was 1995-07-07);
  - `EUFI` ended 1995-01-01 (was 1994-01-01);
  - `EUPT` ended 1986-01-01 (was 1976-01-01).
- `EUDZ-1976` and `EUSY` now describe the 1976 and 1977 Cooperation Agreements.
  - Their `in_force` is 1978-11-01; they had the date of the matching Interim
    Agreements (`EUDZ-1976-2`, `EUSY-1977`).
  - They are renamed to `EC - Algeria Cooperation Agreement` and
    `EC - Syria Cooperation Agreement`.
- `EUTR-1963` (Ankara Agreement) and `EUTR-1970` (Additional Protocol) are `in_force`,
  not `terminated`, and no longer have an `ended` date. EUR-Lex records both as valid
  with no end of validity. WTO RTA-IS had ended them on 1973-01-01 and 1974-01-01, the
  dates of the following instruments. Both are now `verification: official`.
- `EUTR-1973` is the 1973 EC-Turkey Interim Agreement consequent on enlargement, now
  named `EC - Türkiye Interim Agreement of 1973`, and is `verification: official`. It
  ended on 1986-03-01, not 1996-01-01: EUR-Lex gives end of validity on 1986-02-28,
  when the Supplementary Protocol signed the same day entered into force.
- `EUZA` is the EC-South Africa Trade, Development and Cooperation Agreement. It is now
  `superseded` by `EUSADCEPA`, ended 2016-10-10. The SADC EPA repealed its trade
  component when it entered into provisional application in October 2016.

- `EUWESTAFRICAEPA`: the regional EU-West Africa EPA is `signed`, not `in_force`.
  - The intblock no longer has the `active_period` start of 2016-12-15. That date
    belongs to the Côte d'Ivoire and Ghana stepping-stone EPAs (`EUCI`, `EUGH`).
  - The 13 West African signatories listed by the European Commission are now `member`,
    not `partner`. Nigeria, which has not signed, stays `partner`.
