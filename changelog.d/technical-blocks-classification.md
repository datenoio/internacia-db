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
