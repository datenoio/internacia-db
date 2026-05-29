# Internacia Datasets

Comprehensive reference datasets of countries, intergovernmental organizations, and country groups. Source YAML files in `data/countries/` and `data/intblocks/` are validated, enriched, and exported to multiple formats in `data/datasets/`. The project serves as a data source for the **Dateno** search engine.

## Features

- **Multi-format export**: JSONL, YAML, Parquet, and DuckDB (Zstandard compression, level 22)
- **Countries quality pipeline**: schema validation, completeness gates, entity status policy, and field-level provenance
- **Profile enrichment**: population, area, gini, timezones, and native names from World Bank, Wikidata, and IANA tzdata
- **Build metadata**: `countries.manifest.json` with version, commit, row count, and schema hash
- **CI validation**: pull-request checks via `.github/workflows/validate.yml`
- **CLI tools**: Typer-based scripts with tqdm progress bars

## Installation

```bash
pip install -r requirements.txt
```

## Quick start

```bash
# Inspect data sources
python3 scripts/builder.py info

# Validate country YAML (no build)
python3 scripts/validate_countries.py

# Build all datasets
python3 scripts/builder.py build

# Build specific formats only
python3 scripts/builder.py build --formats parquet,duckdb
```

## Output files

Each build writes to `data/datasets/`:

| File | Description |
|------|-------------|
| `countries.jsonl.zst` | Countries (JSONL, zstd) |
| `countries.yaml.zst` | Countries (YAML, zstd) |
| `countries.parquet` | Countries (Parquet, zstd) |
| `countries.manifest.json` | Build metadata (version, commit, row count, schema hash) |
| `intblocks.jsonl.zst` | International blocks (JSONL, zstd) |
| `intblocks.yaml.zst` | International blocks (YAML, zstd) |
| `intblocks.parquet` | International blocks (Parquet, zstd) |
| `blocktypes.jsonl.zst` | Block types (JSONL, zstd) |
| `blocktypes.yaml.zst` | Block types (YAML, zstd) |
| `blocktypes.parquet` | Block types (Parquet, zstd) |
| `internacia.duckdb` | DuckDB database (`countries`, `intblocks`, `blocktypes` tables) |

Current row counts: **252** countries, **1065** intblocks, **85** blocktypes.

## Validation and quality

The builder runs `validate_countries.py` before export. Validation covers:

- JSON Schema conformance (`data/schemas/countries.schema.json`)
- ISO identifier formats and duplicate detection
- Completeness thresholds (`data/schemas/countries_completeness.yaml`)
- Entity status policy (`entity_type`, `code_status`)
- Intblock cross-references (country `includes` resolve to country sources)

```bash
# Full validation with JSON report
python3 scripts/validate_countries.py --report completeness-report.json

# Enrich profile fields from external sources
python3 scripts/enrich_countries.py
python3 scripts/enrich_countries.py backfill-provenance

# Apply entity status annotations
python3 scripts/annotate_entity_status.py

# Audit intblock include name aliases (warn-only)
python3 scripts/report_country_include_names.py

# Compare manifest to main branch baseline
python3 scripts/diff_countries_baseline.py
```

Country code policy (ISO vs user-assigned, filtering examples): [docs/country-code-policy.md](docs/country-code-policy.md)

## Consumer migration

Breaking and semantic changes in the latest countries schema (see [CHANGELOG.md](CHANGELOG.md)):

- **Population / area / gini**: structured as `{value, year, source, source_id}` — use `.value` for the numeric field.
- **Borders**: land neighbors as ISO **alpha-3** codes (e.g. `CAN`, `MEX`), not alpha-2.
- **Entity filter**: `code_status == 'official_iso3166_1'` returns **249** current ISO-style records.
- **Build metadata**: compare `countries.manifest.json` `schema_hash` when upgrading downstream pipelines.

**Pandas example** (structured population):

```python
import pandas as pd

df = pd.read_parquet("data/datasets/countries.parquet")
pop = df["population"].struct.field("value")
```

**DuckDB example** (nested intblock translations):

```python
import duckdb

con = duckdb.connect("data/datasets/internacia.duckdb")
con.execute("""
    SELECT id, name, t.name AS english_name
    FROM intblocks, UNNEST(translations) AS t
    WHERE t.lang = 'en'
    LIMIT 5
""").fetchall()
```

## Countries schema

252 country and territory records. Key fields:

