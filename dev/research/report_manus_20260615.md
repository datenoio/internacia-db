# Internacia-DB: Comprehensive Data Quality & Coverage Report

**Repository:** [datenoio/internacia-db](https://github.com/datenoio/internacia-db)
**Analysis Date:** June 2026
**Scope:** 252 country/territory records · 1,057 international block records · 86 defined blocktypes

---

## Executive Summary

The `internacia-db` repository is a well-structured and ambitious reference dataset for countries and international organizations. Its core required fields are robustly complete, and recent releases (v1.2.0, v1.3.0) have addressed many previously identified gaps. However, three categories of issues remain that limit the dataset's analytical depth and long-term maintainability.

**Metadata completeness** is strong for countries at the required-field level, but several high-value optional fields — most notably `adminregion` (42.5% missing), `gini` (32.5% missing), and country centroid coordinates (present for only 3 of 252 records) — remain substantially incomplete. For international blocks, the optional fields `legal_status` (74.6% missing), `geographic_scope` (59.5% missing), and `headquarters` (54.1% missing) are so sparsely populated that they cannot yet support reliable analysis. Additionally, several fields that would be critically valuable — such as `government_type`, `HDI`, and `GDP` for countries — are entirely absent from the schema.

**Coverage of international blocks** is broad but uneven. The 1,057-record dataset covers the most prominent global organizations, but notable gaps exist in UN principal organs (UNSC, UNGA, UNHRC), emerging digital/technology alliances (CHIP4, DEPA), health and humanitarian organizations (PEPFAR, MSF), and several important political groupings (EPC, D10) that have been deferred from prior gap analyses. Entire thematic domains — particularly digital governance, specialized health initiatives, and foundational international law bodies — are underrepresented.

**Classification quality** is the most structurally significant issue. The topic taxonomy has grown to 177 unique keys, many of which are synonymous or used only once, creating fragmentation that undermines consistent tagging. The blocktype taxonomy has 4 directories with no matching blocktype value and 27 blocktype values with no corresponding directory, while 169 records (16%) have a primary blocktype that does not match their directory. These structural inconsistencies require systematic remediation rather than incremental fixes.

---

## 1. Metadata Completeness Analysis

### 1.1 Country Records

The 252 country records are organized around a 35-field schema. As of the current state of the repository, the most critical fields have been successfully populated.

#### Fields at Full or Near-Full Completeness

The following fields meet or exceed their defined completeness thresholds and require no immediate action:

| Field | Missing | Rate | Threshold |
|---|---:|---:|---|
| `population` | 0 | 0.0% | Error if missing |
| `area` | 0 | 0.0% | Error if missing |
| `native_names` | 0 | 0.0% | Error if missing |
| `wikidata_id` | 0 | 0.0% | Warn if >5% |
| `common_names` | 0 | 0.0% | Warn if >25% |
| `timezones` | 3 | 1.2% | Error if missing |
| `official_name` | 3 | 1.2% | — |
| `languages` | 4 | 1.6% | — |
| `currencies` | 6 | 2.4% | — |
| `other_names` | 6 | 2.4% | — |
| `capital_city` | 11 | 4.4% | Warn if >5% |
| `subregion` | 8 | 3.2% | — |

The three records missing `timezones` and the handful missing `official_name`, `languages`, and `currencies` are almost exclusively uninhabited territories or special-status entities (e.g., `BV` Bouvet Island, `HM` Heard Island, `AQ` Antarctica, `JG` Channel Islands, `AN` Netherlands Antilles), where the absence is either expected or reflects genuine ambiguity in source data.

#### Fields with Significant Gaps Requiring Enrichment

Several fields are present in the schema but have coverage too low to support reliable analysis:

| Field | Missing | Rate | Notes |
|---|---:|---:|---|
| `adminregion` | 107 | 42.5% | World Bank administrative region; absent for high-income and special-status countries |
| `borders` | 89 | 35.3% | Largely expected for island nations; non-island gaps need review |
| `gini` | 82 | 32.5% | Warn threshold is >45%; data genuinely unavailable for many countries |
| `region` | 33 | 13.1% | World Bank region; absent for territories not classified by WB |
| `incomeLevel` | 33 | 13.1% | World Bank income classification; same gap as `region` |
| `lendingType` | 33 | 13.1% | World Bank lending type; same gap as `region` |

The `adminregion`, `region`, `incomeLevel`, and `lendingType` gaps are structurally linked: all 33 records missing these fields are countries or territories that the World Bank does not classify (typically high-income OECD members, overseas territories, and special entities). The gaps are therefore partially expected, but the schema should document this explicitly and consider sourcing these classifications from an alternative authority (e.g., UN M49 or IMF) for the remaining records.

The `gini` gap is more substantive: 82 countries genuinely lack recent Gini coefficient data from public sources, particularly small island states, Gulf monarchies, and countries with limited statistical capacity (e.g., `BN` Brunei, `KP` North Korea, `CU` Cuba, `ER` Eritrea). This is an acceptable data availability limitation, but the schema's `{value, year, source}` structure already accommodates partial data, so older estimates should be backfilled where available.

#### Country Centroid Coordinates: A Critical Structural Gap

Only 3 of 252 country records (`HK` Hong Kong, `IL` Israel, `MO` Macao) contain `latitude`/`longitude` fields, and these appear to have been added ad hoc rather than systematically. Country centroid coordinates are among the most universally useful geographic metadata fields — required for map rendering, distance calculations, and spatial joins. This field should be added to the schema as a structured `centroid: {lat, lng}` object and populated for all records from a reliable open source such as Natural Earth or the World Bank's geocoded country list.

#### Fields Absent from the Schema but Critically Valuable

The following fields do not exist in the current schema but would substantially increase the dataset's analytical utility:

| Proposed Field | Type | Priority | Source |
|---|---|---|---|
| `centroid` (`{lat, lng}`) | Geographic | **Critical** | Natural Earth, World Bank |
| `government_type` | Political | High | CIA World Factbook, Wikidata |
| `hdi` (`{value, year, source}`) | Socioeconomic | High | UNDP Human Development Reports |
| `gdp_per_capita` (`{value, year, source}`) | Socioeconomic | High | World Bank, IMF |
| `internet_penetration` (`{value, year, source}`) | Digital | Medium | ITU, World Bank |
| `iso_currency_codes` | Identifier | Medium | ISO 4217 (already implied by `currencies`) |
| `iso_language_codes` | Identifier | Medium | ISO 639 (already implied by `languages`) |
| `election_system` | Political | Low | IDEA Electoral System Database |
| `press_freedom_index` | Governance | Low | RSF, Freedom House |

The most impactful addition would be `centroid` coordinates, which are both universally available and immediately useful. `government_type`, `HDI`, and `GDP per capita` would transform the dataset from a geographic reference into a genuine country profile database, enabling a much broader range of analytical applications.

### 1.2 International Block Records

The 1,057 intblock records show strong completeness for all required fields but significant gaps in optional contextual fields.

#### Required Fields: Fully Complete

All required fields — `id`, `name`, `blocktype`, `status`, `description`, `tags`, and `topics` — are present in 100% of records. This is a significant achievement and reflects the validation gates introduced in recent releases.

#### Optional Fields with Substantial Gaps

The following optional fields have coverage too low to support reliable analysis:

| Field | Present | Coverage | Notes |
|---|---:|---:|---|
| `links` | 1,011 | 95.6% | Acceptable; 46 records lack any URL |
| `membership_count` | 1,003 | 94.9% | Acceptable |
| `includes` | 983 | 93.0% | Acceptable; below the warn threshold |
| `wikidata_id` | 800 | 75.7% | Acceptable; below the warn threshold |
| `founded` | 702 | 66.4% | Moderate gap; important for historical context |
| `acronyms` | 676 | 64.0% | Moderate gap |
| `provenance` | 644 | 60.9% | Moderate gap; important for data trust |
| `headquarters` | 485 | 45.9% | **Significant gap** |
| `geographic_scope` | 428 | 40.5% | **Significant gap** |
| `regions` | 323 | 30.6% | Moderate gap |
| `legal_status` | 268 | 25.4% | **Critical gap** |

The three most problematic fields are `legal_status` (74.6% missing), `geographic_scope` (59.5% missing), and `headquarters` (54.1% missing). These are not obscure metadata — they are fundamental facts about any international organization. An organization's legal basis (treaty, charter, informal forum), its geographic reach (global vs. regional vs. sub-regional), and its physical seat are all information that is publicly available and should be systematically backfilled.

#### Templated Descriptions

Approximately 141 records (13.3%) contain generic templated descriptions of the form "International entity focused on...". After Wikidata backfill, this number rises to 253 (23.9%), approaching the 25% warning threshold. These templated descriptions reduce the informational value of the `description` field and should be replaced with accurate, specific summaries sourced from official websites or Wikidata.

#### Fields Absent from the Intblock Schema

Unlike countries, the intblock schema is relatively mature. However, two fields would add meaningful value:

| Proposed Field | Rationale |
|---|---|
| `budget` (`{value, year, currency}`) | Annual budget is a key indicator of an organization's operational scale |
| `staff_count` (`{value, year}`) | Organizational size metric; available for major IGOs |

---

## 2. International Blocks Coverage Analysis

### 2.1 Overall Coverage Assessment

With 1,057 records spanning 63 directory categories and 86 defined blocktypes, the database provides broad coverage of the international organizational landscape. The most prominent global institutions are present: the UN system's specialized agencies, major regional economic blocs, military alliances, development banks, and trade agreements. The blocktype distribution shows a strong concentration in `intorg` (316 records), `political` (102), `agreement` (59), `economic` (58), and `research` (52), reflecting the dataset's emphasis on formal intergovernmental structures.

However, coverage becomes uneven when examined by thematic domain. The following table summarizes coverage quality by domain:

| Domain | Assessment | Notable Gaps |
|---|---|---|
| UN Specialized Agencies | Strong | UNSC, UNGA, UNHRC missing |
| Major Regional Blocs | Strong | BRICSPLUS deferred |
| Development Banks | Strong | — |
| Military Alliances | Good | CSTO substructures |
| Trade Agreements | Good | DEPA, newer FTAs |
| Environmental Bodies | Good | Fragmented topic taxonomy obscures coverage |
| Health/Humanitarian | **Weak** | PEPFAR, MSF, G5SAHEL missing |
| Digital/Technology | **Weak** | CHIP4, DEPA, GPAI partially covered |
| International Law | **Weak** | UNCITRAL, UNCLOS missing |
| Historical Entities | Partial | CSCE, Warsaw Pact present; others missing |

### 2.2 Critical Missing Organizations

The following organizations are absent from the database and represent the highest-priority additions:

#### Tier 1 — Critical (Foundational UN Organs)

These are principal organs of the United Nations. Their absence is a structural gap in any database claiming comprehensive coverage of international bodies:

| ID (proposed) | Name | Rationale |
|---|---|---|
| `UNSC` | UN Security Council | Primary UN body for international peace and security; 15 members |
| `UNGA` | UN General Assembly | Main deliberative organ of the UN; all 193 member states |
| `UNHRC` | UN Human Rights Council | 47-member intergovernmental body; previously deferred |

#### Tier 2 — High Priority (Significant Gaps by Domain)

| ID (proposed) | Name | Domain | Rationale |
|---|---|---|---|
| `CHIP4` | Chip 4 Alliance | Digital/Tech | US-Japan-South Korea-Taiwan semiconductor coordination; major geopolitical relevance |
| `DEPA` | Digital Economy Partnership Agreement | Digital/Trade | Singapore-NZ-Chile digital trade framework; first of its kind |
| `PEPFAR` | US President's Emergency Plan for AIDS Relief | Health | Largest bilateral health program globally; 55+ partner countries |
| `MSF` | Médecins Sans Frontières | Humanitarian | Largest independent humanitarian medical organization |
| `EPC` | European Political Community | Political | 47-country European political forum launched 2022; growing significance |
| `D10` | Democracies 10 | Political | Grouping of leading democracies; relevant for technology governance |
| `UNCITRAL` | UN Commission on International Trade Law | Legal | Primary UN body for international trade law |
| `UNCLOS` | UN Convention on the Law of the Sea | Legal/Maritime | Foundational treaty governing the law of the sea; 168 parties |

#### Tier 3 — Medium Priority (Deferred Items and Emerging Bodies)

| ID (proposed) | Name | Domain | Notes |
|---|---|---|---|
| `BRICSPLUS` | BRICS+ (expanded) | Economic/Political | Post-2024 expansion; membership dynamics still evolving |
| `PANDEMICTREATY` | WHO Pandemic Accord | Health/Governance | Negotiations ongoing; add when finalized |
| `CSCE` | Conference on Security and Co-operation in Europe | Historical | OSCE predecessor; relevant for historical analysis |
| `GLOBALGATEWAY` | EU Global Gateway | Development | EU infrastructure investment strategy; 300B EUR commitment |
| `PGII` | Partnership for Global Infrastructure and Investment | Development | G7 counterpart to Belt and Road Initiative |
| `G5SAHEL` | G5 Sahel | Security | Regional security framework; dissolved 2023 — add as historical |
| `BLEU` | Belgium–Luxembourg Economic Union | Economic | Long-standing bilateral economic union |

#### Tier 4 — Lower Priority (Deferred Items Needing Scope Review)

The following items from the prior gap analysis remain deferred and require a scope decision before inclusion:

`EPC2022`, `MSP`, `CIGEPS`, `BIC`, `NSMC`, `C4`, `MOI`, `FILAC`, `EPLO`. These are either very recent initiatives whose membership and status are still evolving, or bodies whose scope may fall outside the dataset's country-membership model.

### 2.3 Underrepresented Domains

Beyond individual missing organizations, several thematic domains are systematically underrepresented:

**Digital and Technology Governance.** The database has only 2 records with `blocktype='cybersecurity'` and 2 with `blocktype='digital'`, despite this being one of the fastest-growing areas of international cooperation. Organizations such as the Global Partnership on AI (GPAI — partially present), the Freedom Online Coalition (FOCONLINE — present), and the Global Forum on Cyber Expertise (GFCE — present) have been added, but the domain still lacks depth. The CHIP4 semiconductor alliance and DEPA digital trade agreement are high-profile absences.

**Health and Humanitarian Organizations.** The `health` topic appears in only 19 records, and the `humanitarian` blocktype covers only 5 records. While GAVI, CEPI, COVAX, and Africa CDC are present, the absence of PEPFAR (the world's largest bilateral health program) and MSF (the most prominent independent humanitarian medical organization) represents a significant gap. The Global Fund for AIDS, TB and Malaria is present (`GLOBALFUND`), which makes the PEPFAR absence more conspicuous.

**International Legal Frameworks.** UNCITRAL and UNCLOS are foundational international legal instruments with broad country membership, yet neither is present. The International Court of Justice (ICJ) and International Criminal Court (ICC) are present, making the absence of these treaty bodies more noticeable.

**Sub-regional African Organizations.** While major pan-African bodies (African Union, ECOWAS, SADC, EAC, COMESA, IGAD, ECCAS) are present, many sub-regional bodies — particularly river basin commissions and specialized economic communities — were only partially added in the v1.3.0 gap-filling exercise. Coverage of the African continent at the sub-regional level remains less complete than for other regions.

---

## 3. Topics and Blocktype Classification Quality

### 3.1 The Blocktype Taxonomy: Structural Issues

The 86-blocktype taxonomy in `data/datasets/blocktypes.yaml` is comprehensive in scope but suffers from several structural inconsistencies that create confusion between the logical taxonomy and the physical file organization.

#### The Directory–Blocktype Alignment Problem

The repository uses a directory structure (`data/intblocks/<category>/`) that is intended to reflect the primary blocktype of records within it. However, this alignment has broken down in several places:

**Directories with no matching blocktype value (4 cases):**

| Directory | Blocktypes actually used | Issue |
|---|---|---|
| `audit/` | `intorg` only | No `audit` blocktype exists; 8 records |
| `taxation/` | `intorg`, `tax` | Directory named `taxation` but blocktype is `tax`; 12 records |
| `transportation/` | `intorg`, `transport` | Directory named `transportation` but blocktype is `transport`; 5 records |
| `unregionalblocks/` | `unregionalblock`, `unregionalgroup` | Directory uses plural form but blocktypes use singular; 5 records |

**Blocktype values used in data but with no corresponding directory (27 values):**

`aviation_safety`, `biodiversity`, `counter_terrorism`, `cuscurr`, `cybersecurity`, `development`, `digital`, `disaster`, `financial`, `fisheries`, `forestry`, `gender`, `human_rights`, `labor`, `migration`, `mining`, `nuclear`, `ocean`, `security`, `tax`, `technical`, `technology`, `transport`, `unregionalblock`, `unregionalgroup`, `waste`, `youth`

Records with these blocktypes are housed in other directories (typically `intorg/` or a thematically adjacent category), making them harder to locate by their specific function.

**Primary blocktype–directory mismatches (169 records, 16%):**

The most pervasive issue is that 169 records have a primary blocktype (first value in the `blocktype` list) that does not match their directory. This affects nearly every category. Selected examples:

| Record | Directory | Primary Blocktype | Correct Action |
|---|---|---|---|
| `ASEAN` | `political/` | `economic` | Move to `economic/` or reorder blocktypes |
| `WTO` | `unagency/` | `trade` | Move to `trade/` directory |
| `G-20` | `political/` | `political` | Add `economic`, `forum` to blocktype list |
| `ICSG`, `ILZSG`, `INSG` | `intorg/` | `mining` | Move to `mining/` directory or create one |
| `CEMAC`, `UEMOA` | `customs/` | `cuscurr` | Align directory with `cuscurr` blocktype |
| `KIMBERLEY` | `agreement/` | `mining` | Reorder or move |
| `EMU` | `wbgroup/` | `currency` | Reorder or move |

#### The `unregionalblocks` Orphan

The blocktype `unregionalblocks` (plural) is defined in `blocktypes.yaml` but is never used in any record. Records in the `unregionalblocks/` directory use either `unregionalblock` or `unregionalgroup`. This orphaned definition should be removed from `blocktypes.yaml`, and the directory should be renamed to `unregionalblock/` to match the actual blocktype value used.

### 3.2 The Topic Taxonomy: Fragmentation and Redundancy

The `topics` field uses a flat list of key-name pairs. With 177 unique keys across 1,057 records, the taxonomy has grown organically without consistent governance, resulting in significant fragmentation.

#### Synonymous and Redundant Topic Keys

The following groups of topic keys are functionally equivalent or nearly so, and should be consolidated:

| Redundant Group | Recommended Canonical Key | Records Affected |
|---|---|---|
| `climate`, `climate_change` | `climate_change` | 21 + 2 = 23 |
| `armscontrol`, `arms_control` | `arms_control` | 5 + 16 = 21 |
| `humanitarian`, `humanitarian_aid`, `humanitarian_assistance` | `humanitarian` | 5 + 1 + 1 = 7 |
| `economy`, `economic`, `economic_cooperation` | `economy` | 263 + 3 + 1 = 267 |
| `law`, `legal`, `legal_development` | `law` | 64 + 3 + 1 = 68 |
| `counter_terrorism`, `counterterrorism` | `counter_terrorism` | 4 + 1 = 5 |
| `disaster_relief`, `disaster` | `disaster_relief` | 4 + 1 = 5 |
| `science`, `scientific_research` | `science` | 48 + 1 = 49 |
| `transport`, `transportation` | `transport` | 2 + 59 = 61 |
| `sustainable_development`, `sustainability` | `sustainable_development` | 4 + 2 = 6 |
| `cooperation`, `international_cooperation` | `regional_cooperation` (already dominant) | 2 + 1 = 3 |

#### Sports Topic Fragmentation

The sports domain is the most extreme example of topic fragmentation. Instead of using a consistent `sports` or `sports_governance` topic, records use highly specific event or sport names:

`football` (7), `champions_league` (5), `world_cup` (3), `sports_governance` (3), `world_championships` (2), `world_championship` (1), `basketball` (1), `volleyball` (1), `beach_volleyball` (1), `cricket` (1), `tennis` (1), `davis_cup` (1), `billie_jean_king_cup` (1), `weightlifting` (1), `swimming` (1), `athletics` (1), `track_and_field` (1), `olympic_games` (1), `youth_sports` (1)

This results in 19 distinct sports-related topic keys for what is functionally a single domain. The recommended approach is to use `sports` as the primary topic key and `sports_governance` as a secondary key for governing bodies, retiring all sport-specific and event-specific topic keys.

#### Records with No Topics

69 intblock records (6.5%) have no topics assigned at all. The `acronym` category is the most affected, with all 21 acronym records lacking topics. While acronym records are definitionally about naming conventions rather than substantive policy domains, they still have thematic context (e.g., a currency acronym belongs to the `finance` or `economy` domain) and should have at least one topic assigned.

#### Recommendations for Topic Taxonomy Consolidation

The 177-key flat taxonomy should be restructured into a two-level hierarchy with approximately 30–40 top-level canonical topics and optional sub-topics. The following table proposes the top-level consolidation:

| Canonical Topic | Absorbs / Replaces |
|---|---|
| `economy` | `economic`, `economic_cooperation`, `finance`, `financial`, `banking`, `fiscal_policy` |
| `trade` | `trade_facilitation`, `customs` |
| `climate_change` | `climate`, `environment`, `environmental_protection`, `sustainability`, `sustainable_development` |
| `law` | `legal`, `legal_development`, `dispute_resolution`, `justice`, `rule_of_law` |
| `transport` | `transportation`, `aviation`, `maritime`, `ocean` (where transport-focused) |
| `science` | `scientific_research`, `research`, `mathematics`, `chemistry`, `physics` |
| `arms_control` | `armscontrol`, `nuclear`, `nuclear_security` |
| `counter_terrorism` | `counterterrorism`, `security` (where terrorism-focused) |
| `humanitarian` | `humanitarian_aid`, `humanitarian_assistance`, `disaster_relief`, `disaster` |
| `sports` | All sport-specific and event-specific keys |
| `digital` | `cybersecurity`, `ICT`, `data`, `digital_government`, `e-government`, `connectivity` |
| `health` | `medical`, `pharmaceuticals` |
| `development` | `poverty`, `poverty_alleviation`, `capacity_building`, `rural_development` |
| `human_rights` | `gender`, `refugees`, `displacement`, `migration` (where rights-focused) |

### 3.3 Specific Misclassification Examples and Recommended Corrections

Beyond the systematic issues, the following specific records warrant individual attention:

**ASEAN** is stored in `political/` with `blocktype=['economic','political','trade']`. Since `economic` is the first (primary) blocktype, it should either be moved to `economic/` or the blocktype list should be reordered to make `political` primary if that is the intended classification.

**WTO** is stored in `unagency/` with `blocktype=['trade']`. The WTO is not a UN agency — it is an independent intergovernmental organization. The `unagency` directory placement is misleading. It should be moved to a `trade/` directory, and `unagency` should be removed from its blocktype list entirely.

**G-20** is stored in `political/` with `blocktype=['political']` only, but its topics include `regional_cooperation` and `political`. The G-20 is fundamentally an economic forum. Its blocktype list should include `economic` and `forum`, and its topics should include `economy` and `finance`.

**CCASG** (Gulf Cooperation Council) is stored in `economic/` with `blocktype=['customs','economic','political']`. The primary blocktype `customs` does not match the `economic/` directory. Either the directory should be `customs/` or the blocktype list should be reordered with `economic` first.

**Records in `audit/`** (8 records including INTOSAI, EUROSAI, ASOSAI, etc.) all use `blocktype=['intorg']` with no `audit` blocktype. These are specialized audit institutions and should either have an `audit` blocktype created and assigned, or the directory should be renamed to `intorg/` and these records merged into the main `intorg/` directory.

---

## 4. Consolidated Priority Roadmap

The following table consolidates all recommendations into a single prioritized action plan:

| Priority | Area | Action | Effort |
|---|---|---|---|
| **Critical** | Taxonomy | Consolidate redundant topic keys (at minimum the 11 synonym groups identified) | Medium |
| **Critical** | Taxonomy | Align directory names with blocktype values (rename `taxation/`→`tax/`, `transportation/`→`transport/`, fix `unregionalblocks/`) | Low |
| **Critical** | Coverage | Add UNSC, UNGA, UNHRC records | Low |
| **Critical** | Intblocks | Backfill `legal_status`, `geographic_scope`, `headquarters` for high-profile records | High |
| **High** | Countries | Add `centroid: {lat, lng}` field to schema and populate all 252 records | Medium |
| **High** | Taxonomy | Define primary blocktype logic and reclassify the 169 directory-mismatch records | High |
| **High** | Coverage | Add CHIP4, DEPA, PEPFAR, MSF, EPC, D10 records | Medium |
| **High** | Coverage | Add UNCITRAL, UNCLOS records | Low |
| **High** | Countries | Enrich `adminregion`, `region`, `incomeLevel`, `lendingType` from non-WB sources for the 33 missing records | Medium |
| **High** | Intblocks | Replace 253 templated descriptions with specific content | High |
| **Medium** | Countries | Add `government_type`, `hdi`, `gdp_per_capita` fields to schema | High |
| **Medium** | Taxonomy | Restructure sports topics under a single `sports` key | Low |
| **Medium** | Taxonomy | Remove orphaned `unregionalblocks` blocktype from `blocktypes.yaml` | Low |
| **Medium** | Coverage | Add BRICSPLUS, PANDEMICTREATY, GLOBALGATEWAY, PGII, CSCE, G5SAHEL (as historical) | Medium |
| **Medium** | Intblocks | Assign topics to the 69 records currently lacking any topic | Low |
| **Medium** | Countries | Backfill `gini` with older estimates where current data unavailable | Medium |
| **Low** | Countries | Add `internet_penetration` field to schema | High |
| **Low** | Taxonomy | Establish formal governance process for adding/deprecating topics and blocktypes | Low |
| **Low** | Coverage | Evaluate and resolve remaining deferred items (MSP, CIGEPS, BIC, NSMC, BLEU, C4, MOI) | Medium |
| **Low** | Intblocks | Backfill `founded` dates for the 355 records missing this field | High |

---

## 5. Summary Statistics

| Metric | Value |
|---|---|
| Country records | 252 |
| Intblock records | 1,057 |
| Defined blocktypes | 86 |
| Unique topic keys in use | 177 |
| Country fields at 100% completeness | 8 |
| Intblock required fields at 100% completeness | 7 |
| Intblock records missing `legal_status` | 789 (74.6%) |
| Intblock records missing `geographic_scope` | 629 (59.5%) |
| Intblock records missing `headquarters` | 572 (54.1%) |
| Intblock records with templated descriptions | 253 (23.9%) |
| Records with primary blocktype–directory mismatch | 169 (16.0%) |
| Records with no topics assigned | 69 (6.5%) |
| Identified synonymous topic key groups | 11 |
| Directories with no matching blocktype | 4 |
| Blocktype values with no corresponding directory | 27 |
| Critical missing organizations (Tier 1) | 3 |
| High-priority missing organizations (Tier 2) | 8 |
| Medium-priority missing organizations (Tier 3) | 7 |

---

*Report generated by Manus AI via wide-research parallel analysis of the [datenoio/internacia-db](https://github.com/datenoio/internacia-db) repository.*
