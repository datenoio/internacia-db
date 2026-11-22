# dataset-release Specification

## Purpose
TBD - created by archiving change add-countries-release-governance. Update Purpose after archive.
## Requirements
### Requirement: Countries build manifest

Each successful countries dataset build SHALL write `data/datasets/countries.manifest.json` containing at minimum: `version`, `build_date` (ISO 8601), `git_commit` (short SHA or `unknown`), `row_count`, and `schema_hash`. The `version` field SHALL match the semver tag when built as part of a release workflow.

#### Scenario: Manifest version matches release tag

- **WHEN** a release build runs for tag `v1.3.0`
- **THEN** `countries.manifest.json` `version` equals `1.3.0`

#### Scenario: Manifest written after build

- **WHEN** `scripts/builder.py` completes a countries export
- **THEN** `countries.manifest.json` exists with `row_count` equal to the current country record count

### Requirement: Pull request validation workflow

The repository SHALL run country validation and dataset build on pull requests affecting `data/countries/` or `scripts/`.

#### Scenario: Invalid country fails CI

- **WHEN** a pull request introduces a country YAML with invalid `iso3code`
- **THEN** the CI workflow fails

#### Scenario: Completeness report published

- **WHEN** CI runs on a pull request
- **THEN** a completeness summary artifact or log is available for review

### Requirement: Field-level provenance on country records

Country YAML records MAY include a `provenance` list. When present, each entry SHALL include `field`, `source`, and `retrieved_at` (ISO 8601 date); `url` and `license` are optional.

#### Scenario: Enrichment adds provenance

- **WHEN** `enrich_countries.py` updates `population` from World Bank
- **THEN** the YAML record includes a provenance entry with `field: population` and non-empty `source`

#### Scenario: Records without enrichment omit provenance

- **WHEN** a country file has only hand-curated data
- **THEN** validation passes whether or not `provenance` is present

### Requirement: Changelog migration documentation

Breaking or consumer-affecting schema changes SHALL be documented in `CHANGELOG.md` with migration guidance.

#### Scenario: Population struct documented

- **WHEN** structured `population` ships
- **THEN** CHANGELOG contains an entry describing the Parquet type change and example access pattern

### Requirement: Semver tag release workflow

Pushing a git tag matching `v*` SHALL trigger a workflow that builds all dataset formats and publishes them as GitHub Release assets.

#### Scenario: Tag triggers release build

- **WHEN** a maintainer pushes tag `v1.3.0`
- **THEN** CI runs validation and `builder.py build`, then attaches outputs under `data/datasets/` to the GitHub Release

#### Scenario: Release assets include core formats

- **WHEN** a release workflow completes successfully
- **THEN** release assets include at minimum countries and intblocks Parquet or compressed JSONL outputs and `internacia.duckdb`

### Requirement: Release consumption documentation

README SHALL document how consumers obtain datasets via GitHub Releases versus cloning the repository.

#### Scenario: Download instructions present

- **WHEN** a consumer reads README release section
- **THEN** they find steps to download assets for a specific semver tag

### Requirement: Intblocks build manifest

Each successful intblocks dataset build SHALL write `data/datasets/intblocks.manifest.json` containing at minimum: `version`, `build_date` (ISO 8601), `git_commit` (short SHA or `unknown`), `row_count`, and `schema_hash`.

#### Scenario: Manifest written after build

- **WHEN** `scripts/builder.py` completes an intblocks export
- **THEN** `intblocks.manifest.json` exists with `row_count` matching the intblock source file count

#### Scenario: Schema hash changes on schema migration

- **WHEN** PyArrow schema for intblocks changes
- **THEN** `schema_hash` in the manifest differs from the previous build

### Requirement: Embedded DuckDB metadata table

The DuckDB export SHALL include a `_meta` table containing one row per dataset with at minimum
`dataset`, `version`, `build_date` (ISO 8601), `git_commit`, `row_count`, and `schema_hash`, so the
database file is self-describing without external manifests.

#### Scenario: Metadata table queryable after build

- **WHEN** `scripts/builder.py build --formats duckdb` completes
- **THEN** `SELECT version, schema_hash FROM _meta WHERE dataset = 'countries'` returns the current build version and schema hash

#### Scenario: One row per dataset

