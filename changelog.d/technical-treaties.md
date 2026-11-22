### Added

- 27 technical multilateral treaties as `treaty_body` records, each with its states-parties
  roster from the depositary, checked on 2026-11-22:
  - WIPO-administered (`patent`, roster from WIPO Lex): `PARIS1883` (Paris Convention),
    `BERNE1886` (Berne Convention; `BERNECONVENTION` stays the wildlife convention), `PCT`,
    `MADRIDPROTOCOL`, `HAGUEAGREEMENT`, `BUDAPESTTREATY`, `LISBONAGREEMENT` (1958 Agreement),
    `MARRAKESHVIP`, `WCT` and `WPPT`.
  - IMO (`maritime`, roster from the IMO Status Book of 30 October 2026): `STCW`, `COLREG`,
    `LL1966`, `SAR1979`, `FAL1965`, `BWM`, `HKC` (in force since 2025-06-26) and `CLC1992`
    (the 1992 Protocol to the Civil Liability Convention).
  - ICAO (`aviation`, roster from the ICAO lists of parties): `MONTREAL1999`, `CAPETOWN2001`
    (count checked against the UNIDROIT status page), `IASTA`, `TOKYO1963`, `HAGUE1970` and
    `MONTREAL1971`.
  - WCO (`trade`, roster from the WCO positions as regards ratifications): `HSCONVENTION`,
    `RKC` (Revised Kyoto Convention) and `ISTANBUL1990` (Convention on Temporary Admission).
- The European Union, OAPI and the Eurasian Patent Organization are listed as
  `type: organization` parties where the depositary lists them. Signatories that have not
  ratified are left out.
- `CLC1992` and `RKC` have `wikidata_exclusions.yaml` entries, because their Wikidata items
  describe the unamended 1969 and 1973 conventions.
- The Maritime Labour Convention, 2006 is not added: the ILO NORMLEX ratification page could
  not be read.

### Fixed

- `SOLAS` and `MARPOL` rosters follow the IMO Status Book, Vol. I, dated 30 October 2026.
  Both add Kyrgyzstan (`SOLAS` 169, `MARPOL` 163).
- `MARPOL` `joined` dates for Liberia, Mexico, the Netherlands, Poland, Spain, Sweden, the
  United Kingdom, the United States and Uruguay were all `2007-01-09`, which is Albania's date.
  They now carry each State's own date of signature or deposit.
- `SOLAS` `joined` for Monaco and Ukraine is now 1974-11-01, the date of their definitive
  signature, not the date the convention entered into force.
