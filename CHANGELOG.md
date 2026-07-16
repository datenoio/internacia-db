# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