- **WHEN** the DuckDB file is built
- **THEN** `_meta` contains a row for each of `countries`, `intblocks`, and `blocktypes`

### Requirement: Parquet sidecar metadata

Each Parquet export SHALL be accompanied by a `data/datasets/<dataset>.meta.json` sidecar containing
the same fields as the dataset manifest, so Parquet-only consumers can determine version without a
separate manifest lookup.

#### Scenario: Sidecar written next to Parquet

- **WHEN** `scripts/builder.py` writes `countries.parquet`
- **THEN** `countries.meta.json` exists in the same directory with matching `version` and `schema_hash`

### Requirement: Identifier alias map artifact

Each successful build SHALL emit an intblock identifier alias artifact at
`data/datasets/intblocks_aliases.json` (and a Parquet equivalent) mapping every retired or renamed
intblock id to its current id. Each entry SHALL include `alias` (retired id), `target` (current id),
`reason` (`renamed`, `merged`, or `disambiguated`), and `since` (the version that introduced the change).

#### Scenario: Alias artifact written on build

- **WHEN** `scripts/builder.py build` completes an intblocks export
- **THEN** `data/datasets/intblocks_aliases.json` exists and contains an entry for each known retired id

#### Scenario: Retired id is resolvable

- **WHEN** a consumer holds the retired id `ASF`
- **THEN** the alias artifact maps `ASF` to its current id `FSA`

### Requirement: Alias artifact in release assets

The alias artifact SHALL be published as a GitHub Release asset by the tag-triggered release workflow.

#### Scenario: Release includes alias artifact

- **WHEN** a release workflow completes for a `v*` tag
- **THEN** release assets include `intblocks_aliases.json`

### Requirement: Committed dataset freshness gate

Pull request CI SHALL rebuild datasets into a temporary location and fail when a committed `data/datasets/` descriptor differs from the fresh build. The committed descriptors SHALL be only the files that change with the schema or with rare source edits: `contract.json`, `README.md`, `intblocks_aliases.json`, `countries_aliases.json`, `attribute_intblock_migrations.json` and `border_status.json`. Build manifests (`*.manifest.json`) and `datapackage.json` SHALL NOT be committed, because they carry per-build checksums, sizes, row counts and build identity that every data change rewrites; the build SHALL still write them and every GitHub Release SHALL still ship them. CI SHALL fail when a generated export or a build-only descriptor is tracked in git. The validate workflow path filters SHALL include `data/datasets/**` so dataset-only commits are validated.

#### Scenario: Stale committed artifact fails CI

- **WHEN** a pull request changes the source schema but does not rebuild `contract.json`
- **THEN** the freshness gate detects the difference and the CI workflow fails

#### Scenario: Data change touches no descriptor

- **WHEN** a pull request adds an intblock record and rebuilds
- **THEN** git shows no change under `data/datasets/` and the freshness gate passes

#### Scenario: Build manifest tracked by mistake

- **WHEN** a pull request adds `data/datasets/intblocks.manifest.json` to git
- **THEN** the freshness gate fails and names the file

#### Scenario: Dataset-only commit is validated

- **WHEN** a commit modifies only files under `data/datasets/`
- **THEN** the validate workflow still runs because the path filter includes `data/datasets/**`

### Requirement: Blocktypes build manifest

Each successful build SHALL write `data/datasets/blocktypes.manifest.json` containing at minimum `version`, `build_date` (ISO 8601), `git_commit`, `row_count`, and `schema_hash`, matching the fields of the countries and intblocks manifests.

#### Scenario: Blocktypes manifest written after build

- **WHEN** `scripts/builder.py build` completes a blocktypes export
- **THEN** `blocktypes.manifest.json` exists with `row_count` equal to the number of defined blocktypes

#### Scenario: Documentation and release assets match emitted manifests

- **WHEN** documentation or the release workflow references `blocktypes.manifest.json`
- **THEN** the referenced file is actually produced by the build

### Requirement: Consumer contract artifact

Each build SHALL write `contract.json` next to the other artifacts. It SHALL list every published table with its columns (name, logical type, nullability), primary key, foreign keys, `schema_hash`, and whether it is present in `internacia.duckdb`; every enum-like column with its allowed values and openness; `contract_version` (`MAJOR.MINOR` of the dataset version); `min_duckdb`; and the DuckDB storage compatibility version. The file SHALL be generated from `internacia_builder/schemas.py` and the source JSON Schemas, committed, and attached to every GitHub Release.

