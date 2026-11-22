### Added

- 66 technical organizations found missing in the `technical` blocktype audit, each with an
  official roster or `membership_applicability: not_applicable`, checked on 2026-11-22:
  - Metrology and standards: `BIPM`, `EURAMET`, `COOMET`, `APMP`, `SIM`, `AFRIMETS`,
    `GULFMET`, `GSO`, `AIDSMO`, `SARSO`, `ISSNIC`.
  - Accreditation: `GLOBALACI` (Global Accreditation Cooperation, formed on 1 January 2026
    from IAF and ILAC), the historical `ILAC`, `EA`, `APAC`, `IAAC`, `AFRAC`, `ARAC`. `IAF`
    now names `GLOBALACI` as its successor.
  - Aviation and maritime: `ASECNA`, `SRVSOP`, `RFIR`, `IOPCFUNDS`, `MOSELLECOM`, and the port
    State control regimes `PARISMOU`, `TOKYOMOU`, `CARIBMOU`, `MEDMOU`, `BSMOU`, `ABUJAMOU`,
    `RIYADHMOU`.
  - Telecom, broadcasting and digital: `RCCCOMM`, `CITEL`, `ABU`, `ASBU`, `DCO`, and the
    regulator networks `CRASA`, `WATRA`, `AREGNET`, `BEREC`, `REGULATEL`, `FRATEL`,
    `EAPEREG`, `ASMG`.
  - Nuclear and power grids: `EURATOM`, `ENSREG`, `WENRA`, `FNCA`, `ABACC`, `GCCIA`, `CRIE`.
  - Meteorology, Earth observation and geospatial: `GEO`, `AGRHYMET`, `ICPAC`,
    `TYPHOONCOMMITTEE`, `WMOESCAPPTC`, `UNGGIM`, `RCMRD`, `AFRIGIST`, `PAIGH`.
  - Scientific and technical cooperation: `ICGEB`, `COMSTECH`, `GOIC`, `CYTED`, `IIR`,
    `CIEC`, `PIARC`.
- `CCASG` lists `GOIC` and `GSO` among its suborganizations.

### Changed

- `technical` blocktype now also tags the six bodies whose `institutional_design.mandate`
  is `technical` (`ICAO`, `IMO`, `ITU`, `UPU`, `WIPO`, `WMO`), `IEC` (as `ISO` already
  was), and the technical-cooperation bodies `CFTC`, `CP` (Colombo Plan) and `SPC`, which
  also gains `scientific`.
- Primary blocktype moved to the domain the taxonomy notes prescribe: `SOLAS` to
  `maritime` (was `transport`), `NSG` and `ZANGGERCOM` to `armscontrol` (were `energy` and
  `forum`), `IPCC` to `climate` (was `research`), and `CP` to `development` (was
  `economic`). `MARPOL` adds `maritime`, `CEPT` adds `telecom`, `NEA`, `NSG` and
  `ZANGGERCOM` add `nuclear`, and `IPCC` adds `scientific`.

### Fixed

- `scope_category` was `igo` on records whose own `legal_status` says they are not
  intergovernmental organizations. Industry associations, NGOs and operator bodies are now
  `non_state_organization`: `WNA`, `WANO`, `WEC`, `IGA`, `IHA`, `WBA`, `WWEA`, `GEIDCO`,
  `FUTURECOAL`, `ENTSOE`, `NORDEL`, `NAERC` (NERC), `AICEP`, `IPC` and `POSTEUROP`.
  Forums and agency coordination groups without IGO personality are now `policy_forum`:
  `CEM`, `MI`, `IPEEC`, `EEHUB`, `NSG`, `CCSDS`, `CEOS` and `CGMS`. `IPCC`, a body of
  WMO and UNEP, is now `intergovernmental_body`.
- `IGAD`: Eritrea is a `former_member` (joined 1993, left 2025-12-12). IGAD acknowledged its
  withdrawal on 12 December 2025, so `membership_count` is now 7.
- `IGAD`: Sudan's entry notes its suspension on 20 January 2024 and its return on
  9 February 2026; it stays a `member`.
- `ISA` (International Solar Alliance): the roster grows from 9 to 114 current members, compiled
  from the Netherlands treaty database's parties tables for the Framework Agreement and its
  amendment, with ratification dates where shown. Brazil, which has signed but not ratified,
  is no longer listed as a member; the United States stays a `former_member`.
