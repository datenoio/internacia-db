# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.1.0] - 2025-01-XX

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
- **Dataset expansion**: Increased international blocks from 727 to 1001+ files across 53+ categories

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
