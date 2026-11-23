### Added

- 30 trade agreement records for agreements that the DESTA (Design of Trade Agreements) v2.3
  list of treaties has and the registry lacked, checked on 2026-11-23
  (`scripts/oneoff/match_desta.py`, `scripts/oneoff/import_desta.py`). Status and dates come
  from ALADI, a party government or the WTO, never from DESTA: four historical ALADI
  agreements of 1982 to 1985 that ended on a fixed date, the UAE CEPAs with Israel, Serbia,
  Mauritius, Kenya and the Central African Republic, Egypt - Serbia, Lebanon - Türkiye,
  Jordan's agreements with Kuwait, Sudan and Algeria, Switzerland - Faroe Islands, the
  France - Monaco customs convention, Latvia - Ukraine, four southern African bilaterals from
  WTO trade policy reviews (Malawi - Mozambique, Mozambique - Zimbabwe, Botswana - Zimbabwe,
  Malawi - South Africa) and nine Arab bilaterals from the WTO reviews of Egypt, Morocco and
  Tunisia (`EGSY`, `EGLY`, `EGLB`, `EGIQ`, `EGMA`, `EGTN`, `SYTN`, `LYTN`, `MATN`).
- A DESTA match report: `docs/history/desta-match-2026-11-23.md` and a per-treaty CSV with the
  matched, ambiguous and missing groups, the held agreements and the party-history gaps that
  DESTA's accession and withdrawal rows suggest.
