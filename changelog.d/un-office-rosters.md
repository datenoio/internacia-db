### Fixed

- Nineteen UN offices, funds, programmes and institutes no longer list the 193 UN Member
  States as their members. Each record had a roster copied from the UN membership list,
  with no source for it. They were checked on 2026-11-23 against each body's own site.
- `OCHA`, `OHCHR` and `UNODC` are departments or offices of the UN Secretariat, so they no
  longer have member states. They are now `intergovernmental_body` records with
  `membership_applicability: not_applicable`.
- `ITC` (International Trade Centre) no longer has member states. It is a subsidiary
  agency of UNCTAD and the WTO. It is now an `intergovernmental_body` with
  `membership_applicability: not_applicable`; the members of its two parents are on the
  `UNCTAD` and `WTO` records.
- The UNESCO institutes `IBE`, `IIEP` and `UIL` no longer have member states. Their
  governing boards have individual members, not States. They are now
  `intergovernmental_body` records with `membership_applicability: not_applicable`.
- `UNIGF` (Internet Governance Forum) no longer lists 195 participating countries. The
  list was the UN Member States plus the Holy See and Palestine, not its directory of
  national and regional initiatives. The forum is a multistakeholder forum with no member
  states, so it now has `membership_applicability: not_applicable`.
- These records now list the States on their governing body, from the body's own list:
  - `UNDP`, `UNFPA` and `UNOPS`: the 36 members of their shared Executive Board in 2026.
  - `UNICEF`: the 36 members of its 2026 Executive Board.
  - `UNWOMEN`: the 40 members of its Executive Board in 2026. One seat was still to be
    elected.
  - `WFP`: the 36 members of its Executive Board for 2026.
  - `UNHCR`: the 110 members of its Executive Committee for October 2026 to October 2027.
    The Holy See is one of them.
  - `UNRWA`: the 29 members of its Advisory Commission, each with the year it joined.
    Palestine, the European Union, the League of Arab States and the Organisation of
    Islamic Cooperation are observers.
  - `UNAIDS`: the 22 Member States on its Programme Coordinating Board in 2026.
- `UNEP` and `UNHABITAT` keep their 193 UN Member States, because their governing
  assemblies have universal UN membership. The records now cite the source for this,
  and their descriptions no longer read "Ethnic group.".
