# Intblock discovery catalogues and roster sources

Catalogues Internacia **searched** when looking for missing international
organizations and treaties, and the authorities used to **compile** membership.
These lists are gap-finding tools. Internacia does **not** import them wholesale —
a candidate still has to meet [intblock-inclusion-policy.md](intblock-inclusion-policy.md).
How to search catalogues and improve existing country / intblock records:
[discovery.md](discovery.md).

Per-record `provenance` and `last_verified` remain the field-level source of
truth. This page records which catalogues were walked, when, and what was kept.

## Discovery catalogues

| Catalogue | URL | Retrieved | What was searched | What Internacia kept |
|-----------|-----|-----------|-------------------|----------------------|
| **UN Treaty Collection** (UNTC) | [treaties.un.org](https://treaties.un.org/) | 2026-09-09 | 560+ multilateral instruments deposited with the UN Secretary-General | Named, in-force treaties with a durable states-parties roster distinct from an existing IGO. Constitutive acts of orgs already recorded (UN Charter, WHO Constitution, Rome Statute, IMO/ICC texts) are not duplicated. Not-in-force instruments and commodity-era pacts are skipped. |
| **WTO RTA Information System** | [rtais.wto.org](https://rtais.wto.org/UI/publicPreDefRepByRTAType.aspx) | 2026-09-09 | ~388 RTAs in force (FTAs, customs unions, partial-scope PTAs, services EIAs) | Named plurilaterals, ASEAN+1, EU and US named FTAs, and bloc-to-bloc deals whose extra parties make a distinct roster. Untitled `Country A – Country B` pairs, UK continuity copies of EU EPAs, and services-only EIA rows of an FTA already recorded are not imported. |
| **WTO Preferential Trade Arrangements Database** | [ptadb.wto.org](https://ptadb.wto.org/ptaList.aspx) | 2026-09-09 | 37 notified non-reciprocal PTA rows (GSP, LDC-only DFQF, waiver programmes) | Named waiver programmes (`AGOA`, `CBERA`, `CARIBCAN`) and the EU GSP+ arrangement (`GSPPLUS`). National GSP ID cards, LDC-only DFQF schemes, and untitled one-country preferences are not imported. |
| **UNCTAD IIA Navigator** (by country grouping) | [investmentpolicy.unctad.org](https://investmentpolicy.unctad.org/international-investment-agreements/by-country-grouping) | 2026-09-09 | 33 country groupings; ~2,861 BITs and ~523 TIPs | Named plurilateral investment treaties with a ratifiers roster distinct from the parent IGO (`OICIA`, `ACIA`, `UAIA`, `CISFTASERVICES`, `CJKIA`, `INTRAEUBIT`, `PCFI`). SADC FIP and the ECOWAS Supplementary Act on Investments stay notes on the parent IGO. Bilateral BITs, FTA investment chapters of records already present, constitutive REC treaties, TIFAs, and not-in-force protocols are not imported. |
| **Wikipedia `.int` organizations** | [List of organizations with .int domain names](https://en.wikipedia.org/wiki/List_of_organizations_with_.int_domain_names) | 2026-09-09 | ~231 named treaty/IGO-style entries with a `.int` site | Standing IGOs missing from intblocks, compiled from each org’s official site (`ALLPI`, `ALSF`, `BOIP`, `CAC`, `CAFRAD`, `CEDARE`, `COMTELCA`, `CTU`, `EACO`, `EASF`, `ECB`, `ECSAHC`, `ECTEL`, `GCAP`, `GLFC`, `IAI`, `ICMP`, `ICPE`, `ICSTI`, `IICAS`, `IGC`, `INCAP`, `INL`, `ISTC`, `IVI`, `JINR`, `OSC`, `RECSA`, `RESPA`, `STCU`, `VPI`, plus earlier `ARC`, Cospas-Sarsat, `CRFM`, `EFI`, `GMCO`, `OIML`, `RIMES`, `UPOV`). Dissolved or non-IGO `.int` holders are skipped. |
| **International road networks and transport corridors** (targeted hunt) | UNTC chapter XI status pages; OAS DIL B-19; SCO Secretariat; ESCAP/ADB/CAREC; corridor-body sites ([ttcanc.org](https://www.ttcanc.org/), [centralcorridor-ttfa.org](https://centralcorridor-ttfa.org/), [tkcmc.com](https://www.tkcmc.com/)); SADC, ECOWAS and UNECA documents | 2026-11-21 | About 60 named road networks, corridors, transit treaties and corridor authorities, duplicate-checked against all intblocks | Treaties with a depositary roster (`ARABMASHREQRAILWAYS`, `PANAMERICANHIGHWAY`, `SCOROADTRANSPORT`, `GMSCBTA`, `QTTA`, `CHABAHAR`), corridor bodies with official member lists (`CCTTFA`, `LCTTFA`, `ALCOMA`, `TKCS`, `CLRT`; `NCTTCA` and `ARABMASHREQROADS` were added separately) and the `GMS` programme. Ashgabat Agreement deferred (conflicting roster, term ended April 2026). Linear corridors without a body or treaty (CPEC, IMEC, Development Road, TEN-T corridors and similar) are left for a sourced `corridor`-role pass; networks with the parent's roster (ASEAN Highway, PIDA, GCC Railway, TEN-T as a network) are skipped. |
| **Linear transport corridors with route roles** (Tier 2 pass) | Government and operator sites; ADB/CAREC, ERIA, IDE-JETRO, JICA; EU (CINEA, Regulation (EU) 2024/1679); SADC, AU-PIDA, AfDB, World Bank; IDB and Proyecto Mesoamérica | 2026-11-21 | About 40 named corridors, each checked for a defined main line with two or more end countries | 20 corridors with `terminal`/`transit` roles, listed in `data/schemas/include_roles_pilot.yaml` (for example `CPEC`, `RAILBALTICA`, `LAPSSET`, `BIOCEANICCORRIDOR`, `PACIFICCORRIDOR`). Branched or undefined routes are deferred in the same manifest: CMREC, the New Eurasian Land Bridge, BCIM, IMEC, the nine TEN-T corridors, Nacala, Beira, the GMS North–South corridor and CAREC corridors 1–6. |
| **Statistics blocktype** (thematic slice) | UNSD CCSA member profiles ([unstats.un.org/unsd/ccsa](https://unstats.un.org/unsd/ccsa/)), IMF [DSBB](https://dsbb.imf.org/), AU treaty list | 2026-11-21 | Statistical IGOs, treaties, data-dissemination standards and regional statistical bodies (about 30 candidates) | `AFRISTAT`, `AFRICANSTATISTICSCHARTER`, `SDDSPLUS`, `SDDS`, `EGDDS`, `CES`, `ESS`; the independent `AITRS` (its members are the statistics offices of the 22 Arab states); and, as `intergovernmental_body` records with no roster of their own and `partof` the parent, `GCCSTAT` (`CCASG`), `SESRIC` (`OIC`), `STATAFRIC` (`AFUNION`), `ISSEA` (`CEMAC`) and `SIAP` (ESCAP, not recorded). The UN Statistical Commission is `UNSTATCOM`, since `UNSC` is the Security Council. Not imported: PARIS21 (no country roster), ISI and IASI (individual or institutional members), the BIS Irving Fisher Committee (central-bank members), regional-commission statistics committees with the parent's roster, and the UN city groups (informal). |
| **AI summit declarations** (thematic slice) | Signatory lists of the summit hosts: [gov.uk](https://www.gov.uk/) (Bletchley, Seoul), [elysee.fr](https://www.elysee.fr/) (Paris), [mea.gov.in](https://www.mea.gov.in/) and [pib.gov.in](https://www.pib.gov.in/) (New Delhi), [government.nl](https://www.government.nl/) and [exteriores.gob.es](https://www.exteriores.gob.es/) (REAIM) | 2026-11-22 | Declarations of the AI summits (Bletchley 2023, Seoul 2024, Paris 2025, New Delhi 2026) and the REAIM summits on military AI (2023, 2024, 2026), with Wayback Machine copies for later endorsements | `BLETCHLEYDECLARATION`, `SEOULAIDECLARATION`, `SEOULAIMINISTERIAL`, `PARISAISTATEMENT`, `PARISAIWEAPONSDECLARATION`, `NEWDELHIAIDECLARATION`, `REAIMCALLTOACTION`, `REAIMPATHWAYS`. The REAIM Blueprint for Action (Seoul, 2024; 61 states) is deferred: its list of endorsing states was only on the closed reaim2024.kr site and was never archived. Summit annexes with the same signatories as the main declaration (Seoul Statement of Intent) are not separate records. |

Inclusion bars for RTAs, PTAs, and IIAs live in
[intblock-inclusion-policy.md](intblock-inclusion-policy.md).

## Roster authorities

Discovery catalogues identify *candidates*. Membership (`includes`) is compiled
from the official roster, not from the catalogue index card alone (WTO warns that
accessions and withdrawals are under-notified).

| Kind | Authority | Typical Internacia use |
|------|-----------|------------------------|
| UN multilateral treaties | UNTC chapter status pages (`treaties.un.org`) and the treaty text | States-parties rosters, dates of consent, entry into force |
| Human-rights treaties | [OHCHR](https://www.ohchr.org/) instrument pages alongside UNTC | Core UN human-rights covenants and optional protocols |
| UNECE instruments | [unece.org](https://unece.org/) treaty and WP.29 pages | Environment protocols, inland transport, vehicle agreements |
| Commercial / trade law | [UNCITRAL](https://uncitral.un.org/), [WIPO Lex](https://www.wipo.int/wipolex/en/), [OAS SICE](https://www.sice.oas.org/) | CISG family, paperless trade, IP and FTA texts |
| Crime / drugs / health | [UNODC](https://www.unodc.org/), [WHO FCTC](https://fctc.who.int/) | UNTOC/UNCAC protocols, narcotics conventions, FCTC |
| International humanitarian law | [ICRC IHL Treaties Database](https://ihl-databases.icrc.org/en/ihl-treaties) | Geneva Conventions and protocol states-parties rosters |
| Disarmament treaties | [UNODA Treaties Database](https://treaties.unoda.org/) and official depositary notices | Biological Weapons Convention and other arms-control party rosters |
| UNESCO conventions | [UNESCO Legal Affairs](https://www.unesco.org/en/legal-affairs) and convention secretariats | World Heritage and cultural-property treaty rosters and deposit dates |
| IMO conventions | [IMO Status of Conventions](https://www.imo.org/en/about/conventions/pages/statusofconventions.aspx) | SOLAS, MARPOL, and other maritime treaty contracting-state rosters; territorial applications are not counted as states parties |
| WTO-notified FTAs | Official treaty text; RTA-IS as a cross-check | ASEAN+1, Agadir, CER, PICTA, EU and US named FTAs |
| EU trade agreements | [European Commission](https://policy.trade.ec.europa.eu/), EUR-Lex | CETA, EU–Japan, EU–UK, EU–Korea, and related partnerships |
| US FTAs and PTAs | [USTR](https://ustr.gov/) and Federal Register | Remaining named U.S. FTAs; AGOA / CBERA beneficiary lists |
| Other PTA grantors | Government of Canada (CARIBCAN); EU GSP regulation (GSP+) | Waiver and GSP+ beneficiary rosters |
| Plurilateral IIAs | OIC COMCEC annex / UNCTAD IIA Navigator (ratifiers); ASEAN Secretariat (ACIA); League of Arab States / UNESCWA; CIS Executive Committee; Council of the EU treaty office; MOFCOM/MOFA treaty texts; Paraguay MFA (MERCOSUR protocols) | OIC Investment Agreement, ACIA, Unified Arab Capital Agreement, CIS services-and-investment FTA, CJK trilateral investment agreement, intra-EU BIT Termination Agreement, Intra-MERCOSUR PCFI |
| Political declarations on AI | The host government's signatory page (gov.uk, elysee.fr, mea.gov.in / pib.gov.in, government.nl, exteriores.gob.es) and the [U.S. Department of State](https://www.state.gov/) for the military AI declaration; Wayback Machine copies date later endorsements | AI summit and REAIM declarations, `MILITARYAIDECLARATION` |
| Statistics | [IMF DSBB](https://dsbb.imf.org/) country lists (its `api/country/getsubscriptiondateInfos` endpoint gives dates); AU treaty status lists; [AFRISTAT member states](https://www.afristat.org/etats-membres-2/); UNECE reports to the UN Statistical Commission; Eurostat and EFTA ESS pages | SDDS Plus, SDDS and e-GDDS participants; African Charter on Statistics parties; AFRISTAT; CES; ESS |
| Standing IGOs (`.int`) | Each organization’s official membership page | ARC, Cospas-Sarsat, CRFM, EFI, GMCO, OIML, RIMES, UPOV, ALLPI, ALSF, BOIP, ECB, GCAP, IVI, JINR, and similar |

**Wikidata** and **English Wikipedia** are used for entity linking (`wikidata_id`)
and names, not as the membership source of truth when an official roster exists.

## How to use a catalogue

Full search-and-improve loop (duplicate checks, hunt patterns, roster repair,
country enrichment): [discovery.md](discovery.md). Agent checklist:
[agents/discover.md](agents/discover.md).

1. Walk the catalogue for named, durable join targets (official acronym, distinct
   roster, in force or a historical predecessor already in the dataset).
2. Check Internacia for an existing `id`, alias, or parent IGO before adding a
   record. Constitutive instruments of an org already present stay off the
   intblock list.
3. Compile `includes` from the official roster or treaty status page. Stamp
   `last_verified` and at least four `provenance` entries (catalogue + roster
   authority).
4. Follow [intblock-inclusion-policy.md](intblock-inclusion-policy.md) for `id`,
   directory/`blocktype`, and `scope_category`.

Worked add walkthrough: [agents/add-intblock-example.md](agents/add-intblock-example.md).

## Related

- [discovery.md](discovery.md) — how to search catalogues and improve records
- [intblock-inclusion-policy.md](intblock-inclusion-policy.md) — what belongs
- [enrichment.md](enrichment.md) — Wikidata completeness and `last_verified` SLA
- [ATTRIBUTION.md](../ATTRIBUTION.md) — licenses for country enrichment sources
- [agents/discover.md](agents/discover.md) — agent discovery checklist
- [agents/contribute.md](agents/contribute.md) — YAML editing checklist
