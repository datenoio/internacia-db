### Added

- The WTO RTA Information System export of 2026-11-22 is imported into the trade agreements
  registry by `scripts/oneoff/import_wto_rtais.py`. Every in-force and inactive RTA that was not
  recorded yet is a new record: 347 `verification: catalogue` records with the parties that WTO
  lists, and five records linked to existing intblocks (`CCASG`, `ECOWAS`, `EEA`, `ALADI` and
  `CARICOM`). An inactive agreement has status `terminated`, or `superseded` with
  `superseded_by` when its successor is known, and the WTO inactive date as `ended`.
- 259 existing registry records now have `wto_rta_id`. Accession rows (EC enlargements, COMESA,
  EAEU, CPTPP and others) map to the agreement that they join.

### Changed

- Ten ADB ARIC catalogue records take the WTO RTA-IS status: `AMRU`, `KGRU`, `KZRU`, `RUTJ` and
  `NITW` are terminated; `GTTW`, `CNMV`, `ILVN`, `HKPE` and `INNZ` are in force. `GBGE` and
  `GBUA` have type `fta` instead of `other`.
- ARIC catalogue records that give only a year, or no date, take the full WTO date of
  signature or entry into force.
