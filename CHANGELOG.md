# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

Dataset rebuild after attribute-partition retirement and Kosovo rename: **256** countries,
**1037** intblocks (**1078 → 1037**), **78** blocktypes (**86 → 78**).

### Changed

- **BREAKING:** Attribute-partition intblocks retired (`dvdregion`, `govform`, `lawsystem`, `railgauge`, `teleregion`, `traffichand`, `writingdirection`, `writingsystem`). Values now live on country records (except government form, which is vocab-only and out of countries scope). Remap retired ids via `attribute_intblock_migrations.json`.
  - Before: `SELECT … FROM intblocks, UNNEST(includes) … WHERE id = 'RHTRAFFIC'`
  - After: `SELECT code, name FROM countries WHERE car_side = 'right'`
- **BREAKING:** Kosovo country code renamed `KV` → `XK`, alpha-3 `KSV` → `XKX`; legacy codes in `countries_aliases.json`.
- New export formats: zstd-compressed `countries.csv.zst` / `intblocks.csv.zst` / `memberships.csv.zst`, lite CSV/Parquet variants, `countries.json.zst` / `intblocks.json.zst`, `datapackage.json`, `countries_aliases.json`.
- Documentation refreshed for new counts, exports, Kosovo `XK`, attribute-field migrations, citation/DOI, and Polars consumer recipes.

### Fixed

- Intblock factual corrections: African Union HQ (Addis Ababa), OAS HQ/roster (Nicaragua former member), EU `partof: EEA` removed, ASEAN description (eleven members), UN agency `partof` standardized to `UN` (ILO, FAO, ICAO).

### Added

- Country attribute fields: `writing_directions`, `writing_systems`, `dvd_region`, `broadcast_systems`, `legal_systems`, `rail_gauges` (plus existing `car_side`); vocab catalogs under `data/vocabs/`; optional `government_forms.yaml` without country assignment.
- `docs/entity-classification-policy.md` — TW, PS, XK, EH, VA, CK, NU edge-case guidance.
- Validation: `partof` hierarchy check (no treaty/agreement parents); Wikidata completeness gate with `data/schemas/wikidata_exclusions.yaml`.
- Contributor onboarding: `docs/getting-started.md`, `docs/architecture.md`, generated `docs/data-dictionary.md`, GitHub issue templates, `dev/research`/`dev/scripts`/`data/_legacy` READMEs.
- LLM ergonomics: OpenAI tool schemas, token-budget tables, RAG/policy-researcher recipes.
- Optional `scope_category` on intblocks (~872 labeled) + `docs/intblock-inclusion-policy.md`.
- Optional country crosswalks: `geonames_id`, `ioc_code`, `fifa_code`, `fips_code`, `bbox`.
- Citation: `CITATION.cff`, Zenodo concept DOI badge, ODbL note for mledoze/countries centroids in `ATTRIBUTION.md`.
- pytest-cov gate (fail-under 45%, measured baseline ~48%), schema migration emitter (`migration.vUnreleased.json`), monthly enrichment auto-PR, optional HF/Zenodo release steps (dataset card + draft deposit).
- Wikidata id backfill for TIMBI, VISTA, SAPP (110 remain on exclusion list).
- [docs/query-examples-polars.md](docs/query-examples-polars.md) — verified Polars / Parquet query cookbook (country filters, borders, memberships, overlap, former members); covered by `tests/test_documented_queries_polars.py`. `polars` added to `requirements-dev.txt`.
- [docs/query-examples-observable.md](docs/query-examples-observable.md) — Observable Framework / Plot cookbook (DuckDB-Wasm + Plot: density bars, NATO/EU overlap, centroid maps, HQ cities, former-member timeline).

## [1.9.0] - 2026-08-01

Correct Guinea-Bissau UN membership and expand the verified DuckDB query cookbook.

### Fixed

- Country **GW** (Guinea-Bissau): set `un_member: true` (was incorrectly `false`). The country-level flag now matches the `UN` intblock roster at **193** members; independent non-UN states shrink to Vatican City (`VA`) alone.

### Changed

- Expanded [docs/query-examples.md](docs/query-examples.md) with verified DuckDB recipes for near-universal org coverage (CN/US absences), former memberships and departure dates (via `intblocks.jsonl.zst`), roster density, observer seats, border/income patterns, `partof` hierarchy, and related cross-joins; expected counts updated for the GW fix. Covered by `tests/test_documented_queries.py`.
- Rebuilt `data/datasets/` exports so consumers pick up the corrected `un_member` flag.

## [1.8.0] - 2026-07-30

Membership and provenance enrichment: ~500 intblock records refreshed with sourced rosters, metadata, and provenance; intblocks row count **1076 → 1078** (three added, one duplicate merged).

### Added

- Data-quality rule **INSUFFICIENT_PROVENANCE**: flags country and intblock records whose `provenance` list has fewer than four entries (threshold configurable via `min_count` in completeness schemas).
- Intblock **USCR** (United States-Costa Rica Free Trade Agreement): bilateral CAFTA-DR schedules for US and CR; signed 2004-05-28, entered into force for Costa Rica 2009-01-01, with full metadata, includes, and provenance.
- Intblock **FATFGREYLIST** (FATF grey list / Jurisdictions under Increased Monitoring): 22 jurisdictions as of the June 2026 FATF plenary, sourced from FATF black-and-grey-lists and increased-monitoring statements.
- Intblock **IPSOS** (International Patient Summary): global health-informatics standards initiative (successor to epSOS); G7 roadmap participants and documented national IPS deployments, HL7 FHIR IPS links, and full provenance.

### Changed

