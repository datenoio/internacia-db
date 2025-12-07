# Internacia Datasets


This repository contains comprehensive datasets of countries, intergovernmental organizations, and country groups. It serves as a reference data source for data enrichment the **Dateno** search engine project.

This script generates datasets from the `data/countries` and `data/intblocks` directories in multiple formats for easy consumption.

## Roadmap

- [x] Create a Python SDK for easy data access - See [internacia-python](../internacia-python)
- [x] Develop a REST API for data retrieval - See [internacia-api](../internacia-api)

The datasets are stored in the `data/datasets` directory.   

The datasets are compressed with Zstandard compression for maximum efficiency.

## Features

- ✅ Uses **typer** for clean CLI interface
- ✅ Generates datasets in **JSONL**, **YAML**, **Parquet**, and **DuckDB** formats
- ✅ Uses **Zstandard** compression for all file formats for maximum efficiency
- ✅ Uses **tqdm** progress bars for visual feedback
- ✅ Flexible output directory configuration
- ✅ Selective format generation

## Installation

Install required dependencies:

```bash
pip install -r scripts/requirements.txt
```

## Usage

### Display Information

Show information about available data sources:

```bash
python3 scripts/builder.py info
```

### Build All Datasets

Generate datasets in all formats (JSONL, YAML, Parquet, DuckDB):

```bash
python3 scripts/builder.py build
```

This will create the following files in `data/datasets/`:
- `countries.jsonl.zst` - All countries data in JSONL format (Zstd compressed)
- `countries.yaml.zst` - All countries data in YAML format (Zstd compressed)
- `countries.parquet` - All countries data in Parquet format (Zstd compressed)
- `intblocks.jsonl.zst` - All international blocks data in JSONL format (Zstd compressed)
- `intblocks.yaml.zst` - All international blocks data in YAML format (Zstd compressed)
- `intblocks.parquet` - All international blocks data in Parquet format (Zstd compressed)
- `internacia.duckdb` - DuckDB database with `countries` and `intblocks` tables

### Build Specific Formats

Generate only specific formats:

```bash
# Generate only JSONL and DuckDB
python3 scripts/builder.py build --formats jsonl,duckdb

# Generate only Parquet
python3 scripts/builder.py build --formats parquet
```

### Custom Output Directory

Specify a custom output directory:

```bash
python3 scripts/builder.py build --output-dir /path/to/output
```

## Output Formats

### JSONL & YAML (Zstandard Compressed)
- **JSONL**: Line-delimited JSON, compressed with Zstandard (`.jsonl.zst`). Efficient for streaming and large datasets.
- **YAML**: Standard YAML, compressed with Zstandard (`.yaml.zst`).
- **Compression**: All text formats use high-level Zstandard compression (level 22) for maximum space savings.

To decompress:
```bash
zstd -d data/datasets/countries.jsonl.zst
```

### Parquet
Columnar storage format optimized for analytics.
- **Compression**: Zstandard compressed (level 22).
- **Schema**: Explicitly typed with native nested structures (Lists and Structs).

### DuckDB
Full relational database with SQL support. Nested structures are stored as native DuckDB `LIST` and `STRUCT` types.

```python
import duckdb

con = duckdb.connect('data/datasets/internacia.duckdb')

# Query nested structures directly
# Example: Get all English translations
con.execute("""
    SELECT id, name, t.name as english_name 
    FROM intblocks, UNNEST(translations) as t 
    WHERE t.lang = 'en' 
    LIMIT 5
""").fetchall()
```

## Dataset Structure

### Countries Schema
The `countries` dataset contains detailed information about 252 countries and territories.

| Field | Type | Description |
|-------|------|-------------|
| `code` | String | ISO 3166-1 alpha-2 code (e.g., "US") |
| `name` | String | Common name |
| `iso3code` | String | ISO 3166-1 alpha-3 code |
| `capital_city` | Struct | `{name, lng, lat}` |
| `region` | Struct | World Bank region `{id, value}` |
| `adminregion` | Struct | World Bank admin region `{id, value}` |
| `incomeLevel` | Struct | World Bank income level `{id, value}` |
| `lendingType` | Struct | World Bank lending type `{id, value}` |
| `numeric_code` | String | ISO 3166-1 numeric code |
| `wikidata_id` | String | Wikidata Item ID |
| `official_name` | String | Official full name |
| `languages` | List[Struct] | List of `{code, name, official}` |
| `currencies` | List[Struct] | List of `{code, name, symbol}` |
| `un_member` | Boolean | Is UN member? |
| `independent` | Boolean | Is independent state? |
| `subregion` | String | UN subregion |
| `continents` | List[String] | List of continents |
| `borders` | List[String] | List of bordering country codes |
| `landlocked` | Boolean | Is landlocked? |
| `tld` | String | Top-level domain |
| `calling_codes` | List[String] | Telephone calling codes |
| `flag_emoji` | String | Flag emoji |
| `car_side` | String | Driving side |
| `start_of_week` | String | Start of week day |
| `demonyms` | Struct | `{female, male}` |
| `m49_code` | String | UN M49 code |
| `population` | Integer | Population estimate |
| `area` | Float | Area in sq km |
| `gini` | Struct | Gini index `{year, value}` |
| `timezones` | List[String] | List of timezones |
| `native_names` | Map | Map of lang code -> `{official, common}` |
| `other_names` | List[Struct] | Name translations in different languages `{id, name}` |
| `common_names` | List[String] | Common names and aliases |

### International Blocks Schema
The `intblocks` dataset contains information about international organizations, alliances, and unions.

| Field | Type | Description |
|-------|------|-------------|
| `id` | String | Unique identifier |
| `blocktype` | List[String] | Types of block (e.g., "Political Union") |
| `status` | String | Current status |
| `name` | String | Name of the block |
| `languages` | List[String] | Official languages |
| `links` | List[Struct] | External links `{url, type}` |
| `other_names` | List[Struct] | Name translations in different languages `{id, name}` |
| `founded` | String | Foundation year/date |
| `geographic_scope` | String | Scope (e.g., "Regional", "Global") |
| `regions` | List[String] | Regions covered |
| `includes` | List[Struct] | Member countries `{id, name, type, status, joined, role, note}` |
| `membership_count` | Integer | Number of members |
| `wikidata_id` | String | Wikidata Item ID |
| `legal_status` | String | Legal status |
| `description` | String | Brief description |
| `tags` | List[String] | Classification tags |
| `topics` | List[Struct] | Related topics `{key, name}` |
| `headquarters` | Struct | `{city, country, coordinates: {lat, lng}}` |
| `acronyms` | List[Struct] | Acronyms `{lang, value}` |
| `partof` | List[String] | Parent organizations |
| `dissolved` | String | Dissolution date (if applicable) |
| `predecessor` | String | Predecessor organization |
| `successor` | String | Successor organization |

## Command Reference

```bash
# Show general help
python3 scripts/builder.py --help

# Show help for build command
python3 scripts/builder.py build --help

# Show data source information
python3 scripts/builder.py info
```

## Data Sources

The builder reads YAML files from:
- `data/countries/*.yaml` - Country data (252 files)
- `data/intblocks/**/*.yaml` - International blocks data (1021+ files across 53+ categories)

## Notes

- Progress bars show real-time loading status
- All generated files use UTF-8 encoding
- Nested structures in Parquet/DuckDB are JSON-serialized for compatibility
- Existing output files are overwritten without warning

## Related Projects

- [internacia-api](../internacia-api): REST API service for accessing Internacia data
- [internacia-python](../internacia-python): Python SDK for programmatic data access