| Field | Type | Description |
|-------|------|-------------|
| `code` | String | ISO 3166-1 alpha-2 code (e.g. `US`) |
| `entity_type` | String | `sovereign_state`, `dependent_territory`, `historical_entity`, etc. |
| `code_status` | String | `official_iso3166_1`, `user_assigned`, `obsolete` |
| `recognition_status` | Struct | Optional recognition/dispute metadata |
| `name` | String | Common name |
| `iso3code` | String | ISO 3166-1 alpha-3 code |
| `capital_city` | Struct | `{name, lng, lat}` |
| `region` | Struct | World Bank region `{id, value}` |
| `adminregion` | Struct | World Bank admin region `{id, value}` |
| `incomeLevel` | Struct | World Bank income level `{id, value}` |
| `lendingType` | Struct | World Bank lending type `{id, value}` |
| `numeric_code` | String | ISO 3166-1 numeric code |
| `wikidata_id` | String | Wikidata item ID |
| `official_name` | String | Official full name |
| `languages` | List[Struct] | `{code, name, official}` |
| `currencies` | List[Struct] | `{code, name, symbol}` |
| `un_member` | Boolean | UN member |
| `independent` | Boolean | Independent state |
| `subregion` | String | UN subregion |
| `continents` | List[String] | Continents |
| `borders` | List[String] | Land borders as ISO **alpha-3** codes |
| `landlocked` | Boolean | Landlocked |
| `tld` | String | Top-level domain |
| `calling_codes` | List[String] | Telephone codes |
| `flag_emoji` | String | Flag emoji |
| `car_side` | String | Driving side |
| `start_of_week` | String | Start of week |
| `demonyms` | Struct | `{female, male}` |
| `m49_code` | String | UN M49 code |
| `population` | Struct | `{value, year, source, source_id}` |
| `area` | Struct | Land area sq km `{value, year, source, source_id}` |
| `gini` | Struct | Gini index `{value, year, source, source_id}` |
| `timezones` | List[String] | IANA timezone identifiers |
| `timezone_status` | String | `not_applicable` when no zones apply |
| `native_names` | Map | Lang code → `{official, common}` |
| `other_names` | List[Struct] | Translations `{id, name}` |
| `common_names` | List[String] | Aliases and common names |
| `provenance` | List[Struct] | Field sourcing `{field, source, retrieved_at, url, license}` |

Non-standard codes retained with explicit status: `AN` (obsolete), `JG` (user-assigned grouping), `KV` (user-assigned, disputed).

## International blocks schema

| Field | Type | Description |
|-------|------|-------------|
| `id` | String | Unique identifier |
| `blocktype` | List[String] | Block types |
| `status` | String | Current status |
| `name` | String | Name |
| `languages` | List[String] | Official languages |
| `links` | List[Struct] | `{url, type}` |
| `other_names` | List[Struct] | `{id, name}` translations |
| `founded` | String | Foundation date |
| `geographic_scope` | String | Scope |
| `regions` | List[String] | Regions covered |
| `includes` | List[Struct] | Members `{id, name, type, status, joined, role, note}` — **`id` is authoritative**; `name` is a source label |
| `membership_count` | Integer | Member count |
| `wikidata_id` | String | Wikidata item ID |
| `legal_status` | String | Legal status |
| `description` | String | Description |
| `tags` | List[String] | Tags |
| `topics` | List[Struct] | `{key, name}` |
| `headquarters` | Struct | `{city, country, coordinates}` |
| `acronyms` | List[Struct] | `{lang, value}` |
| `partof` | List[String] | Parent organizations |
| `dissolved` | String | Dissolution date |
| `predecessor` | String | Predecessor |
| `successor` | String | Successor |

## Data sources

**YAML sources**

- `data/countries/*.yaml` — 252 country/territory records
- `data/intblocks/**/*.yaml` — 1065 international block records

**External enrichment**

- [World Bank](https://data.worldbank.org/) — population, area, gini, income classifications
- [Wikidata](https://www.wikidata.org/) — entity linking, native names, fallbacks
- [IANA tzdata](https://data.iana.org/time-zones/) — timezone mapping (`scripts/data/zone1970.tab`)

## Scripts

| Script | Purpose |
|--------|---------|
| `scripts/builder.py` | Validate and export datasets |
| `scripts/validate_countries.py` | Country schema, completeness, and cross-dataset checks |
| `scripts/validate_links.py` | Intblock URL and Wikidata validation |
| `scripts/enrich_countries.py` | Enrich country profiles; `backfill-provenance` subcommand |
| `scripts/annotate_entity_status.py` | Set `entity_type` and `code_status` |
| `scripts/report_country_include_names.py` | Intblock include name alias audit |
| `scripts/diff_countries_baseline.py` | Manifest diff vs git baseline |

## Notes

- All text files use UTF-8 encoding; generated outputs overwrite existing files.
- Decompress zstd files: `zstd -d data/datasets/countries.jsonl.zst`
- Gap analysis research: `dev/research/countries_gaps_,manus_20260528.md`

## Related projects

- [internacia-api](../internacia-api) — REST API
- [internacia-python](../internacia-python) — Python SDK

## Roadmap

- [x] Python SDK — [internacia-python](../internacia-python)
- [x] REST API — [internacia-api](../internacia-api)
