### Fixed

- `GFDRR` (Global Facility for Disaster Reduction and Recovery) roster and metadata, checked on
  2026-11-21 against the GFDRR Annual Reports 2024 and 2025 on World Bank Documents & Reports.
  `includes` now has 11 `member` entries: AU, AT, CA, DE, IT, JP, NO, SE, CH, US and the EU.
  IN, LU and RS are not in either report's partner list, so they are now `former_member`
  (exit dates unknown), and `membership_count` drops from 14 to 11. The record gains the
  `fund` blocktype and `partof: WB`. It also gains `geographic_scope`, `regions`,
  `active_period`, `legal_status`, `recognition_status`, `secretariat`, `social_media`,
  `official_documents` and `notes` (governance, Umbrella Program trust funds, FY2025 figures).
  The description is rewritten and `provenance` is extended. GFDRR adds one row to the
  `membership_count` mismatch recipe in `docs/query-examples.md`.
- `CDRI` (Coalition for Disaster Resilient Infrastructure) roster and metadata, checked on
  2026-11-21 against cdri.world (About page, Charter and Leadership team). The Philippines
  (`PH`, joined 2026-09) is added, so `membership_count` goes from 58 to 59 member countries.
  ECOWAS gets `joined: '2026-02'`. The site now reports 13 partner organizations but shows
  logos for only 12, so the 13th is not mapped. The record gains French and Spanish
  `languages` and links. It also gains `other_names` (fr, es, ar, zh), `social_media`
  (X, LinkedIn, YouTube, Facebook), `official_documents` (the amended Charter in three
  languages and the 2024–25 Annual Report) and the `sustainable_development` topic. `notes`
  now covers governance under the Charter, the co-chairs and IRAF. The description is
  rewritten and `provenance` is extended.