- **Bulk intblock enrichment**: ~500 records across agreements, forums, FTAs, fisheries, education, environment, gas pipelines, geographic groups, and trade blocs — membership rosters synced to official sources, with founded/HQ metadata, descriptions, notes, and full provenance where previously sparse.
- Intblock completeness: `provenance.min_count: 4` in `countries_completeness.yaml` and `intblocks_completeness.yaml`; Pacific Alliance Wikidata Q7122288 added to `wikidata_duplicate_allowlist` (PACALL vs PACIFICALLIANCE).
- Intblock **BTE** (Baku–Tbilisi–Erzurum / South Caucasus Pipeline): merged duplicate **SOUCAPIPE** record (same Wikidata Q572699); added SCP acronym, notes, and Arabic name; alias `SOUCAPIPE` → `BTE`.
- Intblock **SADCFTA** (Southern African Development Community Free Trade Area): corrected FTA roster to 13 implementing members (removed Angola; DRC and Comoros remain outside SADC FTA), added join dates and founding members, active period from August 2008, geographic scope/regions, sourced description/notes, and full provenance.
- Intblock **INTTRASPORTFORUM** (International Transport Forum): synced membership to 72 (added AR/BR/CR/GH/KH/KR/PA/PE), set founded `1953-10-17`, Paris HQ, ECMT previous names, sourced description/notes on May 2026 Ghana/Panama/Peru accession and RU/BY restrictions, and full provenance.
- Intblock **MSC** (Munich Security Conference): added Wikidata Q565507, foundation legal status, Munich HQ coordinates, previous names, and sourced description/notes; reframed `includes` as 57 frequent participant states plus EU/NATO (`participant` status; invitation-only, no treaty membership), with full provenance.
- Intblock **CAIRNSGROUP** (Cairns Group): confirmed 20 current members plus Fiji and Hungary as former founding members; set founded `1986-08`, join dates where known (incl. Ukraine 2024-02-25), trade blocktype, geographic scope/regions, sourced description/notes, and full provenance.
- Intblock **EAPC** (Euro-Atlantic Partnership Council): confirmed 50-member roster (32 NATO Allies + 18 PfP partners), set founded `1997-05-29`, Brussels NATO HQ, corrected English acronym to EAPC, sourced description/notes on RU/BY suspension and NACC succession, and full provenance.
- Intblock **FIPIC** (Forum for India-Pacific Islands Cooperation): confirmed 15 members (India plus 14 Pacific Island countries) with founding join dates `2014-11-19`, corrected Wikidata to Q20983306 (removed wrong mountain Q-id), fixed FM display name and bogus other_names, FICCI site link, sourced description/notes, and full provenance.
- Intblock **ARF** (ASEAN Regional Forum): confirmed 27 participants with join dates and 18 founding participants, set founded `1994-07-25`, Jakarta ASEAN Secretariat HQ, corrected Wikidata to Q7886981 (replaced polluted Q481014), sourced description/notes, and full provenance.
- Intblock **FOCAC** (Forum on China–Africa Cooperation): confirmed 54 country members (China + 53 African states recognizing the PRC; Eswatini excluded), set founded `2000-10-10`, Beijing HQ, geographic scope/regions, sourced description/notes, multilingual names/acronyms, and full provenance.
- Intblock **BFA** (Boao Forum for Asia): synced `includes` to the 29 BFA Initial Countries (26 charter founders plus Israel/New Zealand 2006 and Maldives 2016; removed incorrect KW/RU/SA/TR), set founded `2001-02-27`, Wikidata Q887521, Beijing secretariat metadata, sourced description/notes, and full provenance.
- Intblock **CVF** (Climate Vulnerable Forum): synced membership to 74 CVF-V20 members (added Cabo Verde, Gabon, Nauru, Solomon Islands, Somalia, and Suriname), set founded `2009-11-10`, Accra HQ, V20 as suborganization, sourced description/notes, and full provenance.
- Intblock **CCAMLR** (Commission for the Conservation of Antarctic Marine Living Resources): confirmed 27 Commission Members plus 10 Acceding States, set founded `1982-04-07`, founding members, Hobart HQ, Wikidata Q97382426, sourced description/notes, and full provenance.
- Intblock **GFCM** (General Fisheries Commission for the Mediterranean): confirmed 24 contracting parties with join dates plus 5 cooperating non-contracting parties; recorded United Kingdom and Japan as former members; set founded `1949-09-24` / entry into force `1952-02-20`, Rome HQ, founding members, sourced description/notes, and full provenance.
- Intblock **VIENNACONVENTION** (Vienna Convention for the Protection of the Ozone Layer): synced parties to universal ratification roster of 198 (added Guinea-Bissau), set founded `1985-03-22` / entry into force `1988-09-22`, founding members, Nairobi Ozone Secretariat HQ, Montreal Protocol as suborganization, sourced description/notes, and full provenance.
- Intblock **WCPFC** (Western and Central Pacific Fisheries Commission): confirmed 26 Members with Convention entry-into-force join dates and 14 founding members; added 7 Participating Territories and 8 Cooperating Non-Members from the official CCM roster; set founded `2004-06-19`, Pohnpei HQ coordinates, geographic scope/regions, sourced description/notes, and full provenance.
- Intblock **CECAF** (Fishery Committee for the Eastern Central Atlantic): confirmed 34 FAO members (coastal African states plus distant-water fishing/research members and the EU), set founded `1967-06` / statutes `1967-09-19`, Accra FAO RAF secretariat, COPACE/CPACO acronyms, sourced description/notes, and full provenance.
- Intblock **IOTC** (Indian Ocean Tuna Commission): confirmed 29 Contracting Parties plus Liberia/Panama as cooperating CNCPs and five former members (BZ/ER/GN/SL/VU), set founded `1993-11-25` / entry into force `1996-03-27`, Victoria HQ, founding members with join/left dates, sourced description/notes, and full provenance.
- Intblock **APFIC** (Asia-Pacific Fishery Commission): confirmed 21 current members plus Netherlands as former member (left 1974-06-01), set founded `1948-11-09`, Bangkok FAO RAP headquarters, founding members and acceptance dates, previous IPFC names, sourced description/notes on 2023–2028 activity suspension, and full provenance.
- Intblock **WECAFC** (Western Central Atlantic Fishery Commission): synced 34-member roster (added Costa Rica; removed incorrect Bolivia), set founded `1973`, Bridgetown FAO/SLC secretariat metadata, COPACO acronyms, Wikidata Q16189708, sourced description/notes, and full provenance.
- Intblock **CIFAA** (Committee for Inland Fisheries and Aquaculture of Africa): confirmed 37 African member states from FAO RFB sources, set founded `1971-06` (FAO Council Resolution 1/56), Accra RAF secretariat, rename history CIFA→CIFAA (2007), sourced description/notes, multilingual names/acronyms, and full provenance.
- Intblock **EIFAAC** (European Inland Fisheries and Aquaculture Advisory Commission): synced membership to 39 (added Cyprus, European Union, and Ukraine), set founded `1957`, Rome FAO secretariat metadata, official links/languages, sourced description/notes (EIFAC→EIFAAC rename; UA joined 2026-02-27), and full provenance.
- Intblock **UNFCCC** (United Nations Framework Convention on Climate Change): synced parties to 198 (added Iraq and Nauru), set founded `1992-05-09` / entry into force `1994-03-21`, Bonn secretariat/HQ metadata, official links/documents, sourced description/notes, and full provenance.
- Intblock **UNCCD** (United Nations Convention to Combat Desertification): added missing Guinea-Bissau to complete 197 parties; set founded `1994-06-17` / entry into force `1996-12-26`, Bonn HQ/secretariat, UNTC links, sourced description/notes, and full provenance.
- Intblock **CPSC** (Colombo Plan Staff College): confirmed 16 active members plus 12 inactive charter members, set founded `1973-12-05`, founding members, Pasig HQ, official site links, sourced description/notes, and full provenance.
- Intblock **UIL** (UNESCO Institute for Lifelong Learning): confirmed `includes` as the 193 UNESCO Member States served by this Category 1 institute, set founded `1952`, Wikidata Q2467481, Hamburg HQ coordinates, previous name UIE (1952–2006), geographic scope/regions, sourced description/notes, and full provenance.
- Intblock **ACU** (Association of Commonwealth Universities): synced includes to the official home-regions roster (56 countries/territories; added Gibraltar, Hong Kong, and Zimbabwe; removed Gabon, Gambia, and Togo), set Wikidata Q593768, geographic scope/regions, sourced description/notes, and full provenance.
- Intblock **IIEP** (UNESCO International Institute for Educational Planning): confirmed `includes` as the 193 UNESCO Member States served by this Category 1 institute, set founded `1963-07`, Wikidata Q3152335, Paris HQ, sourced description/notes, multilingual names, and full provenance.
- Intblock **EHEA** (European Higher Education Area): confirmed 49 country members from the official roster (European Commission noted separately); removed incorrect `partof: EU`; set founded `2010-03`, geographic scope/regions, corrected acronyms (EHEA/EEES/EVP), sourced description/notes on RU/BY suspension, and full provenance.
- Intblock **IBE** (International Bureau of Education): confirmed `includes` as the 193 UNESCO Member States served by this Category 1 institute, added Wikidata Q1047672, official site, global scope, sourced description/notes, multilingual names, and full provenance.
- Intblock **COMMLEARN** (Commonwealth of Learning): completed includes for all 56 Commonwealth member states (added United Kingdom), replaced templated description, set Vancouver HQ/secretariat metadata, geographic scope/regions, sourced notes, and full provenance.
- Intblock **AAU** (Association of African Universities): synced `includes` to 50 countries with AAU member institutions from the official directory (added AE/DE/MY associates; removed seven African countries with no listed members), set founded `1967-11-12`, Wikidata Q743769, geographic scope/regions, recognition notes, and full provenance.
- Intblock **EEA** (European Economic Area): confirmed 30 current parties (27 EU + IS/LI/NO) with join dates; recorded United Kingdom as former member (left 2020-01-31); set founded `1992-05-02` / entry into force `1994-01-01`, Brussels EFTA secretariat metadata, founding members, sourced description/notes, and full provenance.
- Intblock **PETROCARIBE**: confirmed 18 current members plus Guatemala as former member (left 2013-11), set founded `2005-06-29`, founding members and join dates, energy blocktype, Caracas HQ, sourced description/notes, and full provenance.
- Intblock **PECC** (Pacific Economic Cooperation Council): confirmed 24 current member committees from the official roster (11 founding economies; France as associate; PIF/PBEC/PAFTAD as institutional members), recorded Ecuador and Mongolia as former members, set Singapore HQ/secretariat, sourced description, and full provenance.
- Intblock **CP** (Colombo Plan): synced membership to 27 current members (added Chile and Saudi Arabia; recorded United States, Canada, United Kingdom, and Cambodia as former members after the January 2026 U.S. withdrawal), set founded `1951-07-01`, founding members, Colombo HQ, sourced description, and full provenance.
- Intblock **AEC** (African Economic Community): synced parties to 50 Abuja Treaty ratifiers/acceding states (removed DJ, ER, MG, SO, SS pending ratification), set founded `1991-06-03` / entry into force `1994-05-12`, Addis Ababa AU headquarters, founding members, join dates, partof AFUNION, sourced description, and full provenance.
- Intblock **CAEU** (Council of Arab Economic Unity): confirmed 18-member roster with founding members (EG, IQ, JO, KW, SY), set founded `1957-06-03`, Arab League `partof`, Cairo HQ/official site, sourced description, multilingual names, and full provenance.
- Intblock **CCASG** (Gulf Cooperation Council): set founded `1981-05-25`, Riyadh headquarters, founding-member status and join dates for all six members, suborganizations PSF/GCCPO, sourced description/notes, and full provenance.
- Intblock **POPS** (Stockholm Convention on Persistent Organic Pollutants): synced parties to 186 (added Cook Islands, DPRK, and Niue; removed Andorra, Bhutan, Brunei Darussalam, Haiti, Israel, Malaysia, San Marino, South Sudan, Timor-Leste, and Turkmenistan), set founded `2001-05-22` / entry into force `2004-05-17`, Geneva BRS secretariat metadata, sourced description, and full provenance.
- Intblock **RAMSAR** (Ramsar Convention / Convention on Wetlands): synced Contracting Parties to 172 current members (added CI, KP, TR; removed 10 non-parties; recorded Russia as former member after denunciation effective 2025-12-21), set founded `1971-02-02` / entry into force `1975-12-21`, Gland secretariat (IUCN-hosted), sourced description, and full provenance.
- Intblock **RAROTONGA** (Treaty of Rarotonga / South Pacific Nuclear Free Zone Treaty): set founded `1985-08-06` and entry into force `1986-12-11`, confirmed 13 States Parties with ratification join dates and founding members, Suva PIF secretariat, official UNODA/UNTC links, and full provenance.
- Intblock **TPNW** (Treaty on the Prohibition of Nuclear Weapons): synced parties to 75 current States parties (added Mongolia, Niue, and Tonga; removed signatories that have not ratified), set founded `2017-09-20` / entry into force `2021-01-22`, official links/languages, and full provenance.
- Intblock **PIC** (Rotterdam Convention): synced parties to 168 current parties from the UN Treaty Collection (added EU, Israel, DPRK, Palestine; removed 28 non-parties), set founded `1998-09-10` / entry into force `2004-02-24`, BRS secretariat metadata, sourced description, and full provenance.
- Intblock **NPT** (Treaty on the Non-Proliferation of Nuclear Weapons): synced parties to 190 current States parties (added Denmark and Palestine, removed South Sudan, recorded North Korea as former member), set entry-into-force date `1970-03-05`, official name/description/links/languages, and full provenance.
- Intblock **OSPAR** (OSPAR Commission): added European Union to Contracting Parties (15 → 16), founded `1992-09-22` / entry into force `1998-03-25`, London secretariat, founding members, sourced description, and full provenance.
- Intblock **NOUMEA** (Noumea Convention): corrected membership to the 12 contracting parties (removed non-parties previously listed from the broader SPREP roster), added founded/EIF dates, founding members, join dates, UNEP Regional Seas metadata, Apia secretariat, multilingual names, and full provenance; removed incorrect Wikidata Q7446680.
- Intblock **PELINDABA** (Treaty of Pelindaba / African Nuclear-Weapon-Free Zone Treaty): added Western Sahara (EH) as the 44th party, set founded `1996-04-11` and entry into force `2009-07-15`, AFCONE Pretoria headquarters, official links, and full provenance.
- Intblock **CPTPP** (Comprehensive and Progressive Agreement for Trans-Pacific Partnership): added United Kingdom (12th member), founding-member status and join dates for original signatories, Wikidata Q48852287, predecessor TPP, sourced description, multilingual names, and full provenance.
- Intblock **TPP** (Trans-Pacific Partnership): corrected record from P4-only membership to all twelve 2016 signatories (US as former member after 2017 withdrawal), historical status, founded/dissolved dates, successor CPTPP, sourced description, official links, and full provenance.
- Intblock **CASPSREG** (Caspian Sea region): confirmed five littoral-state membership (AZ, IR, KZ, RU, TM), geographic scope/regions, sourced description, multilingual names, and full provenance.
- Intblock **MEGP** (Maghreb–Europe Gas Pipeline): added Portugal to membership (3 → 4), Wikidata Q734096, founded `1996-11-01`, geographic scope/regions, acronyms (MEG/GME), multilingual names, sourced description covering the 2021 supply halt and 2022 reverse flow, and full provenance.
- Intblock **GFTEITP** (Global Forum on Transparency and Exchange of Information for Tax Purposes): expanded includes from 103 to 173 participants (172 tax jurisdictions plus the European Union), corrected description/tags/topics, added headquarters, official links, and full provenance.

