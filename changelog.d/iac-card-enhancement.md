### Changed

- `IAC` (Interstate Aviation Committee) roster checked on 2026-11-21 against the IAC website
  (nine participating states as of January 2026) and the 1991 Minsk Agreement on Civil Aviation
  and on the Use of Airspace. `membership_count` drops from 12 to 9: `UA` becomes
  `former_member` with `left: 2021-02-23` (Presidential Decree No. 70/2021), and `GE` and `MD`
  become `former_member` without a `left` date, since no formal withdrawal date was found. All
  twelve signatories get `joined: 1991-12-25` and are listed in `founding_members`. `RU` keeps
  `member` with a note on the December 2015 transfer of certification to Russian federal bodies.
  - The headquarters now has its country (`RU`) and the coordinates of 22/2 Bolshaya Ordynka
    Street, Moscow, instead of the city centre. The website moves from the retired `mak.ru` to
    `mak-iac.org`.
  - Acronyms get their Wikidata language tags (`SAK` lv, `DAK` tk, `CIEA` es, `ՄԱԿ` hy). Two
    Chinese aliases tagged as acronyms are dropped. The French `other_names` entry, which was
    the English name, is also dropped.
  - New fields: `founded` as a full date, `founding_members`, `secretariat`,
    `geographic_scope`, `regions`, `legal_status`, `recognition_status`, `official_documents`,
    `notes`, `last_verified`, a full `description`, 20 `other_names` languages, and the
    `aviation`, `accident_investigation`, `certification` and `safety` topics. Field-level
    `provenance` cites the IAC website, the Agreement text, Interfax, Wikidata, Wikipedia and
    OpenStreetMap.
  - The documented query counts move with the roster: one more `membership_count` mismatch
    and three more `former_member` rows with `joined`.
