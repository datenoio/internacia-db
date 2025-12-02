# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
