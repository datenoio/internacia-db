### Added

- Four Swiss trade agreements from Fedlex, checked on 2026-11-23:
  - `CHLI`, the Switzerland-Liechtenstein Customs Treaty (`customs_union`, in force since
    1924-01-01);
  - `EUCH-AGRI`, the EU-Switzerland Agreement on Trade in Agricultural Products (Bilaterals I,
    in force since 2002-06-01; Liechtenstein included from 2007-09-27);
  - `CHGB-FSA`, the Berne Financial Services Agreement with the United Kingdom (`services`, in
    force since 2026-01-01);
  - `CHGB-MOBILITY`, the UK-Switzerland Services Mobility Agreement (`services`, in force since
    2021-01-01).

### Changed

- `CHCN`, `CHJP` and `CHFOLI` are `official`, with Fedlex links and provenance (dates
  unchanged).
- `EFTAEE`, `EFTALV` and `EFTALT` give Switzerland's own entry into force (1997-10-01 and
  1997-08-01). `EFTAEE` now lists Switzerland as a party.

### Fixed

- The 1992 Swiss free trade agreements with Estonia, Latvia and Lithuania (`CHEE`, `CHLV`,
  `CHLT`) entered into force in March 1994, not on 1993-04-01, and ended in 1997, when the EFTA
  agreements took effect for Switzerland. They are now `superseded` by `EFTAEE`, `EFTALV` and
  `EFTALT`.