### Fixed

- All **FOUNDING_MEMBER_NOT_INCLUDED** and **HISTORICAL_ENTITY_ACTIVE_MEMBER** quality findings resolved across the enriched intblock set.
- Refreshed documentation counts across README, `llms.txt`, `docs/`, and `openspec/project.md` (256 countries, 1078 intblocks, 86 blocktypes).

## [1.7.0] - 2026-07-20

Coverage expansion: five new intblocks and refreshed ISA Seabed Authority / International Copper Study Group membership.

### Added

- Intblocks **ARABSAT**, **CDRI**, **WANO**, **PAXSILICA**, **WAICO**; intblocks row count **1071 → 1076**.
- Intblock **ARABSAT** (Arab Satellite Communications Organization): Arab League intergovernmental satellite operator founded 1976-04-14, Riyadh HQ; 21 shareholder member states.
- Intblock **CDRI** (Coalition for Disaster Resilient Infrastructure): India-launched global coalition for disaster- and climate-resilient infrastructure (2019-09-23); New Delhi HQ; 58 member countries and 12 partner organizations.
- Intblock **WANO** (World Association of Nuclear Operators): nonprofit nuclear-operator safety organisation founded 1989-05-15, London HQ; 31 countries with operating commercial NPPs.
- Intblock **PAXSILICA** (Pax Silica): US-led AI, semiconductor, and critical-minerals supply-chain initiative.
- Intblock **WAICO** (World Artificial Intelligence Cooperation Organization) — 29 founding members, Shanghai HQ, established 2026-07-16.