#### Scenario: Contract matches the build

- **WHEN** `scripts/builder.py build` completes
- **THEN** `contract.json` exists and regenerating it from the schemas produces an identical file

#### Scenario: Release contract version

- **WHEN** the release workflow runs for tag `v3.2.0`
- **THEN** `contract.json` has `dataset_version` `3.2.0` and `contract_version` `3.2`

### Requirement: Canonical schema hash

`schema_hash` SHALL be the SHA-256 hex digest of the canonical JSON array `[[name, logical_type, nullable], ...]` of a table's columns in column order, serialized with `separators=(",", ":")`, using the logical type grammar documented in `docs/data-contract.md`. It SHALL NOT depend on the pyarrow or DuckDB version.

#### Scenario: pyarrow upgrade

- **WHEN** the builder's pyarrow version changes and the schemas do not
- **THEN** every `schema_hash` stays the same

#### Scenario: Column added

- **WHEN** a column is added to a table
- **THEN** that table's `schema_hash` changes and the other tables' hashes do not

### Requirement: Bundle checksums

Each bundle SHALL contain `SHA256SUMS` listing the SHA-256 of every other file in the bundle in `sha256sum` format. Each `*.manifest.json` SHALL list `sha256` and `bytes` for the files of its dataset and SHALL include `contract_version`. DuckDB `_meta` SHALL include `contract_version`. Each `datapackage.json` resource SHALL include `bytes`, `hash` (`sha256:<hex>`) and, for tabular resources, a `schema`.

#### Scenario: Corrupted download detected

- **WHEN** a consumer runs `sha256sum -c SHA256SUMS` on a downloaded bundle with a truncated file
- **THEN** the check reports that file as failed

#### Scenario: Release assets covered

- **WHEN** the release workflow publishes a GitHub Release
- **THEN** every attached asset other than `SHA256SUMS` is listed in `SHA256SUMS`, including `migration.vX.Y.Z.json`

### Requirement: Open enum values

Enum-like columns SHALL be declared `"open": true` in `contract.json`. Consumers SHALL accept values they do not recognize. Adding a value to an open enum SHALL be a MINOR change; removing or renaming a value SHALL be a MAJOR change.

#### Scenario: New scope category

- **WHEN** a release adds a new `scope_category` value
- **THEN** the release is MINOR and the contract lists the value under the open enum

### Requirement: Data versioning policy

Dataset versions SHALL follow these rules. MAJOR: removing or renaming a table or column, changing a column type, narrowing an enum, or changing key semantics. MINOR: adding tables, columns, views or identifiers, adding open-enum values, or adding a validation gate. PATCH: value changes only. A column or resource SHALL be marked `deprecated` in `contract.json` in a MINOR release before it is removed, and SHALL NOT be removed before the next MAJOR release.

#### Scenario: Column removal requires deprecation

- **WHEN** a column is removed in a MAJOR release
- **THEN** an earlier MINOR release listed that column under `deprecated` in `contract.json`

### Requirement: Identifier stability

An intblock ID or country code present in the previous release SHALL NOT disappear unless the alias files (`intblocks_aliases` / `countries_aliases`) contain an entry for it with a `reason` of `merged`, `renamed`, `disambiguated` or `retired` (`retired` entries have no target). Validation SHALL fail otherwise.

#### Scenario: Silent removal rejected

- **WHEN** a pull request deletes an intblock YAML file without adding an alias entry for its ID
- **THEN** validation fails and names the missing alias

### Requirement: Explicit DuckDB compatibility

The builder SHALL set DuckDB `storage_compatibility_version` explicitly and `contract.json` SHALL declare it together with `min_duckdb`, the oldest DuckDB version the release is tested with.

#### Scenario: Builder DuckDB upgrade

- **WHEN** the builder's DuckDB pin is raised
- **THEN** the storage compatibility version of `internacia.duckdb` does not change unless `contract.json` is changed in the same pull request

### Requirement: Hugging Face dataset mirror

Tagged releases SHALL publish countries and intblocks Parquet artifacts to a Hugging Face Datasets repository linked from README.

#### Scenario: HF dataset updated on release

