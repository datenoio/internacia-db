### Added

- 19 `trade_agreements` records from the China FTA Network of China's Ministry of Commerce
  (MOFCOM), checked on 2026-11-23, all `verification: official`:
  - `CNHN` (China-Honduras FTA early harvest arrangement, in force from 1 September 2024),
    `CNSV` (China-El Salvador FTA, negotiating), `CNPS` (China-Palestine FTA, negotiating) and
    `CNUY` (China-Uruguay FTA, joint feasibility study completed in 2022);
  - eight China-Pacific Island country framework agreements on enhanced economic partnership
    signed in 2025-2026: `CNFM`, `CNKI`, `CNNR`, `CNVU`, `CNFJ-EEPA`, `CNTO`, `CNPG-EEPA`,
    `CNSB`;
  - China-Africa economic partnership for shared development: early harvest arrangements with
    Kenya (`CNKE`) and Seychelles (`CNSC`, both signed), the concluded Gabon negotiations
    (`CNGA`), and framework agreements with South Africa (`CNZA`), Nigeria (`CNNG`), Namibia
    (`CNNA`) and Cabo Verde (`CNCV`).
- `scripts/oneoff/import_mofcom_fta.py`, the curated import that wrote these changes.

### Changed

- `CGCN` and `BYCN` take their official names (the China-Republic of the Congo early harvest
  arrangement and the China-Belarus Agreement on Trade in Services and Investment), keep the WTO
  RTA-IS names as other names, and are now `verification: official`.
- Notes on upgrade protocols and early harvest arrangements from MOFCOM releases: `ACFTA`
  (versions 2.0 and 3.0), `CHCN`, `CLCN`, `CNGE`, `CNKR` (second phase), `CNNI`, `CNNZ`,
  `CNPE`, `CNPK`, `CNSG`, and `SACUCN`; joint feasibility study dates on `CACN`, `CNCO`, `CNFJ`,
  `CNMN` and `CNNP`.
- MOFCOM topic pages added as links to 31 China records.
- `HNSVTW`: El Salvador's party row records its exit on 7 November 2022.

### Fixed

- Dead MOFCOM links on `CNKR` (`/korea/korea_special.shtml`) and in the `CNRS` provenance
  (`/english/fta_qianshu.shtml`).
