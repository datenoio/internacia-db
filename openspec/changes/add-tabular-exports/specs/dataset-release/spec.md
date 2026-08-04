## ADDED Requirements

### Requirement: Flattened CSV country and intblock exports

Each dataset build SHALL publish flattened `countries.csv` and `intblocks.csv` with one row per record, suitable for spreadsheet tools without nested-structure parsing.

#### Scenario: Excel opens countries CSV

- **WHEN** a non-technical user opens `countries.csv` in Excel or Google Sheets
- **THEN** each country appears on one row with scalar columns including code, name, iso3code, and flattened population/area values

#### Scenario: CSV row count matches Parquet

- **WHEN** the artifact-consistency guard runs
- **THEN** CSV row counts match Parquet and DuckDB for countries and intblocks

### Requirement: Lite export variants

The build SHALL publish lite variants (`countries-lite.parquet`, `countries-lite.csv`, `intblocks-lite.parquet`, `intblocks-lite.csv`) containing only identifier, naming, and classification fields documented in `docs/ai-consumers.md`.

#### Scenario: Lite countries fit context-constrained agents

- **WHEN** an LLM agent loads `countries-lite.parquet`
- **THEN** the column set excludes heavy nested fields while preserving code, name, iso3code, wikidata_id, entity_type, and code_status

#### Scenario: Lite and full share primary keys

- **WHEN** a consumer joins lite and full exports on `code` or `id`
- **THEN** every lite row matches exactly one full record

### Requirement: Plain JSON array artifacts

The build SHALL publish `countries.json` and `intblocks.json` as single JSON array files with identical record content to the JSONL exports.

#### Scenario: Simple JSON loader

- **WHEN** a consumer parses `countries.json` without line-delimited handling
- **THEN** they receive a JSON array of country objects matching `countries.jsonl` rows

### Requirement: Frictionless datapackage descriptor

Each release build SHALL emit `data/datasets/datapackage.json` conforming to the Frictionless Data Package specification, listing all published resources with name, path, format, and license metadata.

#### Scenario: Datapackage lists CSV resources

- **WHEN** a consumer opens `datapackage.json` after this change
- **THEN** it includes entries for countries and intblocks CSV (and lite) resources with schema references or field descriptions
