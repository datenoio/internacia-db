### Added

- `EURATOM` (European Atomic Energy Community, Wikidata Q8919), an `energy`/`nuclear`/`research`
  `igo` with its own legal personality, `partof` `EU`: 27 member states with accession dates and
  the United Kingdom as a former member (1973–2020), checked on 2026-11-22.
- `PTBT` (Partial Nuclear Test Ban Treaty, Wikidata Q278960): 125 States Parties, each with the
  earliest deposit date at any of the three depositaries, from the UNODA Treaties Database,
  checked on 2026-11-22.
- `CANWFZ` (Central Asian Nuclear-Weapon-Free Zone Treaty, Wikidata Q501371): 5 States Parties
  with deposit dates from the UNODA Treaties Database, checked on 2026-11-22.
- `ABACC` (Brazilian-Argentine Agency for Accounting and Control of Nuclear Materials, Wikidata
  Q290585), an `igo` founded on 18 July 1991 with Argentina and Brazil as founding members.
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

### Fixed

- `ITER` listed its European Member as `EU` ("European Union (through Euratom)"), and `KEDO`
  listed it under the unresolved id `EAEC`. Both now reference `EURATOM`.
