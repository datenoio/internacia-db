### Added

- Eleven `trade_agreements` records from the Global Affairs Canada agreements table, checked on 2026-11-23 (`verification: official`):
  - `CAEC` (Canada-Ecuador FTA, signed 2026-07-24) and `AECA` (Canada-UAE CEPA, signed 2026-10-27).
  - `CADO` (Dominican Republic), `CATR` (Türkiye) and `MERCOSURCA` (Mercosur), all `negotiating`.
  - `PACALLCA` (Pacific Alliance), `CARICOMCA` (CARICOM), `CAGTNISV` (Guatemala, Nicaragua and El Salvador), `CAMA` (Morocco) and `CAGB-FTA` (the comprehensive Canada-UK FTA), all `abandoned`, which Global Affairs Canada lists as "8. Inactive".
  - `TISA` (Trade in Services Agreement, 23 parties with the EU as one), `services`, `abandoned`.

### Changed

- `CAJP` and `CASG` are now `abandoned`. Global Affairs Canada lists both negotiations as inactive: Japan's last round was in November 2014, and Singapore's talks have been on hold since November 2009.
- `CAPH` and `CATH` are now `negotiating`, not `proposed`. The Canada-Philippines negotiations were launched on 2025-10-26 and concluded on 2026-11-14.
- `CAIN` is renamed "Canada-India Comprehensive Economic Partnership Agreement", after the November 2025 relaunch.
- `ASEANCA` notes the substantial conclusion of negotiations on 2026-11-15.
- `ASEANCA`, `CAID`, `CAIN`, `CAJP`, `CAPH`, `CASG` and `CATH` move from `catalogue` to `official`.

### Fixed

- `CAID` (Canada-Indonesia CEPA) `signed` is 2025-09-24, not 2024-12-02. ADB ARIC gave the date negotiations were concluded. Global Affairs Canada gives entry into force on 2026-12-01; this is recorded in the notes.