### Changed

- Intblock **ISA_SEABED** (International Seabed Authority): synced membership to UNCLOS parties (172 members + US observer); set founded `1994-11-16`, Kingston HQ coordinates, `partof: UNCLOS`, and Wikipedia/Wikidata links.
- Intblock **ICSG** (International Copper Study Group): refreshed membership to 26 current members (incl. EU) plus 7 former members; set founded date 1992-01-23, Wikidata Q17084551, and Lisbon HQ provenance.

## [1.6.0] - 2026-07-16

Data-quality expansion release: shared rule engine with 40+ new referential, temporal, and plausibility checks; intblocks schema tightened (**breaking**); space category consolidation; artifact-consistency and link-check CI guards; hundreds of data fixes.

### Added

- Consumer query cookbook [docs/query-examples.md](docs/query-examples.md) with verified DuckDB and Pandas examples (UN members, borders, intblock membership, cross-joins).
- Intblock **BLASMBL** (Baltic Assembly); intblocks row count **1070 → 1071**.
- `data/datasets/blocktypes.manifest.json` — blocktypes now emit a build manifest like countries/intblocks.
- `scripts/check_generated_artifacts.py` — cross-format primary-key parity, source/export parity, and single-build-identity guard (wired into CI and release).
- `scripts/check_markdown_links.py` — internal Markdown link checker (wired into CI).
- Intblock structural enrichment: `enrich_intblocks.py backfill-structural` fills `headquarters` (Wikidata P159/P625) and `founded` (P571), stamping `last_verified`; `last_verified` coverage now reported by `validate_intblocks.py`.
- Capital cities for 10 previously capital-less entities (GI, HK, IL, MO, PS, TW, VA, XA, XS, XT) with provenance; remaining capital-less entities documented as expected exclusions in `docs/country-code-policy.md`.
- `internacia-build` and `internacia-analyze-quality` console entry points; shared HTTP client `internacia_builder.http`; `internacia_builder.__version__` now reports the release version.
- **Expanded data-quality rules** (`expand-data-quality-rules`): new referential-integrity checks — `UNRESOLVED_BORDER_REFERENCE` (borders resolve to existing `iso3code`, no self-reference), `NONRECIPROCAL_BORDER` (advisory, with allowlist), `UNRESOLVED_ORG_REF` (`predecessor`/`successor`/`suborganizations`), `UNRESOLVED_HQ_COUNTRY`, and `DUPLICATE_WIKIDATA_ID` (with documented allowlist for concept-level Q-ids). New consistency/plausibility checks — `CHRONOLOGY_ERROR`, `DUPLICATE_INCLUDE_ENTRY`, `MEMBERSHIP_COUNT_MISMATCH`, `CONTRADICTORY_APPLICABILITY`, `INVALID_INDICATOR_VALUE`, `INCONSISTENT_ENTITY_FLAGS`, `PROVENANCE_INTEGRITY`, and the `INCLUDE_NAME_MISMATCH` advisory (replaces `scripts/report_country_include_names.py`). CI-only rules (`INVALID_CURRENCY_CODE`, `INVALID_COORDINATES`, `STALE_PROVENANCE`, `FILENAME_ID_MISMATCH`, `DIRECTORY_BLOCKTYPE_MISMATCH`, `DEPRECATED_TOPIC_KEY`) now also appear in `dataquality/` reports.
- `data/schemas/includes_status.yaml` — canonical catalog of `includes[].status` participation values (member, observer, founding_member, former_member, etc.); `validate_intblocks.py` and the quality analyzer now check every include status against it (`INVALID_INCLUDE_STATUS`) and flag entries with no status at all.
- Intblock `membership_applicability: not_applicable` marker for records where an empty `includes` list is intentional (conceptual entities, acronym groups, DVD regions); records with neither `includes` nor the marker are flagged by the new `MISSING_INCLUDES_APPLICABILITY` rule.
- **Extended data-quality rules** (`add-extended-quality-rules`): country field validity — `INVALID_TLD`, `INVALID_CALLING_CODE`, `INVALID_TIMEZONE` (IANA tz database), `FLAG_EMOJI_MISMATCH`, `LANDLOCKED_INCONSISTENCY`, `REGION_HIERARCHY_MISMATCH` (canonical continent→subregion table with allowlist), `UNRESOLVED_PARENT_ENTITY`. Geographic plausibility — `CAPITAL_FAR_FROM_CENTROID` and `HQ_COORDINATES_OUTSIDE_COUNTRY` (area-scaled great-circle budgets that catch swapped/mis-signed coordinates). Intblock temporal/membership — `INCLUDE_DATE_INCONSISTENCY` (precision-aware `joined`/`left` checks), `FOUNDING_MEMBER_NOT_INCLUDED`, `HISTORICAL_ENTITY_ACTIVE_MEMBER`, `STALE_LAST_VERIFIED`. Lineage and naming advisories — `SUCCESSOR_RECIPROCITY`, `PARTOF_SUBORG_RECIPROCITY`, `DUPLICATE_ACRONYM` (with allowlist for real-world collisions). Text integrity — `MOJIBAKE_TEXT`. `UNKNOWN_TOPIC_KEY` is backed by the new canonical topic catalog `data/schemas/topics.yaml` (153 keys seeded from current usage).