- **WHEN** release workflow completes for tag `v*`
- **THEN** the Hugging Face dataset revision matches the release Parquet artifacts

### Requirement: Automated Zenodo deposit

Each published GitHub Release SHALL be archived to Zenodo by the Zenodo GitHub integration under the concept DOI, producing a version-specific DOI for each release. The release workflow SHALL NOT deposit to Zenodo itself, so each release has exactly one Zenodo version.

#### Scenario: Zenodo version follows tag

- **WHEN** tag `v2.0.0` is released
- **THEN** Zenodo records a new version linked to concept DOI `10.5281/zenodo.20706176`

#### Scenario: No duplicate deposit

- **WHEN** the release workflow runs for tag `v*`
- **THEN** it publishes the GitHub Release without calling the Zenodo API

### Requirement: Schema migration diff artifacts

When a release build detects a change in `schema_hash` compared to the previous semver release, the build SHALL emit `data/datasets/migration.vX.Y.Z.json` listing field-level schema changes per dataset (added, removed, renamed, type-changed).

#### Scenario: Breaking field change documented

- **WHEN** a release removes or renames a top-level country field
- **THEN** the migration JSON for that version lists the change with old and new names

#### Scenario: Patch release without schema change

- **WHEN** schema_hash is unchanged between releases
- **THEN** no migration file is required or an empty migration document states no schema changes

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

### Requirement: Content-complete artifact verification
Artifact verification SHALL reject changed projected values, duplicate keys,
missing metadata, invalid schema hashes, changed source records, and mismatched
membership edges. Checks SHALL account for deliberate source-only fields.

#### Scenario: Content corruption preserves identifiers
- **WHEN** one exported value changes without changing its primary key
- **THEN** verification fails and identifies the dataset and format

#### Scenario: Committed freshness precedes fresh-build tests
- **WHEN** CI validates a change
- **THEN** it verifies committed exports before rebuilding and tests the final staged artifacts

### Requirement: Resolvable distribution package
Each distribution descriptor SHALL contain unique physical resource names and
reference only files included in that distribution. Release publication SHALL
follow tests, quality checks, and release-version consistency validation.

#### Scenario: Partial mirror
- **WHEN** a mirror publishes only selected formats
- **THEN** its descriptor lists only those published resource paths

### Requirement: Recursive migration evidence
Migration reports SHALL compare nested source and export contracts against a
named previous release, recording baseline identity or explicit unavailability.

#### Scenario: Nested type change
- **WHEN** an array item or nested field type changes
- **THEN** the migration report identifies the affected field path

### Requirement: Attribute intblock retirement release notes

Retiring attribute-partition intblocks and adding corresponding country fields SHALL be documented as a consumer-affecting change in `CHANGELOG.md` with before/after query examples, a pointer to `attribute_intblock_migrations.json`, and an updated `migration.v*.json` (or Unreleased migration) listing countries fields added and intblock/blocktype removals.

#### Scenario: CHANGELOG shows RHTRAFFIC migration

- **WHEN** a consumer reads the CHANGELOG entry for this release
- **THEN** it shows that `RHTRAFFIC` / `LHTRAFFIC` membership queries are replaced by `car_side` filters

#### Scenario: Migration JSON lists removals

- **WHEN** `data/datasets/migration.vUnreleased.json` (or the versioned migration file for the release) is read
- **THEN** countries `added` includes the new attribute fields and intblocks/blocktypes document the retired attribute categories or ids

### Requirement: Attribute migration artifact in release assets

The exported `attribute_intblock_migrations.json` artifact SHALL be published with dataset releases alongside other consumer aids so offline users can remap retired intblock ids without cloning source YAML.

#### Scenario: Release includes attribute migration map

- **WHEN** a release workflow completes for a `v*` tag that includes this change
- **THEN** release assets include `attribute_intblock_migrations.json`

### Requirement: Former-membership fields in columnar exports

The Parquet and DuckDB intblock exports SHALL carry the `includes[].left` departure date, and any source field intentionally excluded from columnar exports SHALL be listed in consumer documentation (`README.md` and `docs/ai-consumers.md`) as source-only.

#### Scenario: Departure dates queryable in DuckDB

- **WHEN** a consumer runs a former-membership query against the `intblocks` table in `internacia.duckdb`
- **THEN** `includes[].left` values are present and match the YAML sources

