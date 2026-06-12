# countries-build Specification

## Purpose
TBD - created by archiving change add-countries-validation. Update Purpose after archive.
## Requirements
### Requirement: Builder validates before export

The dataset builder (`scripts/builder.py`) SHALL run country validation before generating JSONL, YAML, Parquet, or DuckDB outputs.

#### Scenario: Build aborts on validation failure

- **WHEN** country validation reports schema or identifier errors
- **THEN** the builder exits with non-zero status and does not write updated dataset files

#### Scenario: Successful build preserves row count

- **WHEN** all 252 country YAML sources pass validation
- **THEN** `countries.parquet` contains exactly 252 rows

### Requirement: Clean data normalization in builder

The builder `clean_data()` function SHALL apply identifier and categorical normalization rules consistent with `countries-data-quality` requirements.

#### Scenario: Builder applies whitespace cleanup

- **WHEN** the builder loads country sources with fixable whitespace issues
- **THEN** exported datasets contain trimmed categorical values without manual YAML edits