### Changed

- **INOGATE enriched**: filled `includes` (12 partner countries plus Russia as observer), marked `status: historical` with `founded`/`dissolved` (1996–2016), and added `energy` blocktype, secretariat, headquarters, and provenance.
- **BREAKING (intblocks schema)**: `intblocks.schema.json` now sets `additionalProperties: false`. Declared canonical fields `legal_status`, `recognition_status`, `predecessor`, `successor`, `previous_names`, `official_documents`, `social_media`, `secretariat`; removed unused `abbrRU`, `listed`, and `translations`.
- **BREAKING (intblocks export)**: the empty `translations` column was removed from the Parquet/DuckDB export (use `other_names`).
- Intblock validation now errors (previously warned/unchecked) when a filename stem does not match the record `id`, or a record's category directory is absent from its `blocktype` list. Renamed `UFM.yaml` → `UfM.yaml`; added `space` to 22 space records; normalized one-off keys (`succeeded_by`, plural `predecessors`/`successors`, `official_languages`, `purpose`).
- 25 space-related records (space treaties, agencies, and coordination bodies — e.g. OUTERTREATY, ARTEMISACCORDS, ESA, ISS, UNOOSA, COPUOS, EUMETSAT, COSPAR) consolidated into the `data/intblocks/space/` category directory from `agreement/`, `forum/`, `intorg/`, `meteorology/`, `project/`, `scientific/`, and `unagency/`.
- `data/schemas/intblocks_completeness.yaml` restructured into priority/requirement tiers (high: `includes`; medium: `wikidata_id`, non-templated `description`; low: `languages`, `headquarters`, `regions`, `other_names`, `provenance`, `links`) with measured 2026-07 baselines as warn thresholds, plus documented allowlists for org references, wikidata duplicates, and acronym collisions.
- Quality analyzer `DUPLICATE_LINK` rule de-noised (normalized URLs, excludes reference-catalog hosts and hierarchically related orgs, drops synthetic TLD pseudo-links): 77 → 22 flags. `analyze-quality` now runs in CI and fails on CRITICAL/IMPORTANT.
- Build now emits a single frozen build identity (`build_date`/`git_commit`) across all manifests, sidecars, and DuckDB `_meta` rows.
- `gini` completeness threshold documented and re-scoped (0.33 → 0.40, warn) reflecting World Bank coverage reality.
- Build/export logic moved into the installable `internacia_builder.build`; `scripts/builder.py` is now a thin shim.
- Refreshed stale documentation counts across README, `llms.txt`, `docs/`, and `openspec/project.md` (256 countries, 1071 intblocks, 86 blocktypes).
- Data-quality checkers consolidated into a single shared layer (`internacia_builder/validate/country_rules.py`, `intblock_rules.py`, `cross_rules.py`) used by both `analyze-quality` and the `validate_countries`/`validate_intblocks` CLIs, eliminating the duplicated rule logic in `build.py`.

