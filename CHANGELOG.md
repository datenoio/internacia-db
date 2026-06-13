# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- **Data license**: explicit `DATA_LICENSE` (CC BY 4.0) for datasets, separate from the MIT code license, plus `ATTRIBUTION.md` documenting World Bank (CC BY 4.0), Wikidata (CC0), and IANA tzdata sources and a recommended citation. Build manifests and metadata now carry a `data_license` SPDX field.
- **Self-describing datasets**: `internacia.duckdb` now includes a `_meta` table (one row per dataset with `version`, `build_date`, `git_commit`, `row_count`, `schema_hash`, `data_license`); each Parquet export is accompanied by a `<dataset>.meta.json` sidecar.
- **Identifier stability**: `data/intblocks_aliases.yaml` source plus generated `intblocks_aliases.{json,parquet}` mapping retired/renamed intblock ids to current ids (`reason`: `renamed`/`merged`/`disambiguated`). `validate_intblocks.py` checks alias integrity (targets resolve; collisions allowed only when `disambiguated`). Seeded with the v1.3.0 `ASF`→`FSA` and `CAF`→`CAFBANK` disambiguations.

### Changed

- **Release assets**: the release workflow now publishes `*.meta.json` sidecars and the `intblocks_aliases.*` artifacts.

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
