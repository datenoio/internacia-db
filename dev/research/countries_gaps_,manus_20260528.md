# Wide Research Report: `internacia-db` Countries Dataset and Repository Improvement Plan

**Author:** Manus AI  
**Date:** 2026-05-28  
**Repository reviewed:** [`datenoio/internacia-db`](https://github.com/datenoio/internacia-db)  
**Primary dataset reviewed:** `data/datasets/countries.parquet`

## Executive summary

This report presents a wide, parallelized audit of the `internacia-db` repository, with special focus on the `countries.parquet` dataset. The review combined programmatic dataset inspection, cross-dataset relationship checks against the `intblocks` source files, an ISO-style country-code coverage comparison, and independent parallel research branches covering schema quality, coverage, identifiers, localization, geography, socioeconomic data, repository architecture, and country–intblock relationships.

The repository is already valuable because it publishes countries, territories, intergovernmental organizations, and country groups in several useful formats: JSONL, YAML, Parquet, and DuckDB. The README states that the countries dataset has **252 country and territory records** and that datasets are generated from YAML sources into multiple consumption formats.[1] However, the audit found that several high-value fields are currently empty or incomplete, and some schema contracts are not yet enforced. The most important issue is that **five advertised country-profile fields are 100% missing**: `population`, `area`, `gini`, `timezones`, and `native_names`. This limits analytical value and creates a gap between the documented schema and actual usable content.

The dataset’s country-code coverage is strong for current ISO-style alpha-2 coverage: comparison with a current ISO 3166-derived open list found **no missing current ISO-style alpha-2 entries** and **three extra entries**: `AN`, `JG`, and `KV`. ISO explains that ISO 3166-1 assigns current country codes, ISO 3166-3 covers formerly used country names, and user-assigned code elements such as `XA`–`XZ` are not mutually compatible between organizations.[2] Therefore, these three records should not simply be deleted without policy discussion; instead, the repository should explicitly model them as obsolete, collective, or user-assigned/special-status records.

> ISO states that the purpose of ISO 3166 is to define internationally recognized codes, but it also warns that user-assigned code elements are defined by users themselves and are not compatible between different entities.[2]

The repository’s strongest near-term opportunity is to turn `internacia-db` from a useful registry into a **validated reference data product**. This requires field-level provenance, automated schema validation, continuous integration checks, standardized treatment of dependencies and disputed entities, richer country profiles, and better cross-dataset normalization between countries and international blocks.

![Top missing fields](https://private-us-east-1.manuscdn.com/sessionFile/Julqo7xKuzqiGduepv1XqX/sandbox/ltXEKem2QeO3pedeOw4LKX-images_1779997848467_na1fn_L2hvbWUvdWJ1bnR1L2ludGVybmFjaWFfcmVwb3J0L21pc3NpbmdfZmllbGRz.png?Policy=eyJTdGF0ZW1lbnQiOlt7IlJlc291cmNlIjoiaHR0cHM6Ly9wcml2YXRlLXVzLWVhc3QtMS5tYW51c2Nkbi5jb20vc2Vzc2lvbkZpbGUvSnVscW83eEt1enFpR2R1ZXB2MVhxWC9zYW5kYm94L2x0WEVLZW0yUWVPM3BlZGVPdzRMS1gtaW1hZ2VzXzE3Nzk5OTc4NDg0NjdfbmExZm5fTDJodmJXVXZkV0oxYm5SMUwybHVkR1Z5Ym1GamFXRmZjbVZ3YjNKMEwyMXBjM05wYm1kZlptbGxiR1J6LnBuZyIsIkNvbmRpdGlvbiI6eyJEYXRlTGVzc1RoYW4iOnsiQVdTOkVwb2NoVGltZSI6MTc5ODc2MTYwMH19fV19&Key-Pair-Id=K2HSFNDJXOU9YS&Signature=ujtieIQiR4gs4yAw5BFb96271MeHq8xLh5sSoH6vlwJPM2SKYACZQADrpSe2OoMMfFOU7uuPMd~j9WslQxzqbJ-jQSQJm2XrougUwsmSje78vxNSUjhjnkdst5aHk8nI1bCQpIhzKcsTJ5oES8RhJCZbh~fiJo-I6DozFuzkLZBXOz3FVu9EO~Wd5c4zU28ZR8dm36REUNwiaztdm0exxR-UHkXVyIIIp1U14Zyd~SC91nRiXmxdO3Yl9eRJ6xAfUVyCtBKnyFMM00KsST3BlHT4W~2p4XqImNObxyFEWHMkAEAEzw41ShOJqSQo-EiABbgnaycirXy79kvhjGmezg__)

## Scope and methodology

The analysis used the current `main` branch of the repository cloned from GitHub and inspected `countries.parquet`, all country YAML source files, `data/intblocks/**/*.yaml`, `README.md`, `CHANGELOG.md`, and utility scripts under `scripts/`. Parallel processing was used to execute eight independent review branches. A separate local audit script computed completeness, format, duplicate, relationship, and coverage metrics. External reference context was taken from ISO 3166 documentation, UN M49 methodology, World Bank metadata documentation, and Wikidata data-access guidance.[2] [3] [4] [5]

| Parallel branch | Priority | Confidence |
|---|---:|---:|
| Schema and completeness audit | Critical | 0.95 |
| Country and territory coverage audit | High | 1.00 |
| Standards and identifier consistency audit | High | 0.95 |
| Names and localization audit | High | 0.95 |
| Geographic and geopolitical attributes audit | High | 0.95 |
| Demographic and socioeconomic attributes audit | High | 0.95 |
| Repository architecture, generation pipeline, and documentation audit | High | 0.95 |
| Relationship audit between countries and international blocks | Medium | 0.95 |

The findings below distinguish between **dataset content gaps**, where data is missing or incomplete, and **repository governance gaps**, where validation, provenance, documentation, or release mechanics could be improved. This distinction matters because some gaps can be filled by adding values, whereas others require schema and policy decisions.

## Dataset snapshot

The audited `countries.parquet` file contains **252 rows** and **33 columns**. The repository also has **252 country YAML source files**, **1,065 international-block YAML source files**, and generated datasets for countries, intblocks, blocktypes, and DuckDB. The country table has no duplicate `code`, `iso3code`, or numeric-code values in the current snapshot.

| Metric | Value | Interpretation |
|---|---:|---|
| Country/territory rows | 252 | Broad coverage of countries and territories. |
| Country columns | 33 | Rich schema, including identifiers, geography, localization, and socioeconomic fields. |
| Country source YAML files | 252 | Source file count matches generated country row count. |
| Current ISO-style alpha-2 entries missing | 0 | Strong coverage for current ISO-style country and territory codes. |
| Extra dataset codes outside current ISO-style list | 3 | `AN`, `JG`, and `KV` need explicit code-status governance. |
| Fully empty fields | 5 | `population`, `area`, `gini`, `timezones`, and `native_names`. |
| Border references | 644 | All are alpha-3 codes, while README says `borders` is a list of country codes and `code` is alpha-2. |
| Country include records in intblocks | 42,160 | Very extensive relationship coverage. |
| Typed country references missing from countries dataset | 4 | `XA`, `XS`, `XT`, `XN` in `CIS2.yaml`. |

## Completeness audit

The central finding is that multiple high-value fields are present in the schema but absent in the data. The dataset therefore looks complete structurally, but several fields cannot yet support analysis, display, or enrichment use cases.

| Field | Missing or empty records | Missing rate | Example affected codes |
|---|---:|---:|---|
| `area` | 252 | 100.00% | TJ, JM, HT, ST, MS |
| `gini` | 252 | 100.00% | TJ, JM, HT, ST, MS |
| `native_names` | 252 | 100.00% | TJ, JM, HT, ST, MS |
| `population` | 252 | 100.00% | TJ, JM, HT, ST, MS |
| `timezones` | 252 | 100.00% | TJ, JM, HT, ST, MS |
| `adminregion` | 107 | 42.46% | MS, AE, NL, LU, SA |
| `borders` | 89 | 35.32% | JM, ST, MS, TF, AI |
| `common_names` | 59 | 23.41% | JM, MS, BZ, MF, AI |
| `incomeLevel` | 33 | 13.10% | MS, TF, AI, BV, EH |
| `lendingType` | 33 | 13.10% | MS, TF, AI, BV, EH |
| `region` | 33 | 13.10% | MS, TF, AI, BV, EH |
| `capital_city` | 11 | 4.37% | BV, HM, PS, AQ, GI |
| `subregion` | 8 | 3.17% | TF, BV, HM, AQ, JG |
| `currencies` | 6 | 2.38% | BV, HM, AQ, JG, AN |
| `other_names` | 6 | 2.38% | JG, PT, CO, AN, KV |
| `wikidata_id` | 6 | 2.38% | JG, PT, CO, AN, KV |
| `calling_codes` | 5 | 1.98% | HM, AQ, JG, AN, KV |
| `languages` | 4 | 1.59% | AQ, JG, AN, KV |

The five 100% empty fields should be treated as **critical release blockers** if the public schema implies they are available. `population` and `area` are foundational facts for nearly every country profile. `timezones` and `native_names` are important for application-level localization and practical country lookup. `gini` is less universally available, but it should either be populated where possible with a `{year, value, source}` structure or renamed/documented as optional.

`adminregion`, `region`, `incomeLevel`, and `lendingType` are World Bank-style fields, and their missingness is concentrated in territories and special entities. This is not necessarily an error, because the World Bank’s country metadata distinguishes concepts such as country, region, income group, and source metadata and does not classify every non-sovereign territory in every field.[4] The improvement should be to document why a value is missing, not to force a World Bank classification where none exists.

## Country and territory coverage

The dataset covers all 249 current ISO-style alpha-2 codes in the reference comparison and adds three non-current or non-standard records. ISO 3166 is relevant because it defines alpha-2, alpha-3, and numeric country-code elements and is maintained to reflect changes in country names and subdivisions.[2] The UN M49 standard is also relevant because it provides country or area names, three-digit numerical codes, and ISO alpha-3 codes for statistical use.[3]

| Code | Dataset name | Status issue | Recommendation |
|---|---|---|---|
| `AN` | Netherlands Antilles | Former ISO 3166-1 code; Netherlands Antilles was dissolved and its successors are represented by current codes such as `CW`, `SX`, and `BQ`. | Move to a historical/obsolete entity layer or keep only with `code_status: obsolete` and ISO 3166-3 metadata. |
| `JG` | Channel Islands | Not a current ISO 3166-1 alpha-2 code for a collective Channel Islands entity; Guernsey and Jersey have current separate codes. | Prefer `GG` and `JE` as countries/territories; model Channel Islands as a grouping rather than a country code. |
| `KV` | Kosovo | Commonly used user-assigned code, but not an official ISO 3166-1 code. | Keep if useful, but mark as `code_status: user_assigned`, `sovereignty_status: disputed_or_partially_recognized`, and document source policy. |

The answer to “which countries should be added” depends on the repository’s intended scope. If the scope is **current ISO 3166-1 countries and areas**, no current ISO-style alpha-2 records are missing. If the scope includes **special-status or disputed entities referenced by international blocks**, then four entities referenced as `type: country` in `data/intblocks/political/CIS2.yaml` are absent from country profiles: `XA` Abkhazia, `XS` South Ossetia, `XT` Transnistria, and `XN` Artsakh/Nagorno-Karabakh. ISO specifically states that user-assigned code elements such as `XA`–`XZ` are available for users but are not compatible across entities.[2] Therefore, these should be added only if the repository adopts an explicit special-status entity policy.

| Potential addition | Reason to consider | Recommended treatment |
|---|---|---|
| Abkhazia (`XA`) | Referenced as `type: country` in an intblock source file. | Add to a special-status profile layer or change intblock type from `country` to `disputed_entity`. |
| South Ossetia (`XS`) | Referenced as `type: country` in an intblock source file. | Add only with user-assigned code and dispute metadata. |
| Transnistria (`XT`) | Referenced as `type: country` in an intblock source file. | Add only if non-ISO political entities are in scope. |
| Artsakh/Nagorno-Karabakh (`XN`) | Referenced as `type: country`; current status is historically sensitive and changed over time. | Avoid treating as a current country without date/status metadata; consider historical/disputed entity modeling. |

## Identifier and standards consistency

Identifier coverage is generally strong for core ISO-style identifiers. There were no bad alpha-2, alpha-3, numeric, or M49 format values in the local audit. However, the dataset has **schema-contract inconsistencies** and incomplete external identifiers.

| Area | Finding | Recommendation |
|---|---|---|
| ISO and M49 identifiers | Alpha-2, alpha-3, numeric, and M49 formats are syntactically clean. | Add validation tests that fail the build on malformed values and duplicate identifiers. |
| Wikidata IDs | 6 records are missing `wikidata_id`. | Fill missing IDs or add `wikidata_status` with reason such as obsolete, no item, or disputed mapping. |
| Borders | 644 border references are alpha-3 values such as `AFG`, `CHN`, `KGZ`; the dataset primary `code` is alpha-2. | Either convert `borders` to alpha-2 or rename/document as `border_iso3codes`; add reciprocal-border validation. |
| TLDs and calling codes | TLDs are missing for 3 entries and calling codes for 5. | Permit nulls for areas without assigned calling codes/TLDs, but encode reason codes. |
| Timezones | All 252 records lack timezones. | Populate from IANA TZDB-compatible sources and support multiple zones per country. |
| UN M49 | M49 is suitable for statistical country/area codes; UN notes that group assignments are for statistical convenience and not political affiliation.[3] | Use M49 for geoscheme fields and include a disclaimer for political neutrality. |

The border issue is particularly important because it can silently break consumers. If users expect `borders` to contain the same identifier type as `code`, then current values are “invalid” from the consumer’s perspective even though they are valid ISO alpha-3 codes. A backwards-compatible solution is to add `border_codes_alpha2` while deprecating or documenting existing alpha-3 `borders`.

## Names, localization, and country-profile richness

Names and localization are one of the most promising areas for profile extension. The dataset already has `official_name`, `other_names`, `common_names`, `languages`, `demonym`, and `flag_emoji` fields, but `native_names` is entirely missing and `common_names` is missing for 59 records. Wikidata is a reasonable enrichment source for labels, aliases, and multilingual values, but its own data-access guidance emphasizes choosing access methods carefully and avoiding excessive load.[5]

| Field or feature | Current state | Improvement opportunity |
|---|---|---|
| `native_names` | 252/252 missing. | Populate native official and common names keyed by language code. |
| `common_names` | 59 missing. | Add aliases used in search, data matching, and common English usage. |
| `other_names` | 6 missing. | Normalize translation identifiers and include source language. |
| `official_name` | 3 missing, concentrated in `AN`, `JG`, `KV`. | Resolve through entity-status policy. |
| Demonyms | 3 missing. | Add demonyms with language and gender/neutral form where available. |
| Profile extension | No field-level provenance. | Add `sources` or `provenance` at field level for names, identifiers, and indicators. |

A mature country-profile record should include both stable identifiers and practical display metadata. Recommended additions include `short_name`, `official_name`, `name_variants`, `native_names`, `endonyms`, `exonyms`, `former_names`, `date_valid_from`, `date_valid_to`, `recognition_status`, and `source`. This would allow the repository to handle “Turkey/Türkiye”, “Czech Republic/Czechia”, “Swaziland/Eswatini”, and “Macedonia, FYR/North Macedonia” without losing historical or common usage.

## Geographic and geopolitical attributes

Geographic data is incomplete in several places. The entire `area` column is empty, `capital_city` is missing for 11 records, and one capital record, United States Minor Outlying Islands, has `Washington DC` as the name but no coordinates. There are also five trailing whitespace issues in structured region values. These are small but important quality issues because categorical whitespace can create duplicate categories in downstream analytics.

![Entity classification](https://private-us-east-1.manuscdn.com/sessionFile/Julqo7xKuzqiGduepv1XqX/sandbox/ltXEKem2QeO3pedeOw4LKX-images_1779997848467_na1fn_L2hvbWUvdWJ1bnR1L2ludGVybmFjaWFfcmVwb3J0L2VudGl0eV9jbGFzc2lmaWNhdGlvbg.png?Policy=eyJTdGF0ZW1lbnQiOlt7IlJlc291cmNlIjoiaHR0cHM6Ly9wcml2YXRlLXVzLWVhc3QtMS5tYW51c2Nkbi5jb20vc2Vzc2lvbkZpbGUvSnVscW83eEt1enFpR2R1ZXB2MVhxWC9zYW5kYm94L2x0WEVLZW0yUWVPM3BlZGVPdzRMS1gtaW1hZ2VzXzE3Nzk5OTc4NDg0NjdfbmExZm5fTDJodmJXVXZkV0oxYm5SMUwybHVkR1Z5Ym1GamFXRmZjbVZ3YjNKMEwyVnVkR2wwZVY5amJHRnpjMmxtYVdOaGRHbHZiZy5wbmciLCJDb25kaXRpb24iOnsiRGF0ZUxlc3NUaGFuIjp7IkFXUzpFcG9jaFRpbWUiOjE3OTg3NjE2MDB9fX1dfQ__&Key-Pair-Id=K2HSFNDJXOU9YS&Signature=cZHDADdhEMdo~EKLltyusquVuMNpD8y4MnN2zLf61ifONTv0ef3Di9-iwS3ebECzX13IfGToWnZLv4tgWz1EgMs4RDsW6FAh5kbEIt5rj-r8iBhX-SJOva2cCVPIymEAGqtXwxDs5XvbdxHBfgmMuZswvXmJXQz7mpidNdEJwMGKNdjXhROGWqGKvWgjyMdnBGhCY6aWQlTsM2Gj102jOPgXcHqU5mYv6oHELUiOVVhXdbvc1aKgsdaGzRmjmMnP-sz334Pnyz791r~cPO1ZRnU2J3DFHAYDyX~3-3yjMnQc43t7vzTQHMpopdIn8yRTIuU0WLHvOqPf4nY9eOODDA__)

| Topic | Finding | Suggested fix |
|---|---|---|
| Area | 252/252 missing. | Populate in square kilometers with source and year/method. |
| Capital city | 11 missing; `UM` has missing coordinates. | Add coordinates when meaningful; otherwise add `capital_applicability: not_applicable`. |
| Region strings | Five trailing-whitespace issues. | Strip categorical values during build and validate clean strings. |
| Landlocked and borders | Many island territories have empty borders, which is valid; landlocked countries correctly have land borders. | Document that `borders` means land borders and use empty lists rather than nulls for island/no-land-border cases. |
| Dependent and disputed territories | 55 dependent/non-sovereign areas, 2 independent non-UN/special-status entities, and 3 unknown-status entities. | Add explicit `entity_type`, `sovereignty_status`, `parent_entity`, and `recognition_notes`. |

For dependent territories, the repository should avoid overloading `independent` and `un_member` as the only status fields. Recommended values for `entity_type` include `sovereign_state`, `dependent_territory`, `special_administrative_region`, `disputed_territory`, `historical_entity`, `supranational_grouping`, and `statistical_area`.

## Demographic and socioeconomic attributes

The socioeconomic schema is ambitious but currently underfilled. `population`, `area`, and `gini` are all 100% missing, while World Bank-style classification fields are missing for 33 records. World Bank metadata documentation shows that its API exposes country concepts, metatypes such as income group, and metadata for indicators including population.[4] This makes the World Bank a practical source for automated updates, with the caveat that dependent territories and special entities may not be classified.

| Indicator group | Recommended fields | Candidate sources and notes |
|---|---|---|
| Population | `population.value`, `population.year`, `population.source` | World Bank `SP.POP.TOTL` for many entities; UN Population Division for broader coverage. |
| Economy | GDP, GDP per capita, income group, lending type | World Bank and IMF, with clear missing-reason handling for territories. |
| Inequality | `gini.value`, `gini.year`, `gini.source` | World Bank `SI.POV.GINI`, but sparse for many territories. |
| Geography | Area, land area, coastline, centroid | UN/World Bank/Wikidata/geospatial sources; include method and date. |
| Human development | HDI, life expectancy, literacy, internet use | UNDP and World Bank indicators, with optional profile modules. |

The report recommends not storing a bare integer for `population`. Instead, use a structured value such as `{value, year, source, source_url, retrieved_at}`. For indicators that change frequently, include `latest_available_year` and avoid implying real-time freshness.

## Country–intblock relationship quality

The relationship between countries and international blocks is a major strength. The intblock source set contains 42,160 country include records and references every country in `countries.parquet` at least once. This indicates that the country dataset is not isolated; it is deeply connected to the repository’s main international-block use case.

However, relationship quality could be improved. Four typed country references in `CIS2.yaml` are missing from the countries dataset, and there are 3,832 country-name mismatches between include names and canonical country names. Many mismatches are understandable synonyms or historical/common variants, such as `Türkiye` vs. `Turkey`, `Czechia` vs. `Czech Republic`, `Viet Nam` vs. `Vietnam`, and `Côte d'Ivoire` vs. `Cote d'Ivoire`. The issue is not that all names must be identical; rather, the repository should distinguish **identifier integrity** from **display-name provenance**.

| Relationship issue | Count | Interpretation | Recommendation |
|---|---:|---|---|
| Country include records | 42,160 | Rich cross-dataset membership graph. | Maintain and expose as first-class relationship table. |
| Unique country include references | 256 | More than country table because of four missing special entities. | Resolve special entities or change include type. |
| Missing typed country references | 4 | `XA`, `XS`, `XT`, `XN` appear as `type: country`. | Add special-status profiles or reclassify. |
| Name mismatches | 3,832 | Mostly canonical-name differences and aliases. | Store only IDs as authoritative; treat include names as source labels or aliases. |
| Organization include records | 89 | Includes can reference organizations such as EU. | Document `includes.type` vocabulary and validate by type. |

A robust design would create separate tables for `country_profiles`, `intblocks`, and `memberships`. The membership table would carry `member_id`, `member_type`, `source_label`, `canonical_label`, `status`, `joined`, `left`, and `source`. This would preserve original source labels while allowing canonical joins.

## Repository and pipeline improvement plan

The repository has a clear structure and useful generated outputs, but it should add stricter governance. The README documents schemas and generated formats, but it does not yet describe validation guarantees, field-level provenance, update frequency, or status policy for non-standard entities.[1]

| Area | Current strength | Recommended improvement |
|---|---|---|
| Data layout | Clear `data/countries`, `data/intblocks`, and generated `data/datasets`. | Add `schemas/` and enforce schemas in the build. |
| Formats | JSONL, YAML, Parquet, DuckDB. | Add dataset metadata files: version, build date, source commit, row count, schema hash. |
| Build script | Generates multiple formats. | Fail builds on schema violations, duplicate IDs, malformed codes, and unexpected nulls. |
| Validation | Link validation script exists. | Add checks for country-code policy, null thresholds, border identifier type, and intblock member references. |
| Documentation | README provides schemas and usage. | Add data dictionary, status-policy document, examples for consumers, and known-null semantics. |
| Releases | Changelog exists. | Add machine-readable changelog and migration notes for breaking schema changes. |
| Provenance | Some enrichment scripts imply external sources. | Store source URL, retrieval date, license, and confidence per field or source group. |
| CI/CD | Not evident in the cloned repository snapshot. | Run validation, build, and row-count/schema diff checks on every pull request. |

The most important governance improvement is to introduce a **quality gate**. For example, the build should fail if a field advertised as populated is 100% null, if a code is outside ISO without an explicit status, if a country include with `type: country` does not resolve to a country or special-status entity, or if a region value contains leading/trailing whitespace.

## Recommended roadmap

| Priority | Recommendation | Evidence |
|---|---|---|
| Critical | Populate completely empty analytical fields: `population`, `area`, `gini`, `timezones`, `native_names`. | These five fields are 100% missing across 252 records; they are currently schema promises rather than usable data. |
| High | Resolve non-standard country-code policy for `AN`, `JG`, and `KV`; add explicit `entity_status` and `code_status` fields. | Dataset covers all 249 ISO-style current alpha-2 entries but contains three extra codes that require policy decisions. |
| High | Normalize borders to the schema’s alpha-2 contract, or update the schema to state alpha-3. | All 644 border references are alpha-3 while the README says country codes are ISO alpha-2. |
| High | Introduce automated validation and CI for completeness, code standards, links, and cross-dataset references. | Current outputs contain trailing whitespace, missing core fields, and thousands of country-name mismatches across intblocks. |
| Medium | Improve country profile richness with subdivisions, official sources, localization, geospatial boundaries, and economic indicators. | The repository is already strong as a reference dataset, but profile usefulness would increase materially with richer provenance and indicators. |
| Medium | Add provenance metadata at field level and dataset-level release metadata. | Reproducibility and trust would improve if every externally sourced value had source, retrieval date, and update cadence. |

### Phase 1: stabilize the schema and validation

The first phase should add schema validation, code-status policy, and build-time quality thresholds. It should also clarify whether `borders` uses alpha-2 or alpha-3 codes. This is foundational because it prevents downstream consumers from building against ambiguous semantics.

### Phase 2: fill high-value country-profile fields

The second phase should populate `population`, `area`, `timezones`, and `native_names`. `gini` should be populated where available and explicitly null where unavailable. The repository should avoid storing mutable socioeconomic indicators without year and source metadata.

### Phase 3: formalize entity-status modeling

The third phase should resolve `AN`, `JG`, `KV`, and the intblock-implied `XA`, `XS`, `XT`, `XN` records. The recommended approach is to support a broader entity model rather than forcing all entries into “country” semantics. This is especially important because UN M49 itself notes that geographical groupings are for statistical convenience and do not imply political affiliation.[3]

### Phase 4: mature repository operations

The final phase should add CI, tests, provenance, versioned releases, and consumer-facing documentation. This would make `internacia-db` more reliable for SDK/API users and easier for contributors to improve without regressions.

## Suggested schema extensions

| New or revised field | Type | Purpose |
|---|---|---|
| `entity_type` | enum | Distinguish sovereign states, dependent territories, disputed entities, historical entities, and groupings. |
| `code_status` | enum | Mark `official_iso3166_1`, `user_assigned`, `obsolete`, `internal`, or `exceptionally_reserved`. |
| `validity` | struct | Store `valid_from`, `valid_to`, and historical status. |
| `parent_entity` | struct/list | Link dependent territories to administering state(s). |
| `recognition_status` | struct | Capture UN membership, observer status, partial recognition, or dispute notes. |
| `provenance` | list/struct | Capture source URL, source name, retrieved date, license, and confidence. |
| `indicators` | list/struct | Store socioeconomic indicators with value, year, unit, and source rather than many sparsely populated top-level fields. |
| `geo` | struct | Add centroid, bounding box, area, land area, and optional geometry links. |
| `name_history` | list/struct | Track official and common name changes over time. |
| `aliases` | list/struct | Replace or complement `common_names` with language, label, and source. |

## Conclusion

`internacia-db` already has broad country and territory coverage, strong generated-format support, and an unusually rich international-block relationship graph. Its main weakness is not lack of ambition; it is that the public schema is ahead of the populated data and validation layer. The highest-impact improvements are to populate the five completely empty fields, clarify non-standard and special-status entities, normalize border-code semantics, add source provenance, and enforce quality gates through CI.

If the repository implements these recommendations, it can become a more dependable reference database for country profiles and international organizational membership, suitable for SDK/API consumption, data enrichment, and analytical use cases.

## References

[1]: https://github.com/datenoio/internacia-db "datenoio/internacia-db README"
[2]: https://www.iso.org/iso-3166-country-codes.html "ISO 3166 — Country Codes"
[3]: https://unstats.un.org/unsd/methodology/m49/ "UNSD Methodology — Standard Country or Area Codes for Statistical Use (M49)"
[4]: https://datahelpdesk.worldbank.org/knowledgebase/articles/1886695-metadata-api-queries "World Bank Metadata API Queries"
[5]: https://www.wikidata.org/wiki/Wikidata:Data_access "Wikidata: Data access"