### Fixed

- All 377 `INCLUDE_NAME_MISMATCH` advisories resolved: IFDC's Benin member used Belgium's code (`BE` → `BJ`); World Bank WLD placeholder display names `TW`/`VA` replaced with real names; legitimate alternate names (e.g. `Türkiye`, `Holy See`, `Chinese Taipei`, ISO 3166 long forms) added to 15 country records' `common_names` with provenance; scoped-membership qualifiers (e.g. "Denmark (in respect of the Faroe Islands and Greenland)", "Malaysia (Labuan)", Bonaire/Sint Eustatius under `BQ`) moved from `includes[].name` into `includes[].note`.
- Wrong `wikidata_id` on seven UN records (UNDP, WFP, UNFPA, UNRWA, UN Women shared the generic "nonprofit organization" item Q163740; UN-Habitat and SIDS carried UNEP's and WMO's Q-ids); Kosovo's empty `borders` populated (ALB, MKD, MNE, SRB); 27 intblock `founded`/`dissolved` placeholder dates (`YYYY-00-00`) normalized.
- Swapped/incorrect capital coordinates for Western Sahara (`EH`: El Aaiún was placed in Zambia) and the French Southern Territories (`TF`: Port-aux-Français was placed near Mont-Saint-Michel), surfaced by the new `CAPITAL_FAR_FROM_CENTROID` rule.
- Missing lineage back-references added: `WTO.predecessor: GATT`, `ICSU.successor: ISC`, `EEHUB.predecessor: IPEEC`, `ENTSOE.predecessor: NORDEL`, `G8 ↔ G7`, and `BRIC ↔ BRICS`; `IMF` now declares `partof: UN` (it was already listed in UN suborganizations); IATTC's Spanish acronym `CIAT` re-tagged from `lang: en` to `lang: es`.

## [1.5.0] - 2026-06-15

Coverage expansion, taxonomy governance, builder refactor, and enrichment tooling release.

### Added

- User-assigned country profiles for CIS2 entities (`XA`, `XS`, `XT`, `XN`) with `recognition_status` metadata; countries row count **252 → 256**.
- Country `centroid: {lat, lng}` on all 256 records.
- Intblocks **COCESNA**, **EPLO**, **FILAC** (P2 backlog); intblocks row count **1067 → 1070**.
- Nine intblock coverage gaps (UNSC, UNGA, UNHRC, CHIP4, DEPA, PEPFAR, MSF, UNCITRAL, UNCLOS) and topic taxonomy governance (`docs/topic-taxonomy.md`, `data/schemas/topic_aliases.yaml`).
- `scripts/apply_manus_roadmap.py` for batch topic/directory/centroid migrations.
- `enrich_countries.py check`: report stale provenance and missing fields (no network).
- `validate_countries.py`: ISO 4217 currency code warnings and provenance freshness checks.
- `.github/workflows/enrichment-check.yml`: monthly enrichment freshness report.
- G5 Sahel historical record (`G5SAHEL`) and `enrich_intblocks.py backfill-founded` for Wikidata inception dates.

### Changed

- `builder.py` imports validators directly (no subprocess); validation logic moved to `internacia_builder/`.
- `enrich_intblocks.py backfill-founded` also checks Wikidata P1619 (date of official opening).
- Blocktypes taxonomy source moved to `data/blocktypes/blocktypes.yaml`; `data/datasets/blocktypes.yaml` is now build output.
- Intblock directory taxonomy aligned with blocktype values (`tax/`, `transport/`, `unregionalblock/`, `audit` blocktype); 169 primary blocktype mismatches remediated.
- Topic keys consolidated (11 synonym groups, sports unification); `validate_intblocks.py` warns on deprecated keys and directory misalignment.
- `enrich_countries.py`: paginated World Bank fetch, M49-based classification for non-WB entities.
- `enrich_intblocks.py`: `--ids` filter for batch high-profile enrichment.
- **Dataset outputs rebuilt**: 256 countries, 1070 intblocks, 86 blocktypes.

## [1.4.0] - 2026-06-15

Intblocks taxonomy reorganization and enrichment release: domain-folder classification, Wikidata enrichment, data licensing, and self-describing dataset metadata.

### Added

- **Intblocks enrichment** (`scripts/enrich_intblocks.py`): backfills `wikidata_id` (high-confidence matches only), replaces templated boilerplate descriptions with Wikidata descriptions, and adds multilingual `other_names` and acronym aliases — all with field-level `provenance`. Intblock records now support a `provenance` list (validated and exported in all formats). Coverage: +55 `wikidata_id` (60%→66%), templated descriptions 43%→24%, provenance on 459 records.
- **Intblocks description-quality gate**: `validate_intblocks.py` measures the templated-description rate against a configurable threshold in `intblocks_completeness.yaml` (`quality.templated_description`).
- **Data license**: explicit `DATA_LICENSE` (CC BY 4.0) for datasets, separate from the MIT code license, plus `ATTRIBUTION.md` documenting World Bank (CC BY 4.0), Wikidata (CC0), and IANA tzdata sources and a recommended citation. Build manifests and metadata now carry a `data_license` SPDX field.
- **Self-describing datasets**: `internacia.duckdb` now includes a `_meta` table (one row per dataset with `version`, `build_date`, `git_commit`, `row_count`, `schema_hash`, `data_license`); each Parquet export is accompanied by a `<dataset>.meta.json` sidecar.
- **Identifier stability**: `data/intblocks_aliases.yaml` source plus generated `intblocks_aliases.{json,parquet}` mapping retired/renamed intblock ids to current ids (`reason`: `renamed`/`merged`/`disambiguated`). `validate_intblocks.py` checks alias integrity (targets resolve; collisions allowed only when `disambiguated`). Seeded with the v1.3.0 `ASF`→`FSA` and `CAF`→`CAFBANK` disambiguations.
- **Domain category folders**: new intblock source directories — `agriculture`, `audit`, `aviation`, `climate`, `cultural`, `education`, `health`, `intelligence`, `maritime`, `space`, `statistics`, `taxation`, `tourism`, `transportation`, and `water` — with ~150 records relocated from the catch-all `intorg/` folder into their primary domain.
- **New intblock records**: OPCW, GICNT, BIS, ICCROM, WTO, AANZFTA, OIV, CARICC, and regional fisheries/aviation/audit bodies among others.
- **Blocktype taxonomy**: added `statistics` blocktype (86 total).

