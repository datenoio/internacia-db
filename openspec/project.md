# Project Context

## Purpose
Internacia Datasets is a comprehensive reference data repository containing structured information about countries, intergovernmental organizations, and country groups. The project serves as a data source for the **Dateno** search engine project, providing enriched geographic and organizational data for data enrichment purposes.

The project generates datasets in multiple formats (JSONL, YAML, Parquet, DuckDB) from YAML source files, with efficient Zstandard compression for distribution and consumption.

## Tech Stack
- **Python 3**: All scripts use `#!/usr/bin/env python3` shebang
- **CLI Framework**: Typer for command-line interfaces
- **Data Processing**: 
  - PyYAML for YAML parsing
  - PyArrow for Parquet schema definition and columnar data
  - DuckDB for relational database generation
  - jsonschema for source YAML validation
- **Compression**: Zstandard (zstd) at level 22 for maximum efficiency
- **Utilities**: 
  - tqdm for progress bars
  - requests for HTTP validation
- **Dev tooling**: pytest (tests/), ruff (lint + format), pre-commit; pinned in `requirements-dev.txt`
- **Data Formats**: YAML (source), JSONL, YAML, Parquet, DuckDB (output)

## Project Conventions

### Code Style
- **Python scripts**: All scripts start with `#!/usr/bin/env python3` shebang
- **Encoding**: UTF-8 encoding for all text files
- **Type hints**: Use Python type hints (`typing` module) for function parameters and return types
- **Docstrings**: Use triple-quoted docstrings for functions and modules
- **Naming**: 
  - Functions: snake_case
  - Variables: snake_case
  - Constants: UPPER_SNAKE_CASE
- **CLI**: Use Typer for all command-line interfaces with proper help text and options
- **Error handling**: Use typer.echo for user-facing messages, typer.Exit for error exits

### Architecture Patterns
- **Data Pipeline**: Source YAML files → Load → Clean → Transform → Output (multiple formats)
- **Schema-first**: Explicit PyArrow schemas defined for all datasets to ensure type consistency
- **Data Cleaning**: Dedicated `clean_data()` function to normalize data types and handle edge cases (boolean values, None values, list normalization)
- **Modular Functions**: Separate functions for each output format (JSONL, YAML, Parquet, DuckDB)
- **Progress Feedback**: Use tqdm progress bars for long-running operations
- **File Organization**:
  - Source data: `data/countries/*.yaml` and `data/intblocks/**/*.yaml`
  - Generated datasets: `data/datasets/`
  - Scripts: `scripts/`
  - Schemas: `data/schemas/`

### Testing Strategy
- **Unit/integration tests**: `tests/` (pytest) covers `clean_data` normalization, validation logic, manifest generation, and Parquet/DuckDB exports; runs in CI
- **Source validation**: `scripts/validate_countries.py` and `scripts/validate_intblocks.py` enforce JSON Schemas, completeness thresholds, duplicates, taxonomy, and cross-dataset references; both run in CI on every PR
- **Link validation**: `scripts/validate_links.py` validates URL accessibility and Wikidata entity/name consistency; runs weekly via `.github/workflows/link-validation.yml`
- **Baseline diff**: `scripts/diff_countries_baseline.py` compares countries and intblocks manifests against the main-branch baseline
- **Data Quality**: Schema enforcement through PyArrow schemas prevents type mismatches
- **Error Reporting**: Detailed error messages with file paths and specific issues

### Git Workflow
- **Versioning**: Semantic Versioning (SemVer)
- **Changelog**: Keep a Changelog format in `CHANGELOG.md`
- **Commits**: Descriptive commit messages following conventional commits

## Domain Context
- **Countries Dataset**: Reference data for 252 countries and territories. In scope:
  - ISO 3166-1 codes (alpha-2, alpha-3, numeric)
  - Geographic data (borders, continents, subregions, coordinates, centroids)
  - Demographic reference fields (population, area, Gini index where available)
  - World Bank-style classification (region, income level, lending type)
  - Cultural reference data (languages, timezones, demonyms, flag emoji)
  - Multilingual names (`other_names`, `common_names`)
  - Wikidata integration for entity linking

  **Out of scope**: socioeconomic profile expansion (HDI, GDP per capita, government type, internet penetration, and similar indicators). Do not propose or implement those fields in countries; consumers should enrich downstream.

- **International Blocks Dataset**: Contains 1,057 organizations across 51 categories:
  - Intergovernmental organizations (UN, EU, NATO, etc.)
  - Trade agreements and economic unions
  - Regional alliances and groups
  - Specialized organizations (environmental, humanitarian, scientific, etc.)
  - Membership information with join dates and roles
  - Multilingual names and translations
  - Historical data (founded, dissolved, predecessor, successor)
  - Wikidata integration for entity linking

- **Data Sources**: 
  - World Bank data for country classifications
  - Wikidata for entity linking and validation
  - Wikipedia for reference links
  - Official organization websites

- **Key Identifiers**:
  - Countries: ISO 3166-1 alpha-2 codes (e.g., "US", "FR")
  - International blocks: Custom uppercase IDs, unique across categories (e.g., "UN", "EU", "NATO")
  - Wikidata: Q-numbers (e.g., "Q30" for United States)

## Important Constraints
- **Compression**: All output formats use Zstandard compression at level 22 for maximum space efficiency
- **Encoding**: All files must use UTF-8 encoding to support international characters
- **Schema Consistency**: Data must conform to explicit PyArrow schemas - type mismatches are cleaned automatically
- **Data Quality**: 
  - URLs must be accessible (validated via HTTP)
  - Wikidata IDs must exist and match entity names
  - Required fields cannot be None (converted to empty strings or appropriate defaults)
- **File Formats**: 
  - Source: YAML files only
  - Output: Compressed formats (.zst for JSONL/YAML, .parquet for Parquet, .duckdb for DuckDB)
- **Performance**: Rate limiting for HTTP requests (0.1s delay) to avoid overwhelming external services

## External Dependencies
- **Wikidata API**: Used for entity validation and metadata retrieval
  - Base URL: `https://www.wikidata.org/w/api.php`
  - Validates entity existence and name matching
- **Related Projects**:
  - `internacia-api`: REST API service for accessing Internacia data
  - `internacia-python`: Python SDK for programmatic data access
- **Data Sources**:
  - World Bank API/data for country classifications
  - Wikipedia for reference links
  - Official organization websites for membership and metadata
