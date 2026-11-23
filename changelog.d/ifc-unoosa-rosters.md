### Fixed

- `IFC` (International Finance Corporation) lists the 186 member countries of the World
  Bank Group member list, each with its date of membership, checked on 2026-11-23. The
  record had 195 entries. It drops Taiwan and eight entries that are not IFC members:
  Andorra, American Samoa, Aruba, Bermuda, the Cook Islands, Hong Kong, Macao and Nauru.
  It also drops St. Vincent and the Grenadines and adds Portugal, a member since 1966.
  China's entry has a note: its 1969 date is from when the Republic of China government
  in Taipei held China's seat, which passed to the People's Republic of China in May 1980.
  Vietnam's 1967 date has a note too: the government in Saigon held the seat then, and the
  Socialist Republic of Vietnam took over that membership in 1976. The Dominican Republic
  stays a founding member, with its current membership dated 1961-10-31.
- `UNOOSA` (United Nations Office for Outer Space Affairs) no longer has member states.
  It is a unit of the UN Secretariat, so it is now an `intergovernmental_body` with
  `partof: UN` and `membership_applicability: not_applicable`. Its description now comes
  from the Office's own site. Its 195 entries had been the UN Member States without
  Denmark, plus the Cook Islands, Niue and Taiwan. The 110 States members of the
  Committee that the Office serves are on the `COPUOS` record.