### Changed

- **Intblocks folder taxonomy**: records are filed under their primary domain category rather than `intorg/` when a dedicated folder exists; `intorg/` now holds general-purpose intergovernmental organizations only (~81 records, down from ~230).
- **Description quality**: acronym and geographic group records updated with substantive descriptions replacing generic "International entity." boilerplate.
- **Currency record**: `CMA` (Comorian franc) moved from `cuscurr/` to `currency/`.
- **Release assets**: the release workflow now publishes `*.meta.json` sidecars and the `intblocks_aliases.*` artifacts.
- **Dataset outputs rebuilt**: all artifacts regenerated (252 countries, 1057 intblocks, 86 blocktypes).

## [1.3.0] - 2026-06-12

Intblocks quality and engineering hardening release: intblocks validation pipeline, automated tests, dev tooling, CI/CD workflows, and data fixes.

### Added

- **Intblocks validation** (`scripts/validate_intblocks.py`): JSON Schema checks, duplicate id detection, blocktype taxonomy validation, `partof` reference resolution, lifecycle consistency (`dissolved` implies `historical`), and completeness gates; runs in CI and before every build.
- **Intblocks completeness config** (`data/schemas/intblocks_completeness.yaml`): per-field null-rate thresholds with warn/error modes.
- **Intblocks build manifest** (`data/datasets/intblocks.manifest.json`): `version`, `build_date`, `git_commit`, `row_count`, `schema_hash`; baseline diff extended to cover it.
- **Test suite** (`tests/`, 49 tests): `clean_data` normalization, country/intblock validation logic, cross-dataset include resolution, Parquet/DuckDB export round-trips, and manifest generation.
- **Dev tooling**: `pyproject.toml` (ruff + pytest config), `.pre-commit-config.yaml`, `requirements-dev.txt`.
- **Contributor guide** (`CONTRIBUTING.md`): setup, YAML authoring conventions, validation workflow, PR checklist.
- **Workflows**: weekly scheduled link validation (`.github/workflows/link-validation.yml`), tag-triggered release with dataset assets (`.github/workflows/release.yml`), Dependabot for pip and GitHub Actions.

### Changed

- **Builder hardening** (`scripts/builder.py`): runs both countries and intblocks validation before export; YAML parse failures abort the build instead of silently skipping files; Parquet schema mismatches fail loudly (removed pandas fallback); fixed DuckDB export (PyArrow tables are now registered explicitly, restoring `internacia.duckdb` generation).
- **Intblocks schema reconciled** (`data/schemas/intblocks.schema.json`): status, include type/status, and geographic scope enums now match observed legitimate values; `founded` accepts decade notation; `partof` accepts strings or objects.
- **Indicator years**: missing `population`/`area`/`gini` years are exported as `null` instead of `0` (**semantic change**); validator rejects `year: 0`.
- **Pinned dependencies** (`requirements.txt`): exact versions for reproducible builds; CI uses pip caching.
- **One-off scripts relocated**: `enrich_gap_records.py` and `fill_includes_agreement_intorg.py` moved to `dev/scripts/`.

### Fixed

- **Intblocks deduplicated**: merged 8 duplicate records (OFID, GEF, ICRC, IFRC, NPI, IFAD, UNHCR, UNICEF) keeping the richer record with combined blocktypes; resolved 2 acronym collisions (African Solidarity Fund renamed to `FSA`, CAF Development Bank renamed to `CAFBANK`). Row count: 1065 → 1057 (**breaking** for consumers joining on removed ids).
- **Country data corrections**: `AN.yaml` (Netherlands Antilles) had Anguilla's wikidata id, names, and indicators; `JG.yaml` (Channel Islands) pointed to the wrong Wikidata entity (Urdoma); removed all `year: 0` placeholders across 36 country files.
- **YAML boolean traps**: quoted `NO` (Norway) and `no` (Norwegian) values that were parsed as `false` in intblock records (NORDEL, CEPI, and others).
- **Lifecycle consistency**: dissolved organizations (EASTERNBLOC, WESTERNBLOC, FRUGALFOUR, ICSU, NORDEL, GATT) now carry `status: historical`.
- **Reference fixes**: `partof` aliases corrected (`AU` → `AFUNION`, `GCC` → `CCASG`); missing `wikidata_id` filled for ISA, Kimberley Process, EAEU; UNFCCC duplicate member entry removed.
- **Validation report ordering**: `validate_countries.py --report` now includes cross-dataset results.

### Migration

- **Removed intblock ids**: `ASF` (African Solidarity Fund) is now `FSA`; `CAF` (development bank) is now `CAFBANK`; duplicate ids listed above resolve to a single record.
- **Indicator year**: treat `population.year == null` as "year unknown" (previously `0`).

## [1.2.0] - 2026-05-29

Countries reference data quality release: validation gates, profile enrichment, entity status modeling, and release governance. Based on gap analysis in `dev/research/countries_gaps_manus_20260528.md`.

### Added

