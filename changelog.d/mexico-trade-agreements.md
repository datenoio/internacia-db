### Added

- Six Mexico trade agreement records, checked on 2026-11-23 against the Secretaría de Economía's
  list of Mexico's agreements, the Diario Oficial and partner governments:
  - `GBMX-FTA` (new Mexico-UK free trade agreement, negotiations launched 2022-05-20) and
    `ECMX-FTA` (Ecuador-Mexico Productive Integration Agreement, nine rounds from 2020 to 2022),
    both `negotiating`.
  - `MXTR-TRA` (1998 Mexico-Türkiye economic and commercial cooperation agreement, in force
    2001-02-02 per the Diario Oficial promulgation decree).
  - `EUMX-TRA` (1975 EEC-Mexico agreement with most-favoured-nation treatment) and `EUMX-FCA`
    (1991 framework agreement for cooperation, superseded by `EUMX` from 2001-02-27), with dates
    from EUR-Lex Cellar.
  - `MXUS-TRA` (1942 US-Mexico Reciprocal Trade Agreement, in force 1943-01-30, ended after
    1950-12-31).
- Intblocks of bodies of which Mexico is a member, each roster taken from the body's own site, its
  founding text or the depositary, checked on 2026-11-23:
  - North America: `NAPPO` (North American Plant Protection Organization), `CEC` (Commission for
    Environmental Cooperation), and the US-Mexico `NADB` (North American Development Bank) and
    `IBWC` (International Boundary and Water Commission).
  - Mesoamerica and migration: `TUXTLAMECHANISM` (Tuxtla Mechanism for Dialogue and Concertation,
    10 members with dates of joining), `MESOAMERICAPROJECT` (Mesoamerica Integration and
    Development Project, formerly Plan Puebla-Panamá), `OIRSA` (Organismo Internacional Regional de
    Sanidad Agropecuaria) and `RCM` (Regional Conference on Migration, Puebla Process; 11 members
    and 5 observers).
  - Latin American political forums: `CONTADORAGROUP` (1983-1986, historical), `LIMAGROUP` (2017
    Lima Declaration; Mexico and Argentina as former members), `UFC` (Uniting for Consensus) and
    `ARCOPACIFICO` (Latin American Pacific Arc Forum, 11 members, no meeting found after 2010).
  - Inter-regional and trade: `FEALAC` (36 members with dates of entry), `EULACFOUNDATION` (EU-LAC
    International Foundation, 61 members), `APEP` (Americas Partnership for Economic Prosperity),
    `MPIA` (WTO Multi-Party Interim Appeal Arbitration Arrangement, 35 participants with joining
    dates) and `G20WTO` (the WTO G-20 group in the agriculture negotiations).
  - Institutions: `CEMLA` (Center for Latin American Monetary Studies, central banks),
    `CISS` (Inter-American Conference on Social Security), `FLACSO`, `IILA` (Italian-Latin American
    International Organization, with entry-into-force dates) and `ILCE` (Latin American Institute of
    Educational Communication).
- Mexico in `EBRD` (a shareholder in the constituency of Spain) and in `G-77` as a former member
  (signatory of the 1964 Joint Declaration, not on the current roster).

### Changed

- `EUMX` lists `EUMX-FCA` in `supersedes`.
- Lineage: `RIOGROUP.predecessor` is `CONTADORAGROUP`, and `PACIFICCORRIDOR` is part of
  `MESOAMERICAPROJECT`, itself part of `TUXTLAMECHANISM`.
- `G-3` (Colombia-Mexico FTA, AAP.CE 33) carries the WTO RTA id 649, the DTA id 188 and the 2010
  amending protocol that were on `COMX`.
- `EFTAMX` notes the July 2026 commitment to modernise the agreement and the restart of negotiations
  with a technical round on 4-6 November 2026.

### Removed

- `COMX`, a second record of the Colombia-Mexico FTA (AAP.CE 33) created from the WTO RTA-IS entry
  "Colombia - Mexico", which is the Group of Three agreement after Venezuela's withdrawal in 2006.
  Use `G-3`: `SELECT * FROM trade_agreements WHERE id = 'G-3'`. The registry has no alias table,
  so the old id no longer resolves.
