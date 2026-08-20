# Internacia Datasets

[![Validate datasets](https://github.com/datenoio/internacia-db/actions/workflows/validate.yml/badge.svg)](https://github.com/datenoio/internacia-db/actions/workflows/validate.yml)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.21452328.svg)](https://doi.org/10.5281/zenodo.21452328)

Comprehensive reference datasets of countries, intergovernmental organizations, and country groups. Source YAML files in `data/countries/`, `data/intblocks/`, and `data/blocktypes/` are validated, enriched, and exported to multiple formats in `data/datasets/`. Internacia is part of the **[Dateno](https://dateno.io)** open-source project and a data source for the Dateno search engine.

## Distribution

- **GitHub Releases** — primary Parquet/JSONL/DuckDB assets on each `v*` tag
- **Zenodo** — concept DOI [10.5281/zenodo.21452328](https://doi.org/10.5281/zenodo.21452328)
- **Hugging Face Datasets** — optional mirror `datenoio/internacia` when `HF_TOKEN` is set ([docs/release-distribution.md](docs/release-distribution.md))

## Features

- **Multi-format export**: JSONL, YAML, Parquet, and DuckDB (Zstandard compression, level 22)
- **Countries quality pipeline**: schema validation, completeness gates, entity status policy, and field-level provenance
- **Intblocks quality pipeline**: schema validation, blocktype taxonomy checks, duplicate detection, and completeness gates
- **Profile enrichment**: population, area, gini, timezones, and native names from World Bank, Wikidata, and IANA tzdata
- **Data-quality analyzer**: 50+ rules (referential integrity, temporal consistency, geographic plausibility, provenance depth, naming) reported under `dataquality/`; runs in CI and fails on CRITICAL/IMPORTANT findings
- **Build metadata**: `countries.manifest.json`, `intblocks.manifest.json`, and `blocktypes.manifest.json` with version, commit, row count, and schema hash — all sharing a single frozen build identity
- **Artifact consistency guard**: `check_generated_artifacts.py` verifies committed exports agree across formats and match YAML sources (runs in CI and release)
- **CI validation**: pull-request checks, tests, and lint via `.github/workflows/validate.yml`; weekly link validation; tagged releases with dataset assets
- **CLI tools**: Typer-based scripts with tqdm progress bars; console entry points `internacia-build`, `internacia-analyze-quality`, `internacia-validate-countries`, `internacia-validate-intblocks`

## AI agents and LLMs

- [AGENTS.md](AGENTS.md) — root routing hub (all platforms)
- [AGENTS.zh.md](AGENTS.zh.md) · [llms.zh.txt](llms.zh.txt) — 中文指南（Kimi K3、GLM-5.2、通义灵码）
- [llms.txt](llms.txt) — compact index (datasets, join keys, gotchas)
- [llms-full.txt](llms-full.txt) — extended index for crawlers
- [docs/agents/query.md](docs/agents/query.md) — query and join workflow
- [docs/agents/zh/query.md](docs/agents/zh/query.md) — 中文查询工作流
- [docs/agents/contribute.md](docs/agents/contribute.md) — YAML editing workflow
- [docs/query-examples.zh.md](docs/query-examples.zh.md) — 已验证中文 DuckDB 示例
- [docs/ai-consumers.md](docs/ai-consumers.md) — consumption contract, scope boundaries
- [docs/getting-started.md](docs/getting-started.md) — spreadsheet / DuckDB quick start
- [docs/when-to-use-internacia.md](docs/when-to-use-internacia.md) — task-based routing guide for choosing Internacia
- [docs/data-dictionary.md](docs/data-dictionary.md) — generated field reference
- [docs/architecture.md](docs/architecture.md) — pipeline diagram
- [docs/versioning-policy.md](docs/versioning-policy.md) — dataset SemVer and API posture
- [docs/agents/add-intblock-example.md](docs/agents/add-intblock-example.md) — worked add-intblock walkthrough
- [docs/intblock-inclusion-policy.md](docs/intblock-inclusion-policy.md) — scope_category taxonomy
- [docs/entity-classification-policy.md](docs/entity-classification-policy.md) — TW / PS / XK / EH edge cases
- [docs/country-code-policy.md](docs/country-code-policy.md) — ISO vs user-assigned codes
- [docs/query-examples.md](docs/query-examples.md) — verified DuckDB and Pandas query cookbook (UN membership, borders, org density, former members, hierarchy)
- [docs/llm-scenarios.md](docs/llm-scenarios.md) — intent-based copy/paste scenarios for LLM code generation
- [docs/query-examples-polars.md](docs/query-examples-polars.md) — verified Polars / Parquet query cookbook
- [docs/query-examples-r.md](docs/query-examples-r.md) — verified R / dplyr / Parquet query cookbook
- [docs/query-examples-observable.md](docs/query-examples-observable.md) — Observable Framework / Plot cookbook (DuckDB-Wasm)
- [CLAUDE.md](CLAUDE.md) / [.github/copilot-instructions.md](.github/copilot-instructions.md) — Claude / Copilot shims
- [.kimi/AGENTS.md](.kimi/AGENTS.md) — Kimi Code
- [.lingma/rules/](.lingma/rules/) — 通义灵码 Project Rules
- [.cursor/skills/](.cursor/skills/) — thin Cursor wrappers pointing to `docs/agents/`

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
| `countries.jsonl` | Countries (plain JSONL) |
| `countries.json.zst` | Countries (JSON array, zstd) |
| `countries.csv.zst` | Countries (flattened CSV, zstd) |
| `countries-lite.csv.zst` / `countries-lite.parquet` | Countries lite (identifier + classification columns only) |
| `countries.jsonl.zst` | Countries (JSONL, zstd) |
| `countries.yaml.zst` | Countries (YAML, zstd) |
| `countries.parquet` | Countries (Parquet, zstd) |
| `countries.manifest.json` | Build metadata (version, commit, row count, schema hash, data license) |
| `countries.meta.json` | Version metadata sidecar for Parquet consumers |
| `intblocks.manifest.json` | Build metadata (version, commit, row count, schema hash, data license) |
| `intblocks.meta.json` | Version metadata sidecar for Parquet consumers |
| `intblocks.jsonl` | International blocks (plain JSONL) |
| `intblocks.json.zst` | International blocks (JSON array, zstd) |
| `intblocks.csv.zst` | International blocks (flattened CSV, zstd) |
| `intblocks-lite.csv.zst` / `intblocks-lite.parquet` | Intblocks lite (identifier + scope columns only) |
| `intblocks.jsonl.zst` | International blocks (JSONL, zstd) |
| `intblocks.yaml.zst` | International blocks (YAML, zstd) |
| `intblocks.parquet` | International blocks (Parquet, zstd) |
| `intblocks_aliases.json` | Retired/renamed intblock id → current id map |
| `countries_aliases.json` | Retired/renamed country code → current code map |
| `attribute_intblock_migrations.json` | Retired attribute-partition intblock → country field predicate |
| `datapackage.json` | Frictionless Data Package descriptor listing all resources |
| `intblocks_aliases.parquet` | Alias map (Parquet, zstd) |
| `blocktypes.manifest.json` | Build metadata (version, commit, row count, schema hash, data license) |
| `blocktypes.yaml` | Block types (plain YAML copy of source, regenerated on build) |
| `blocktypes.jsonl` | Block types (plain JSONL) |
| `blocktypes.jsonl.zst` | Block types (JSONL, zstd) |
| `blocktypes.yaml.zst` | Block types (YAML, zstd) |
| `blocktypes.parquet` | Block types (Parquet, zstd) |
| `blocktypes.meta.json` | Version metadata sidecar for Parquet consumers |
| `memberships.parquet` | Flattened country↔intblock membership edges (`intblock_id`, `country_code`, `include_type`, `status`, `joined`, `left`) |
| `memberships.csv.zst` | Membership edge table (CSV, zstd) |
| `memberships.manifest.json` | Build metadata (version, commit, row count, schema hash, data license) |
| `memberships.meta.json` | Version metadata sidecar for Parquet consumers |
| `internacia.duckdb` | DuckDB database (`countries`, `intblocks`, `blocktypes`, `memberships`, and `_meta` tables) |

Current row counts: **256** countries, **1037** intblocks, **78** blocktypes.

Format policy: JSONL is shipped both plain and zstd-compressed; YAML exports are
zstd-only (the plain `blocktypes.yaml` is a regenerated copy of the small source
taxonomy, kept for convenience). Flattened CSV and JSON-array exports are
**zstd-only** (`.csv.zst`, `.json.zst`). Use Parquet or DuckDB for analytics.

## Validation and quality

The builder runs both `validate_countries.py` and `validate_intblocks.py` before export. Validation covers:

- JSON Schema conformance (`data/schemas/countries.schema.json`, `data/schemas/intblocks.schema.json`)
- ISO identifier formats and duplicate detection (country codes and intblock ids)
- Completeness thresholds (`data/schemas/countries_completeness.yaml`, `data/schemas/intblocks_completeness.yaml`)
- Entity status policy (`entity_type`, `code_status`)
- Blocktype taxonomy and `partof` reference checks for intblocks
- Intblock cross-references (country `includes` resolve to country sources; `includes[].status` values come from `data/schemas/includes_status.yaml`)
- Referential integrity (borders, `predecessor`/`successor`/`suborganizations`, headquarters countries, duplicate `wikidata_id`) plus temporal, geographic-plausibility, provenance depth, and naming rules — shared between the validators and the quality analyzer (`internacia_builder/validate/*_rules.py`)

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
python3 scripts/enrich_intblocks.py backfill-structural   # headquarters + founded

# Generate the data-quality report (dataquality/ — by rule, priority, country)
python3 scripts/builder.py analyze-quality

# Apply entity status annotations
python3 scripts/annotate_entity_status.py

# Compare manifests to main branch baseline
python3 scripts/diff_countries_baseline.py

# Verify committed exports match sources and each other; check doc links
python3 scripts/check_generated_artifacts.py
python3 scripts/check_markdown_links.py

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
- **Kosovo**: code is `XK` / `XKX` (not `KV` / `KSV`); remap via `countries_aliases.json`.
- **Attribute partitions**: traffic hand, DVD region, scripts, etc. are country fields — not intblocks; see `attribute_intblock_migrations.json`.
- **Build metadata**: compare `countries.manifest.json` `schema_hash` when upgrading downstream pipelines.

**Pandas example** (structured population — `.struct` requires the Arrow dtype backend):

```python
import pandas as pd

df = pd.read_parquet("data/datasets/countries.parquet", dtype_backend="pyarrow")
pop = df["population"].struct.field("value")
```

**Polars example** (same struct field; structs load natively from Parquet):

```python
import polars as pl

countries = pl.read_parquet("data/datasets/countries.parquet")
pop = countries.select(pl.col("population").struct.field("value").alias("pop"))
```

Full Polars recipes: [docs/query-examples-polars.md](docs/query-examples-polars.md).

**R / dplyr example** (same struct field via Arrow):

```r
library(arrow)
library(dplyr)

countries <- read_parquet("data/datasets/countries.parquet")
pop <- countries |>
  transmute(code, name, pop = population$value) |>
  collect()
```

Full R recipes: [docs/query-examples-r.md](docs/query-examples-r.md).
Observable / Plot recipes: [docs/query-examples-observable.md](docs/query-examples-observable.md).

**DuckDB example** (nested intblock multilingual names):

```python
import duckdb

con = duckdb.connect("data/datasets/internacia.duckdb")
con.execute("""
    SELECT id, name, t.name AS english_name
    FROM intblocks, UNNEST(other_names) AS t
    WHERE t.id = 'en'
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

Attribute-partition intblocks (traffic hand, DVD region, scripts, etc.) were retired in favor of
country fields. Remap those ids with `attribute_intblock_migrations.json` (e.g. `RHTRAFFIC` →
`car_side = 'right'`), not `intblocks_aliases.json`.

## Countries schema

256 country and territory records. Key fields:

| Field | Type | Description |
|-------|------|-------------|
| `code` | String | ISO 3166-1 alpha-2 code (e.g. `US`) |
| `entity_type` | String | `sovereign_state`, `dependent_territory`, `historical_entity`, etc. |
| `code_status` | String | `official_iso3166_1`, `user_assigned`, `obsolete`, `exceptionally_reserved` |
| `recognition_status` | Struct | Optional recognition/dispute metadata |
| `parent_entity` | Struct | Parent state `{code, name}` for dependent territories |
| `name` | String | Common name |
| `iso3code` | String | ISO 3166-1 alpha-3 code |
| `capital_city` | Struct | `{name, lng, lat}` |
| `centroid` | Struct | Geographic centroid `{lat, lng}` |
| `region` | Struct | World Bank region `{id, value}` |
| `adminregion` | Struct | World Bank admin region `{id, value}` |
| `incomeLevel` | Struct | World Bank income level `{id, value}` |
| `lendingType` | Struct | World Bank lending type `{id, value}` |
| `numeric_code` | String | ISO 3166-1 numeric code |
| `wikidata_id` | String | Wikidata item ID |
| `official_name` | String | Official full name |
| `languages` | List[Struct] | `{code, name, official}` |
| `currencies` | List[Struct] | `{code, name, symbol}` |
| `un_member` | Boolean | UN member (**193** `true`; aligns with the `UN` intblock roster) |
| `un_status` | String | `member`, `observer` (PS, VA), or `non_member` |
| `independent` | Boolean | Independent state (non-UN independents: `VA` only) |
| `subregion` | String | UN subregion |
| `continents` | List[String] | Continents |
| `borders` | List[String] | Land borders as ISO **alpha-3** codes |
| `landlocked` | Boolean | Landlocked |
| `tld` | String | Top-level domain |
| `calling_codes` | List[String] | Telephone codes |
| `flag_emoji` | String | Flag emoji |
| `car_side` | String | Driving side (`left` / `right`) |
| `writing_directions` | List | Writing direction ids (`ltr`, `rtl`, `ttb`) |
| `writing_systems` | List | Script ids (e.g. `latin`, `arabic`) |
| `dvd_region` | Integer | DVD region 1–6 when assigned |
| `broadcast_systems` | List | TV/broadcast standard ids (e.g. `atsc`, `dvbt`) |
| `legal_systems` | List | Legal tradition ids (e.g. `common_law`) |
| `rail_gauges` | List | Rail gauge ids with optional `gauge_mm` |
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

Seven non-standard codes are retained with explicit status (see [docs/country-code-policy.md](docs/country-code-policy.md)): `AN` (obsolete, Netherlands Antilles), `JG` (user-assigned grouping, Channel Islands), `XK` (user-assigned, Kosovo; former `KV` in `countries_aliases.json`), `XA` (user-assigned, Abkhazia), `XS` (user-assigned, South Ossetia), `XT` (user-assigned, Transnistria), `XN` (user-assigned, Nagorno-Karabakh). All carry explicit `un_member`, `un_status`, `independent`, and `landlocked` values.

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

The table above lists exported columns. Source YAML may carry additional curation fields that are
validated but not exported (`membership_applicability`, `founding_members`, `suborganizations`,
`secretariat`, `last_verified`, `previous_names`, `official_documents`, `social_media`,
`recognition_status`); see `data/schemas/intblocks.schema.json` for the full source contract.
Valid `includes[].status` values are cataloged in `data/schemas/includes_status.yaml`.

## Data sources

**YAML sources**

- `data/countries/*.yaml` — 256 country/territory records
- `data/intblocks/<category>/*.yaml` — international block records across domain categories (`intorg`, `aviation`, `agriculture`, `health`, `climate`, etc.)

**External enrichment**

- [World Bank](https://data.worldbank.org/) — population, area, gini, income classifications
- [Wikidata](https://www.wikidata.org/) — entity linking, native names, fallbacks
- [IANA tzdata](https://data.iana.org/time-zones/) — timezone mapping (`scripts/data/zone1970.tab`)

## Scripts

| Script | Purpose |
|--------|---------|
| `internacia_builder/` | Installable package (`pip install -e .`): build/export, quality analyzer, validation rule modules, shared paths/HTTP helpers |
| `scripts/builder.py` | Shim → `internacia_builder.build` / `internacia_builder.quality` (`build`, `info`, `analyze-quality`) |
| `scripts/validate_countries.py` | Shim → `internacia_builder.validate.countries` |
| `scripts/validate_intblocks.py` | Shim → `internacia_builder.validate.intblocks` |
| `scripts/validate_links.py` | Intblock URL and Wikidata validation (run weekly in CI) |
| `scripts/enrich_countries.py` | Enrich country profiles; `backfill-provenance` subcommand |
| `scripts/enrich_intblocks.py` | Enrich intblocks from Wikidata (wikidata_id, descriptions, multilingual names); `backfill-structural` fills headquarters and founded dates |
| `scripts/annotate_entity_status.py` | Set `entity_type` and `code_status` |
| `scripts/diff_countries_baseline.py` | Manifest diff vs git baseline (countries, intblocks, blocktypes) |
| `scripts/check_generated_artifacts.py` | Cross-format primary-key parity, source/export parity, build-identity guard |
| `scripts/check_markdown_links.py` | Internal Markdown link checker |
| `scripts/check_doc_counts.py` | Consumer-facing docs vs manifest `row_count` |
| `scripts/generate_data_dictionary.py` | Regenerate `docs/data-dictionary.md` from JSON Schemas |

One-off migration scripts currently live under `scripts/` (for example
`apply_manus_roadmap.py`) and are not part of the maintained pipeline. `dev/scripts/`
is the intended archive (see `dev/scripts/README.md`). Research notes: `dev/research/`.

## Releases

Tagged releases (`vX.Y.Z`) automatically rebuild all formats and attach them as GitHub Release assets (`.github/workflows/release.yml`). Consumers can either clone the repository (datasets are committed under `data/datasets/`) or download versioned assets from the Releases page.

## Notes

- All text files use UTF-8 encoding; generated outputs overwrite existing files.
- Decompress zstd files: `zstd -d data/datasets/countries.jsonl.zst`
- Gap analysis research: `dev/research/countries_gaps_manus_20260528.md`
- `data/_legacy/` contains pre-1.0 Airtable JSON exports kept for reference only; nothing in the pipeline consumes them.

## License

Internacia is part of the [Dateno](https://dateno.io) open-source project.

- **Code** (`scripts/`, `internacia_builder/`, `tests/`, build tooling, and `website/`) — MIT, see [LICENSE](LICENSE).
- **Data and documentation** (curated sources under `data/`, generated artifacts in `data/datasets/`, and docs under `docs/`, README, and related guides) —
  Creative Commons Attribution 4.0 (CC BY 4.0), see [DATA_LICENSE](DATA_LICENSE).

Upstream sources (World Bank, Wikidata, IANA tzdata) and citation guidance are documented in
[ATTRIBUTION.md](ATTRIBUTION.md). Machine-readable citation metadata is in [CITATION.cff](CITATION.cff);
concept DOI [10.5281/zenodo.21452328](https://doi.org/10.5281/zenodo.21452328). The data license
SPDX identifier is recorded in each build manifest and in the `_meta`/`*.meta.json` metadata.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for the YAML authoring guide, validation workflow, and PR checklist.

## Related projects

- [internacia-api](https://github.com/datenoio/internacia-api) — REST API (**self-host only**; no public hosted instance)
- [internacia-python](https://github.com/datenoio/internacia-python) — Python SDK

## Roadmap

- [x] Python SDK — [internacia-python](https://github.com/datenoio/internacia-python)
- [x] REST API — [internacia-api](https://github.com/datenoio/internacia-api) (self-host; not a hosted service)
