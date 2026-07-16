## ADDED Requirements

### Requirement: Generated artifact primary-key parity

Every committed dataset export format (JSONL, YAML, Parquet, and DuckDB) SHALL contain the same primary-key set and row count for each dataset, and that set SHALL equal the set of ids in the corresponding YAML sources. A consistency checker SHALL verify this and exit non-zero on any difference.

#### Scenario: All formats agree with source

- **WHEN** `scripts/check_generated_artifacts.py` runs against a freshly built `data/datasets/`
- **THEN** the countries, intblocks, and blocktypes id sets are identical across JSONL, YAML, Parquet, and DuckDB and match the YAML source id sets, and the checker exits 0

#### Scenario: Format missing a record fails

- **WHEN** one export format is missing an id that other formats and the YAML source contain
- **THEN** the checker reports the missing id and dataset and exits non-zero

### Requirement: Single build identity across generated artifacts

All manifests, Parquet `*.meta.json` sidecars, and DuckDB `_meta` rows in `data/datasets/` SHALL agree on `version`, `git_commit`, and `build_date`, so consumers can confirm the artifacts came from one build.

#### Scenario: Consistent build identity passes

- **WHEN** the consistency checker compares build identity fields across all metadata artifacts
- **THEN** it confirms a single `version`, `git_commit`, and `build_date` and exits 0

#### Scenario: Mixed build commits fail

- **WHEN** `countries.manifest.json` and `intblocks.manifest.json` report different `git_commit` values
- **THEN** the checker reports the divergent build identity and exits non-zero
