### Added

- `PTBT` (Partial Nuclear Test Ban Treaty, Wikidata Q278960): 125 States Parties, each with the
  earliest deposit date at any of the three depositaries, from the UNODA Treaties Database,
  checked on 2026-11-22.
- `CANWFZ` (Central Asian Nuclear-Weapon-Free Zone Treaty, Wikidata Q501371): 5 States Parties
  with deposit dates from the UNODA Treaties Database, checked on 2026-11-22.
- `AFCONE` (African Commission on Nuclear Energy, Wikidata Q2986403), an `intergovernmental_body`
  `partof` `PELINDABA` that lists the 12 States Parties currently elected to the Commission.
- `UNSCEAR` (Wikidata Q2297408), an `intergovernmental_body` `partof` `UN`, established by General
  Assembly resolution 913 (X) of 3 December 1955: 31 member states with the year each was designated.
- `CONFDISARMAMENT` (Conference on Disarmament, Wikidata Q1931500): 65 member states by regional
  group, from UNODA. The id avoids `CD`, the ISO code of the Democratic Republic of the Congo.
- `PARISNUCLEAR` (Paris Convention on Third Party Liability in the Field of Nuclear Energy,
  Wikidata Q7137274): 16 Contracting Parties with ratification dates. The roster comes from the
  Wikipedia table of the OECD NEA ratification status, because oecd-nea.org blocks automated access.
- Nuclear forums and initiatives, each with its official roster checked on 2026-11-22:
  - `GIF` (Generation IV International Forum, Q1123284): the seven states and Euratom that have
    signed the 2025 Framework Agreement.
  - `IFNEC` (International Framework for Nuclear Energy Cooperation, Q3366107): 33 Participant
    countries, 32 observer countries and 5 observer organizations.
  - `PSI` (Proliferation Security Initiative, Q1141011): 116 endorsing states.
  - `GPWMD` (Global Partnership Against the Spread of Weapons and Materials of Mass Destruction,
    Q5570539): 30 countries and the EU.
  - `IPNDV` (International Partnership for Nuclear Disarmament Verification): 32 partner states
    and the EU. It has no Wikidata item and is listed in `wikidata_exclusions.yaml`.
  - `NPDI` (Non-Proliferation and Disarmament Initiative, Q7048793): 12 members.
  - `NEWAGENDA` (New Agenda Coalition, Q3875176): 6 members. The id avoids `NAC`, which is the
    World Bank North America aggregate.
- IAEA regional agreements and the Arab Atomic Energy Agency, each with its official roster checked on
  2026-11-22:
  - `RCA` (Asia-Pacific, 22 Government Parties).
  - `ARCAL` (Latin America and the Caribbean, 21 members).
  - `ARASIA` (Arab states in Asia, 10 States Party).
  - `AAEA` (Arab Atomic Energy Agency, Q56376750): an `igo` `partof` `LAS` with 14 member states.

  `RCA`, `ARCAL` and `ARASIA` have no Wikidata item and are listed in
  `wikidata_exclusions.yaml`.
- `HCOC` (Hague Code of Conduct against Ballistic Missile Proliferation, Q1566329): 145 subscribing
  states with subscription dates.
- `TRIPLENUCLEAR` (Declaration to Triple Nuclear Energy, Q139072661): the 39 endorsing countries
  listed by the World Nuclear Association (updated 2 October 2026), including Kosovo (`XK`).
- `NUCLEARARMED`, a `reference_enumeration` of the nine nuclear-armed states counted by the SIPRI
  Yearbook 2026. It complements `NWS`, the five NPT nuclear-weapon States.

### Fixed

- `ITER` listed its European Member as `EU` ("European Union (through Euratom)"), and `KEDO`
  listed it under the unresolved id `EAEC`. Both now reference the `EURATOM` record.
