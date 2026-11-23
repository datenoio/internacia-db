### Added

- Seven African bilateral trade agreement records that tralac's country trade profiles name and
  the registry lacked, checked on 2026-11-23 (`scripts/oneoff/import_africa_agreements.py`).
  Status and dates come from a party government or the WTO, never from tralac:
  - Morocco's trade and tariff conventions with Algeria (`DZMA`, 1989), Libya (`LYMA`, 1990),
    Guinea (`GNMA`, signed 1997, in force 2000), Mauritania (`MAMR`, 1986, applied
    provisionally) and Senegal (`MASN`, in force 1968, with its 1987 protocol as an instrument),
    from the Moroccan Ministry of Industry and Trade. Four of them were held in the DESTA walk
    for lack of a date.
  - The 1964 trade agreement between South Africa and Southern Rhodesia (`ZAZW-1964`), in force
    from 1 December 1964 (SARS) and ended on 20 November 2018 (WTO Trade Policy Review of
    Zimbabwe, 2020).
  - The Algeria - Mauritania preferential trade agreement under negotiation since
    4 August 2026 (`DZMR`).
- The five Phase II protocols of the AfCFTA Agreement (investment, competition policy and
  intellectual property rights of 2023; digital trade and women and youth in trade of 2024) as
  `instruments` of `AfCFTA`, with their dates of adoption from the African Union; none is in
  force.

### Changed

- The `AfCFTA` intblock roster now gives each State Party's signature, ratification and deposit
  dates from the African Union status list of 22 May 2026 in `includes[].note`, and the date the
  Agreement entered into force for it in `joined`: 30 May 2019 for the 24 States that deposited
  by then, the date of deposit for later ones, and 4 September 2026 for Somalia. Benin, Libya,
  South Sudan and Sudan have signed and not deposited, and have no `joined` date. Western
  Sahara's `joined` moves from its deposit date to 30 May 2019. Where the AfCFTA Secretariat's
  State Parties table gives other dates (Algeria, Sierra Leone) the entry's note says so.
- The `TFTA` intblock roster gives `joined` 25 July 2024, the entry into force, for the 14
  States that had deposited ratification by then (SADC Secretariat), and no `joined` date for
  the other 15. All 29 had `joined` 10 June 2015, the launch of the agreement.
- `AGOA` and `AGOA-APPAREL` record the 2025 lapse and the extensions through 31 December 2026
  (Public Law 119-75) and through 31 December 2028 (Public Law 119-103, enacted
  2 September 2026); both stay `in_force`.
- `MWZA` gets its signature date, 19 June 1990, from SARS.
