# Internacia Datasets

[![Validate datasets](https://github.com/commondataio/internacia-db/actions/workflows/validate.yml/badge.svg)](https://github.com/commondataio/internacia-db/actions/workflows/validate.yml)

Comprehensive reference datasets of countries, intergovernmental organizations, and country groups. Source YAML files in `data/countries/`, `data/intblocks/`, and `data/blocktypes/` are validated, enriched, and exported to multiple formats in `data/datasets/`. The project serves as a data source for the **Dateno** search engine.

## Features

- **Multi-format export**: JSONL, YAML, Parquet, and DuckDB (Zstandard compression, level 22)
- **Countries quality pipeline**: schema validation, completeness gates, entity status policy, and field-level provenance
- **Intblocks quality pipeline**: schema validation, blocktype taxonomy checks, duplicate detection, and completeness gates
- **Profile enrichment**: population, area, gini, timezones, and native names from World Bank, Wikidata, and IANA tzdata
- **Build metadata**: `countries.manifest.json` and `intblocks.manifest.json` with version, commit, row count, and schema hash
- **CI validation**: pull-request checks, tests, and lint via `.github/workflows/validate.yml`; weekly link validation; tagged releases with dataset assets
- **CLI tools**: Typer-based scripts with tqdm progress bars

## AI agents and LLMs

- [llms.txt](llms.txt) — compact index (datasets, join keys, gotchas)
- [docs/ai-consumers.md](docs/ai-consumers.md) — consumption contract, query recipes, scope boundaries
- [docs/query-examples.md](docs/query-examples.md) — verified DuckDB and Pandas query cookbook
- [.cursor/skills/internacia-contribute/SKILL.md](.cursor/skills/internacia-contribute/SKILL.md) — maintainer workflow for editing YAML

## Installation

Requires Python 3.11+ (CI runs 3.11). Dependencies are pinned for reproducible builds.

```bash
pip install -r requirements.txt        # runtime
pip install -r requirements-dev.txt    # development (adds pytest, ruff, pre-commit)
```

## Quick start

```bash
# Inspect data sources
python3 scripts/builder.py info

# Validate country YAML (no build)
python3 scripts/validate_countries.py
# or: internacia-validate-countries   (after pip install -e .)

# Validate intblock YAML (no build)
python3 scripts/validate_intblocks.py
# or: internacia-validate-intblocks

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
| `countries.manifest.json` | Build metadata (version, commit, row count, schema hash, data license) |
| `countries.meta.json` | Version metadata sidecar for Parquet consumers |
| `intblocks.manifest.json` | Build metadata (version, commit, row count, schema hash, data license) |
| `intblocks.meta.json` | Version metadata sidecar for Parquet consumers |
| `intblocks.jsonl.zst` | International blocks (JSONL, zstd) |
| `intblocks.yaml.zst` | International blocks (YAML, zstd) |
| `intblocks.parquet` | International blocks (Parquet, zstd) |
| `intblocks_aliases.json` | Retired/renamed intblock id → current id map |
| `intblocks_aliases.parquet` | Alias map (Parquet, zstd) |
| `blocktypes.yaml` | Block types (plain YAML copy of source, regenerated on build) |
| `blocktypes.jsonl.zst` | Block types (JSONL, zstd) |
| `blocktypes.yaml.zst` | Block types (YAML, zstd) |
| `blocktypes.parquet` | Block types (Parquet, zstd) |
| `blocktypes.meta.json` | Version metadata sidecar for Parquet consumers |
| `internacia.duckdb` | DuckDB database (`countries`, `intblocks`, `blocktypes`, and `_meta` tables) |

Current row counts: **256** countries, **1070** intblocks, **86** blocktypes.

## Validation and quality

The builder runs `validate_countries.py` before export. Validation covers:

- JSON Schema conformance (`data/schemas/countries.schema.json`, `data/schemas/intblocks.schema.json`)
- ISO identifier formats and duplicate detection (country codes and intblock ids)
- Completeness thresholds (`data/schemas/countries_completeness.yaml`, `data/schemas/intblocks_completeness.yaml`)
- Entity status policy (`entity_type`, `code_status`)
- Blocktype taxonomy and `partof` reference checks for intblocks
- Intblock cross-references (country `includes` resolve to country sources)

```bash
# Full validation with JSON reports
python3 scripts/validate_countries.py --report completeness-report.json
python3 scripts/validate_intblocks.py --report intblocks-report.json

# Enrich profile fields from external sources
python3 scripts/enrich_countries.py
python3 scripts/enrich_countries.py backfill-provenance

# Enrich intblocks from Wikidata (wikidata_id, descriptions, multilingual names)
python3 scripts/enrich_intblocks.py --dry-run
python3 scripts/enrich_intblocks.py

# Apply entity status annotations
python3 scripts/annotate_entity_status.py

# Audit intblock include name aliases (warn-only)
python3 scripts/report_country_include_names.py

# Compare manifests to main branch baseline
python3 scripts/diff_countries_baseline.py

# Run tests and lint
pytest tests/
ruff check internacia_builder/ scripts/ tests/
```

Country code policy (ISO vs user-assigned, filtering examples): [docs/country-code-policy.md](docs/country-code-policy.md)

## Consumer migration

Breaking and semantic changes in the latest countries schema (see [CHANGELOG.md](CHANGELOG.md)):

- **Population / area / gini**: structured as `{value, year, source, source_id}` — use `.value` for the numeric field. `year` is **null** when the source year is unknown (never `0`).
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

## Versioning and identifier stability

Datasets are **self-describing**. The DuckDB file carries a `_meta` table and each Parquet file has a
`<dataset>.meta.json` sidecar, both mirroring the manifest fields (`version`, `build_date`,
`git_commit`, `row_count`, `schema_hash`, `data_license`):

```python
import duckdb

con = duckdb.connect("data/datasets/internacia.duckdb")
con.execute("SELECT dataset, version, schema_hash FROM _meta").fetchall()
```

**Identifier stability.** Country `code` and intblock `id` are stable join keys. When an intblock id is
renamed, merged, or its acronym is reassigned to a different entity, the old id is recorded in
`intblocks_aliases.json` (and `.parquet`) so downstream joins can remap:

```python
import json

aliases = {a["alias"]: a["target"] for a in json.load(open("data/datasets/intblocks_aliases.json"))}
current_id = aliases.get("ASF", "ASF")  # -> "FSA"
```

A `reason` of `disambiguated` means the old id still exists but now refers to a **different** entity
(e.g. `ASF` is now the African Standby Force; the African Solidarity Fund moved to `FSA`).

## Countries schema

256 country and territory records. Key fields:

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

- `data/countries/*.yaml` — 256 country/territory records
- `data/intblocks/<category>/*.yaml` — 1070 international block records across 60+ domain categories (`intorg`, `aviation`, `agriculture`, `health`, `climate`, etc.)

**External enrichment**

- [World Bank](https://data.worldbank.org/) — population, area, gini, income classifications
- [Wikidata](https://www.wikidata.org/) — entity linking, native names, fallbacks
- [IANA tzdata](https://data.iana.org/time-zones/) — timezone mapping (`scripts/data/zone1970.tab`)

## Scripts

| Script | Purpose |
|--------|---------|
| `internacia_builder/` | Installable package (`pip install -e .`): validation modules, shared paths/HTTP helpers |
| `scripts/builder.py` | Validate and export datasets |
| `scripts/validate_countries.py` | Shim → `internacia_builder.validate.countries` |
| `scripts/validate_intblocks.py` | Shim → `internacia_builder.validate.intblocks` |
| `scripts/validate_links.py` | Intblock URL and Wikidata validation (run weekly in CI) |
| `scripts/enrich_countries.py` | Enrich country profiles; `backfill-provenance` subcommand |
| `scripts/enrich_intblocks.py` | Enrich intblocks from Wikidata (wikidata_id, descriptions, multilingual names) |
| `scripts/annotate_entity_status.py` | Set `entity_type` and `code_status` |
| `scripts/report_country_include_names.py` | Intblock include name alias audit |
| `scripts/diff_countries_baseline.py` | Manifest diff vs git baseline (countries + intblocks) |

One-off migration scripts live in `dev/scripts/` and are not part of the maintained pipeline.

## Releases

Tagged releases (`vX.Y.Z`) automatically rebuild all formats and attach them as GitHub Release assets (`.github/workflows/release.yml`). Consumers can either clone the repository (datasets are committed under `data/datasets/`) or download versioned assets from the Releases page.

## Notes

- All text files use UTF-8 encoding; generated outputs overwrite existing files.
- Decompress zstd files: `zstd -d data/datasets/countries.jsonl.zst`
- Gap analysis research: `dev/research/countries_gaps_manus_20260528.md`
- `data/_legacy/` contains pre-1.0 Airtable JSON exports kept for reference only; nothing in the pipeline consumes them.

## License

- **Code** (everything under `scripts/`, `tests/`, and build tooling) — MIT, see [LICENSE](LICENSE).
- **Data** (curated sources under `data/` and generated artifacts in `data/datasets/`) —
  Creative Commons Attribution 4.0 (CC BY 4.0), see [DATA_LICENSE](DATA_LICENSE).

Upstream sources (World Bank, Wikidata, IANA tzdata) and citation guidance are documented in
[ATTRIBUTION.md](ATTRIBUTION.md). The data license SPDX identifier is recorded in each build manifest
and in the `_meta`/`*.meta.json` metadata.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for the YAML authoring guide, validation workflow, and PR checklist.

## Related projects

- [internacia-api](../internacia-api) — REST API
- [internacia-python](../internacia-python) — Python SDK

## Roadmap

- [x] Python SDK — [internacia-python](../internacia-python)
- [x] REST API — [internacia-api](../internacia-api)