- **Country validation** (`scripts/validate_countries.py`): JSON Schema checks, ISO identifier rules, completeness thresholds, entity status enforcement, and intblock cross-reference validation.
- **Completeness manifest** (`data/schemas/countries_completeness.yaml`): per-field null-rate gates with warn/error modes.
- **Country enrichment** (`scripts/enrich_countries.py`): World Bank + Wikidata + IANA tzdata for `population`, `area`, `gini`, `timezones`, and `native_names`; `backfill-provenance` subcommand.
- **IANA timezone reference**: bundled `scripts/data/zone1970.tab`.
- **Entity status fields**: `entity_type`, `code_status`, optional `recognition_status` on all 252 country records.
- **Entity annotation utility** (`scripts/annotate_entity_status.py`).
- **Country code policy** (`docs/country-code-policy.md`): ISO vs user-assigned codes, filter examples, deferred CIS2 entity notes.
- **Field provenance**: optional `provenance` list on country records (`field`, `source`, `retrieved_at`, `url`, `license`).
- **Build manifest** (`data/datasets/countries.manifest.json`): `version`, `build_date`, `git_commit`, `row_count`, `schema_hash`.
- **Baseline diff utility** (`scripts/diff_countries_baseline.py`).
- **Include name audit** (`scripts/report_country_include_names.py`): intblock alias reporting (warn-only).
- **CI workflow** (`.github/workflows/validate.yml`): validate, completeness report artifact, parquet build, baseline diff.

### Changed

- **Countries profile fields**: `population`, `area`, and `gini` are structured indicators `{value, year, source, source_id}` in YAML and Parquet (**breaking** — was bare `int64` for population).
- **Countries data populated**: formerly empty fields (`population`, `area`, `timezones`, `native_names`) filled across all 252 records where sources exist.
- **Borders contract**: documented and validated as ISO 3166-1 **alpha-3** land-border codes.
- **Builder integration**: runs country validation before export; strips categorical whitespace; writes manifest on parquet/duckdb build.
- **Extended JSON Schema** (`data/schemas/countries.schema.json`): full builder field coverage including entity status and provenance.
- **Dataset outputs rebuilt**: all countries artifacts regenerated.

### Migration

- **Parquet population**: column is now a struct. Access count via `population.value` (pandas: `df['population'].struct.field('value')`).
- **Current ISO filter**: `code_status == 'official_iso3166_1'` returns 249 records; excludes `AN` (obsolete), `JG` and `KV` (user-assigned).
- **Borders joins**: use alpha-3 codes in `borders` or map via `iso3code`.
- **Upgrade check**: compare `countries.manifest.json` `schema_hash` before deploying downstream consumers.

## [1.1.2] - 2026-05-28

### Added
- **International blocks expansion**: Added and merged new `intblocks` records from gap-analysis research (Manus + Perplexity), including additional agreement, intorg, forum, political, military, bank, food, environment, geographic, economic, and armscontrol entries.
- **Merged research report**: Added consolidated gap report at `dev/research/gaps_merged_20260528.md`.
- **Metadata enrichment utility**: Added `scripts/enrich_gap_records.py` to normalize and enrich newly added records with `wikidata_id`, `headquarters`, `acronyms`, `legal_status`, `topics`, and aligned tags.
- **Includes backfill utility**: Added `scripts/fill_includes_agreement_intorg.py` to populate missing `includes` for `agreement` and `intorg` datasets.

### Changed
- **Blocktype taxonomy**: Extended `data/datasets/blocktypes.yaml` with previously used but undefined blocktypes (including `health`, `water`, `ocean`, `transport`, `digital`, `cybersecurity`, `climate`, and related domain tags).
- **International blocks coverage**: Updated `agreement` and `intorg` records to ensure `includes` sections are populated where previously missing.
- **Dataset outputs rebuilt**: Regenerated all dataset artifacts (`countries`, `intblocks`, `blocktypes`) in JSONL, YAML, Parquet, and DuckDB formats.

## [1.1.0] - 2025-12-07

### Added
- **Countries dataset**: Added `other_names` field containing name translations in multiple languages (Arabic, Chinese, English, French, Russian, Spanish)
- **Countries dataset**: Added `common_names` field containing common aliases and alternative names
- **International Blocks dataset**: Added `other_names` field for standardized multilingual name translations
- **New international blocks categories**: Added support for environment, humanitarian, intelligence, meteorology, patent, scientific, sports, and standards categories
- **Expanded UN agency data**: Significantly expanded membership data for UN agencies (UNDP, UNEP, UNFPA, UNHABITAT, UNODC, UNRWA, UNWOMEN, WFP)
- **New utility scripts**: 
  - `add_environment_members.py`: Script to add environment organization members
  - `add_un_members_to_agencies.py`: Script to add UN members to UN agencies
  - `generate_environment_members.py`: Generate environment organization memberships
  - `generate_un_regional_groups.py`: Generate UN regional groups
  - `insert_environment_members.py`: Insert environment members into intblocks
  - `remove_translations.py`: Utility to remove deprecated translations field
- **Dataset expansion**: Increased international blocks from 727 to 1021+ files across 53+ categories
- **New international block**: Added PACER Plus (Pacific Agreement on Closer Economic Relations Plus) free trade agreement

### Changed
- **International Blocks dataset**: Replaced `translations` field with `other_names` field for consistency. The new field uses `id` instead of `lang` to identify languages, maintaining the same `name` structure
- **Schema updates**: Updated JSON schemas to reflect new `other_names` and `common_names` fields
- **Builder improvements**: Enhanced builder script to handle new field structures and expanded data

## 1.0

### Added
- Initial release of the Internacia Dataset Builder, a component of the **Dateno** search engine.
- Provides comprehensive availability of countries, intergovernmental organizations, and country groups data.
- Support for generating datasets in multiple formats:
    - **JSONL** (Zstandard compressed)
    - **YAML** (Zstandard compressed)
    - **Parquet** (Zstandard compressed)
    - **DuckDB** database
- CLI tool (`scripts/builder.py`) using `typer` for easy dataset generation.
- Comprehensive dataset schemas for:
    - **Countries**: 252 countries and territories with detailed attributes (ISO codes, demographics, geography, etc.).
    - **International Blocks**: 727 organizations and alliances with rich metadata (members, history, links, etc.).
- Zstandard compression (level 22) for efficient storage.
- Progress bar integration (`tqdm`) for build process visualization.
