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
| WTO-notified FTAs | Official treaty text; RTA-IS as a cross-check | ASEAN+1, Agadir, CER, PICTA, EU and US named FTAs |
| EU trade agreements | [European Commission](https://policy.trade.ec.europa.eu/), EUR-Lex | CETA, EU–Japan, EU–UK, EU–Korea, and related partnerships |
| US FTAs and PTAs | [USTR](https://ustr.gov/) and Federal Register | Remaining named U.S. FTAs; AGOA / CBERA beneficiary lists |
| Other PTA grantors | Government of Canada (CARIBCAN); EU GSP regulation (GSP+) | Waiver and GSP+ beneficiary rosters |
| Plurilateral IIAs | OIC COMCEC annex / UNCTAD IIA Navigator (ratifiers); ASEAN Secretariat (ACIA); League of Arab States / UNESCWA; CIS Executive Committee; Council of the EU treaty office; MOFCOM/MOFA treaty texts; Paraguay MFA (MERCOSUR protocols) | OIC Investment Agreement, ACIA, Unified Arab Capital Agreement, CIS services-and-investment FTA, CJK trilateral investment agreement, intra-EU BIT Termination Agreement, Intra-MERCOSUR PCFI |
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
