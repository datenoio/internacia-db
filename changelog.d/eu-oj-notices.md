### Added

- Records for the Interim Agreements that applied the trade provisions of the Stabilisation
  and Association Agreements and of the EU-Lebanon Association Agreement until those entered
  into force: `EUAL-2006`, `EUMK-2001`, `EUME-2007`, `EUBA-2008`, `EURS-2008` and `EULB-2002`
  (`superseded`). Also the Europe Agreements with Estonia, Latvia and Lithuania
  (`EUEE-1995`, `EULV-1995`, `EULT-1995`, in force 1998-02-01 to 2004-05-01). Checked against
  Official Journal notices and EUR-Lex metadata on 2026-11-23.

### Changed

- EU trade agreements now separate provisional application from entry into force, using Official
  Journal notices:
  - Applied provisionally only, so `in_force` is now empty: `CETA`, `EUCI`, `EUGH`,
    `EUCENTRALAFRICAEPA`, `EUESAEPA`, `EUSADCEPA`, `EUCARIFORUMEPA`, `EUPACIFICEPA` and the
    `EUMERCOSUR` interim agreement.
  - `in_force` is now the definitive date and `provisional_application` the earlier one:
    `EUKR` (2015-12-13), `EUUA` (2017-09-01), `EUGE` and `EUMD` (2016-07-01), `EUAM`
    (2021-03-01), `EUANDEAN` (2024-11-01), `EUCENTRALAMERICA` (2024-05-01) and `EUCL-2002`
    (2005-03-01).
- `EUAL`, `EUMK`, `EUME`, `EUBA`, `EURS` and `EULB` now carry the entry into force of the
  Stabilisation and Association Agreement or Association Agreement itself. The earlier trade
  date belongs to the new Interim Agreement record.
- `EUEE`, `EULV` and `EULT` (the 1994 free trade agreements) are `superseded` by the Europe
  Agreements and ended on 1998-02-01.
- `EUCENTRALAMERICA` and `EUANDEAN` intblocks note when trade provisions began to apply for each
  partner.
