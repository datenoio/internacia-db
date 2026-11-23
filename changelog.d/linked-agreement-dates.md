### Fixed

- Dates of 14 trade agreement records linked to an intblock. Their exported dates (taken from
  the intblock, or from ADB ARIC or Wikipedia) differed from WTO RTA-IS. Each was checked on
  2026-11-23 against the treaty text, the depositary, the secretariat or a party government,
  and each record now sets its own dates:
  - in force: `ACFTA` 2005-01-01, `AfCFTA` 2019-05-30, `CACM` 1961-06-04, `CAN` 1969-10-16,
    `MERCOSUR` 1991-11-29, `SADCFTA` 2000-01-25, `UEMOA` 1994-08-01;
  - signed and in force: `AFTA` 2009-02-26 and 2010-05-17 (ATIGA), `CEFTA` 2006-12-19 and
    2007-07-26, `COMESA` 1993-11-05 and 1994-12-08, `EAC` 1999-11-30 and 2000-07-07, `EFTA`
    1960-01-04 and 1960-05-03, `EUCU` 1957-03-25 and 1958-01-01 (EEC Treaty), `SACU`
    2002-10-21 and 2004-07-15.
- `AKFTA`, `CEMAC`, `ECOTA` and `MSGTA` keep their dates; their notes record the different
  date or instrument that WTO RTA-IS gives.
- `wto_rta_id: 128` moves from `ECOTA` to a new catalogue record, `ECOPTA-1992`. WTO RTA 128
  is the ECO Additional Protocol on Preferential Tariffs, signed at Tehran on 17 February 1992
  by Iran, Pakistan and Turkey (GATT document L/7047), not the 2003 ECO Trade Agreement, which
  WTO RTA-IS lists no notification of.
- `akfta.asean.org` now serves an unrelated gambling page. The `AKFTA` intblock and record
  link a 2021 Wayback Machine copy of the ASEAN–Korea FTA page instead.
