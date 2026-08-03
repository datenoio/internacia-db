## ADDED Requirements

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
