### Added

- `TLATELOLCO` (Treaty of Tlatelolco, Wikidata Q1567567), the treaty record for the Latin
  American and Caribbean nuclear-weapon-free zone: 33 States Parties with deposit dates from
  the UNODA Treaties Database, checked on 2026-11-22. `OPANAL` is now `partof` it.

### Changed

- Nuclear arms-control treaties `NPT`, `CTBT`, `TPNW`, `PELINDABA`, `RAROTONGA`, `BANGKOK`
  and `SEABEDTREATY` move from `agreement` to `armscontrol` as primary blocktype, as the
  `agreement` description requires. They keep `agreement` and add `nuclear`.
- `NSG` (from `energy`), `OPANAL` (from `energy`), `ZANGGERCOM` (from `forum`) and `AG`, the
  Australia Group (from `political`), move to `armscontrol`.
- The `nuclear` blocktype now covers nuclear security and non-proliferation, not only energy
  and safety. It is added as a secondary tag to `IAEA`, `CTBT`, `CTBTO`, `NEA`, `KEDO`, `NSG`,
  `ZANGGERCOM`, `OPANAL`, `GICNT`, `NSS`, `JCPOA`, `NWS`, `NWFZ` and the nuclear-weapon-free
  zone treaties. `NSS`, `ISTC` and `STCU` also gain `armscontrol`.
- `scope_category`: `NSG` is a `policy_forum` (a group of supplier countries, not an IGO).
  `OPANAL` is an `igo` established by Article 7 of the treaty, no longer a `treaty_body`.
  `NWS` and `NWFZ` are `reference_enumeration`, applying the reviewed decisions in
  `scope_category_nonformal_30.yaml`. `WANO` and `WNA` are `non_state_organization` and leave
  the `igo` legal-status allowlist.

### Fixed

- `IAEA` listed 8 of its members. It now lists all 182 member states with membership dates
  (IAEA INFCIRC/2/Rev.94), North Korea as a former member (withdrew 1994) and Palestine as an
  observer.
- `CTBT` listed every signatory as a member. It now lists the 179 States Parties with deposit
  dates. The Russian Federation is a `former_member` since it withdrew its ratification on
  3 November 2023, and the 8 signature-only states are omitted, as for other treaties.
- `CTBTO` listed 195 states, including non-signatories (India, Pakistan, North Korea, Saudi
  Arabia, Syria and others). It now lists the 188 CTBT signatories that make up the
  Preparatory Commission, with signature dates.
- `WANO` and `WNA` no longer present countries with nuclear plants or member companies as
  member states. Their members are operators and companies, so the records have no country
  roster (`membership_applicability: not_applicable`).
