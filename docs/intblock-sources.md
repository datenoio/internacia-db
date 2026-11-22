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
| **Technical bodies** (thematic slice) | Each body's official members page or founding instrument: BIPM, EURAMET, COOMET, APMP, SIM, AFRIMETS, GULFMET, GSO, AIDSMO and SARSO sites; global-aci.org and the regional accreditation cooperations; ASECNA, SRVSOP, Roberts FIR, IOPC Funds, Moselle Commission and port State control MoU sites; RCC, CITEL, DCO, ISSN, ABU, ASBU and regulator-network sites; EUR-Lex, ENSREG, WENRA, FNCA, ABACC, GCCIA and the Central American electricity framework treaty; GEO, ICPAC, ESCAP/WMO, UN-GGIM, RCMRD, AFRIGIST and PAIGH sites; ICGEB (with UNTC XIV-7), GOIC, CYTED, IIR, CIEC and PIARC | 2026-11-22 | About 75 technical organizations (metrology, accreditation, standards, aviation, maritime, telecom regulation, nuclear safety, power grids, meteorology, geospatial, technical cooperation) found missing in an audit of the `technical` blocktype | 66 records, including `BIPM`, `GLOBALACI` and its historical predecessor `ILAC`, the six CIPM regional metrology organizations, `ASECNA`, `IOPCFUNDS`, seven port State control regimes, eight telecom regulator networks, `EURATOM`, `ENSREG`, `GEO`, `ICGEB` and `PIARC`. A second pass added the bodies whose own sites could not be read, from Wayback Machine copies of their official pages, founding texts and IGO documents: `SMARTAFRICA` (42 of the 43 announced members could be named), `COMELEC` (1989 statutes, 2018 member page), `ACMAD` (2018 UNECA assessment of the ACMAD archive), `EMERG` (24 authorities, 2023 member page), `IOMOU` (2025 member page), `VINADELMAR` (agreement text in force from 2024) and the historical `ECOMET` (dissolved 2023, successor `EUMETNET`). AIT was skipped because it returned to a national charter in 2012. Treaties (WIPO, IMO and ICAO conventions) were not part of this pass. |
| **Statistics blocktype** (thematic slice) | UNSD CCSA member profiles ([unstats.un.org/unsd/ccsa](https://unstats.un.org/unsd/ccsa/)), IMF [DSBB](https://dsbb.imf.org/), AU treaty list | 2026-11-21 | Statistical IGOs, treaties, data-dissemination standards and regional statistical bodies (about 30 candidates) | `AFRISTAT`, `AFRICANSTATISTICSCHARTER`, `SDDSPLUS`, `SDDS`, `EGDDS`, `CES`, `ESS`; the independent `AITRS` (its members are the statistics offices of the 22 Arab states); and, as `intergovernmental_body` records with no roster of their own and `partof` the parent, `GCCSTAT` (`CCASG`), `SESRIC` (`OIC`), `STATAFRIC` (`AFUNION`), `ISSEA` (`CEMAC`) and `SIAP` (ESCAP, not recorded). The UN Statistical Commission is `UNSTATCOM`, since `UNSC` is the Security Council. Not imported: PARIS21 (no country roster), ISI and IASI (individual or institutional members), the BIS Irving Fisher Committee (central-bank members), regional-commission statistics committees with the parent's roster, and the UN city groups (informal). |
| **Technical treaties** (WIPO, IMO, ICAO and WCO depositary lists) | [WIPO Lex](https://www.wipo.int/wipolex/en/) treaty pages, [IMO Status of Conventions](https://www.imo.org/en/about/conventions/pages/statusofconventions.aspx), [ICAO current lists of parties](https://www.icao.int/secretariat/legal/current-list-of-parties), [WCO Conventions and Agreements](https://www.wcoomd.org/en/about-us/legal-instruments/conventions.aspx) | 2026-11-22 | Technical treaties missing after the technical-blocktype audit: WIPO IP treaties, IMO safety, pollution and facilitation conventions, ICAO private and criminal air law, WCO customs conventions (about 30 candidates) | `PARIS1883`, `BERNE1886`, `PCT`, `MADRIDPROTOCOL`, `HAGUEAGREEMENT`, `BUDAPESTTREATY`, `LISBONAGREEMENT`, `MARRAKESHVIP`, `WCT`, `WPPT`; `STCW`, `COLREG`, `LL1966`, `SAR1979`, `FAL1965`, `BWM`, `HKC`, `CLC1992`; `MONTREAL1999`, `CAPETOWN2001`, `IASTA`, `TOKYO1963`, `HAGUE1970`, `MONTREAL1971`; `HSCONVENTION`, `RKC`, `ISTANBUL1990`. Constitutive instruments of organizations already recorded (Chicago Convention for `ICAO`, the WCO Convention) are not duplicated. The Maritime Labour Convention, 2006 is deferred: ILO NORMLEX refused automated reads. |

| **Netherlands Treaty Database** (multilateral treaties) | [treatydatabase.overheid.nl](https://treatydatabase.overheid.nl/en/Treaty/SearchAdvancedResult?type=Multilateraal) | 2026-11-22 | 3,789 multilateral treaties the Kingdom of the Netherlands signed or joined; amendments and derived acts removed, 176 candidates checked against intblocks and open pull requests | First batch: six HCCH conventions (`APOSTILLE`, `SERVICE1965`, `EVIDENCE1970`, `CHILDABDUCTION1980`, `ADOPTION1993`, `CHILDPROTECTION1996`) and eleven Council of Europe treaties (`MAAC`, `TRANSFERSENTENCED`, `LISBONRECOGNITION`, `CONVENTION108`, `LANZAROTE`, `COETRAFFICKING`, `ECPT`, `ISTANBULCONVENTION`, `FCNM`, `ESC`, `ESCREVISED`). Remaining candidates (UNESCO, IMO, nuclear-safety, IHL protocols, CMS daughter agreements, river commissions, and IGOs such as `BIE`, `UPC`, `TSCG`) are not yet added. Constitutive acts of recorded bodies (ECHR, GRECO), Geneva Conventions I–III (roster as `GCIV`), treaties not in force, and the ILO conventions are skipped. |

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
| IMO conventions | [IMO Status of Conventions](https://www.imo.org/en/about/conventions/pages/statusofconventions.aspx): Status Book (Vol. I and II) and the Ratifications by State workbook | SOLAS, MARPOL, STCW, COLREG, BWM and other maritime treaty contracting-state rosters; the Status Book tables give deposit dates, the workbook is a cross-check; territorial applications are not counted as states parties |
| ICAO air law treaties | [ICAO current lists of parties](https://www.icao.int/secretariat/legal/current-list-of-parties); [UNIDROIT](https://www.unidroit.org/) status pages for the Cape Town instruments | Montreal 1999, Cape Town, IASTA, Tokyo, Hague and Montreal 1971 party rosters; signatures without ratification are left out |
| WCO customs conventions | [WCO Conventions and Agreements](https://www.wcoomd.org/en/about-us/legal-instruments/conventions.aspx) (position as regards ratifications PDFs) | HS Convention, Revised Kyoto Convention and Istanbul Convention Contracting Parties, including the European Union |
| WTO-notified FTAs | Official treaty text; RTA-IS as a cross-check | ASEAN+1, Agadir, CER, PICTA, EU and US named FTAs |
| EU trade agreements | [European Commission](https://policy.trade.ec.europa.eu/), EUR-Lex | CETA, EU–Japan, EU–UK, EU–Korea, and related partnerships |
| US FTAs and PTAs | [USTR](https://ustr.gov/) and Federal Register | Remaining named U.S. FTAs; AGOA / CBERA beneficiary lists |
| Other PTA grantors | Government of Canada (CARIBCAN); EU GSP regulation (GSP+) | Waiver and GSP+ beneficiary rosters |
| Plurilateral IIAs | OIC COMCEC annex / UNCTAD IIA Navigator (ratifiers); ASEAN Secretariat (ACIA); League of Arab States / UNESCWA; CIS Executive Committee; Council of the EU treaty office; MOFCOM/MOFA treaty texts; Paraguay MFA (MERCOSUR protocols) | OIC Investment Agreement, ACIA, Unified Arab Capital Agreement, CIS services-and-investment FTA, CJK trilateral investment agreement, intra-EU BIT Termination Agreement, Intra-MERCOSUR PCFI |
| Statistics | [IMF DSBB](https://dsbb.imf.org/) country lists (its `api/country/getsubscriptiondateInfos` endpoint gives dates); AU treaty status lists; [AFRISTAT member states](https://www.afristat.org/etats-membres-2/); UNECE reports to the UN Statistical Commission; Eurostat and EFTA ESS pages | SDDS Plus, SDDS and e-GDDS participants; African Charter on Statistics parties; AFRISTAT; CES; ESS |
| HCCH conventions | [HCCH status tables](https://www.hcch.net/en/instruments/conventions/status-table/?cid=41) (`?cid=`); the Netherlands Treaty Database as depositary cross-check | Apostille, Service, Evidence, Child Abduction, Intercountry Adoption and Child Protection conventions |
| Council of Europe treaties | Council of Europe Treaty Office charts (behind a bot check for automated clients); the [Netherlands Treaty Database](https://treatydatabase.overheid.nl/) party tables (`Details/{id}_p.html?expand-table=partijtabel`) | MAAC, ETS 112, Lisbon Recognition, Convention 108, Lanzarote, CETS 197, CPT, Istanbul Convention, FCNM, European Social Charter |
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
