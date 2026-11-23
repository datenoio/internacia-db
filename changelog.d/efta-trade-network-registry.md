### Changed

- 29 EFTA trade agreement records checked on 2026-11-23 against the EFTA free trade
  network partner pages (Wayback Machine copies, because efta.int sits behind a bot
  check), with the WTO RTA-IS ID cards and Fedlex as tie-breakers. Each one now links its
  EFTA page and cites it in `provenance`. 26 records move from `catalogue` to `official`
  verification; `EFTAMD`, `EFTAXK` and `EFTATSOUZ` stay `catalogue`.
- Per-state entry-into-force dates (`parties[].in_force`) for agreements that entered into
  force on different dates for different EFTA States: `EFTAAL`, `EFTACO`, `EFTACRPA`,
  `EFTAMD`, `EFTAME`, `EFTAMERCOSUR`, `EFTAPE`, `EFTARS`, `EFTATN`, `EFTAXK`, `GBISLINO`
  and `EFTASG-DEA`. `EFTAPE` also records Peru's later signature (2010-07-14).
- `EFTAMY` is renamed to EFTA-Malaysia Economic Partnership Agreement (MEEPA).

### Fixed

- `EFTATH` and `EFTAMY` were still `negotiating`; they are `signed` (2025-01-23 and
  2025-06-23).
- `EFTASG-DEA` was still `negotiating`; it was signed on 2025-09-25 and has been in force
  for Norway and Singapore since 2026-03-01.
- `GBISLINO` entry into force is 2022-09-01 (Iceland 2023-02-01). The previous date,
  2021-12-01, was the start of provisional application with Norway.
- Notes on `EFTATSOUZ` (negotiations suspended), `EFTAVN` (negotiations concluded
  2026-07-02, not signed) and `EFTALB` (the EFTA page's 1 July 2007 date conflicts with
  Fedlex and WTO, which give 1 January 2007 for all parties).