#### Scenario: Intentional divergence documented

- **WHEN** a field exists in intblock YAML sources but not in the Parquet/DuckDB schema
- **THEN** consumer documentation lists that field as source-only

### Requirement: Plain JSONL artifacts

Each dataset build SHALL publish uncompressed JSONL artifacts (`countries.jsonl`, `intblocks.jsonl`, `blocktypes.jsonl`) alongside the zstd-compressed variants, with identical row content.

#### Scenario: Sandboxed agent reads plain JSONL

- **WHEN** a consumer without zstd support downloads `countries.jsonl`
- **THEN** it parses as one JSON object per line with the same rows as `countries.jsonl.zst`

#### Scenario: Consistency guard covers plain JSONL

- **WHEN** the artifact-consistency guard runs
- **THEN** plain JSONL row counts and primary-key sets match all other formats

### Requirement: Flattened membership edge export

The build SHALL emit a normalized membership edge artifact (`intblock_id`, `country_code`, `status`, `joined`, `left`) in Parquet and CSV, and as a `memberships` table inside the DuckDB artifact, derived from country-type `includes` entries.

#### Scenario: CSV agent joins memberships

- **WHEN** a consumer loads `memberships.csv` and joins `country_code` to countries `code`
- **THEN** roster analytics work without unnesting nested lists

#### Scenario: Edge rows match source includes

- **WHEN** the consistency guard compares the edge artifact to intblock sources
- **THEN** the edge row count equals the total number of country-type `includes` entries

### Requirement: Country alias artifact in release

GitHub Release assets and committed `data/datasets/` artifacts SHALL include `countries_aliases.json` when any country code alias is defined.

#### Scenario: Alias ships with release

- **WHEN** a semver release build completes after the Kosovo rename
- **THEN** `countries_aliases.json` is present in release assets alongside countries Parquet and DuckDB

### Requirement: Changelog fragments

A pull request SHALL record its consumer-visible changes as one fragment file `changelog.d/<slug>.md` instead of editing `CHANGELOG.md`. A fragment SHALL contain only Keep a Changelog subsections (`### Added`, `### Changed`, `### Deprecated`, `### Removed`, `### Fixed`, `### Security`), each with at least one entry. Entries SHALL NOT carry running dataset totals. When the release train writes a release, it SHALL merge the `[Unreleased]` body of `CHANGELOG.md` and every fragment into the dated release section, grouped by subsection in Keep a Changelog order, and SHALL delete the merged fragments in the same release pull request.

#### Scenario: Two pull requests add entries

- **WHEN** two open pull requests each add a changelog fragment with a different slug
- **THEN** neither pull request conflicts with the other in changelog files

#### Scenario: Release merges fragments

- **WHEN** the release train applies `v4.3.0` with fragments `ah.md` (`### Added`) and `fix-view.md` (`### Fixed`)
- **THEN** the `## [4.3.0]` section has one `### Added` and one `### Fixed` subsection holding those entries, and `changelog.d/` keeps only its README

#### Scenario: Unknown subsection

- **WHEN** a fragment uses `### Notes`
- **THEN** the test suite fails and names the fragment

### Requirement: Composite currency blocktype deprecation

`contract.json` SHALL list `eccurr` and `cuscurr` under `deprecated` as `enum_value` entries for `intblocks.blocktype`, with replacements `[economic, currency]` and `[customs, currency]` and `removal: next MAJOR`. Both values SHALL be removed from records and from the taxonomy only in a MAJOR release, and `CHANGELOG.md` SHALL give the replacement queries.

#### Scenario: Deprecation listed in the contract

- **WHEN** `scripts/builder.py build` runs with `eccurr` and `cuscurr` marked deprecated
- **THEN** `contract.json` `deprecated` contains an entry for each value with its replacements and `removal: next MAJOR`

#### Scenario: Query unchanged during the deprecation window

- **WHEN** a consumer runs `list_contains(blocktype, 'cuscurr')` on the MINOR release that deprecates it
- **THEN** the query returns `CEMAC` and `UEMOA`, the same IDs as on the release before

#### Scenario: Replacement query after removal

- **WHEN** a release removes `cuscurr`
- **THEN** the release is MAJOR and `CHANGELOG.md` gives `list_has_all(blocktype, ['customs', 'currency'])` as the replacement query

