### Added

- 46 trade agreement records from the OAS Foreign Trade Information System (SICE), checked
  on 2026-11-23 (`scripts/oneoff/import_sice.py`): ALADI complementation and partial scope
  agreements (ACE 14, 16, 57, 58, 59, 72; AAP.A25TM 22, 23, 29, 38, 41, 42; ACE 54 and 55
  with Mexico), free trade agreements never notified to the WTO (`ARCL`, `BRCL`, `CLUY`,
  `CLPY`, `CLEC`, `CREC`, `AECR`, `AECL`, `GTIL`, `GTPE`, `PYTW`), signed agreements
  (`AECO`, `COPA-2013`, `ILPA`, `PATT`, `MERCOSURPA`) and current negotiations (`BZSV`,
  `CLTT`, `CRIL`, `DOEC`, `AEEC`, `AEPE`, `PESV`, `MERCOSURAE`, `INUS`, `GCCCL`). Entry into
  force per pair of parties is kept as party `in_force` dates; ALADI codes are `acronyms`.
