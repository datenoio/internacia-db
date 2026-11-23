### Fixed

- `IBRD`, `IDA`, `MIGA` and `ICSID` list their members with a `joined` date per entry,
  checked on 2026-11-23. The dates come from the World Bank Group member countries list
  and, for ICSID, from ICSID's own list of Contracting States and signatories (ICSID/3,
  as of 16 August 2026). The `IBRD` (189) and `MIGA` (182) rosters already matched.
- `IDA` lists 175 members, adding Bulgaria (2021) and Suriname (2024). Poland has no
  `joined` date: the official list gives 1960, but Poland was not back in IBRD until
  1986, and IDA's Board of Governors adopted its membership resolution in 1987.
- `ICSID` lists 159 Contracting States, adding ten: Angola, Djibouti, Ecuador, Equatorial
  Guinea, Georgia, Iraq, Kosovo, the Kyrgyz Republic, Mexico and Nauru. Bolivia (left
  2007) and Venezuela (left 2012) are `former_member` entries. The record's
  `founding_members` are now the 20 States for which the Convention entered into force
  on 14 October 1966. Its notes name the seven States that signed but have not ratified.
- China's IBRD and IDA dates have a note: they are from when the Republic of China held
  China's seat, which passed to the People's Republic of China in May 1980. Vietnam's
  dates have a note that the Socialist Republic of Vietnam took over the Saigon
  government's membership in 1976. `MIGA` notes that Switzerland was a founding member
  before it joined IBRD in 1992. It also says that seven IBRD members are not MIGA
  members, not six: Nauru was missing.
