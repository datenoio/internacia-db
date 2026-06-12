# countries-data-quality Specification

## Purpose
TBD - created by archiving change add-countries-validation. Update Purpose after archive.
## Requirements
### Requirement: Country YAML JSON Schema validation

Every file under `data/countries/*.yaml` SHALL validate against `data/schemas/countries.schema.json` before dataset export.

#### Scenario: Valid country file passes schema

- **WHEN** `validate_countries.py` runs on `data/countries/US.yaml`
- **THEN** validation reports no schema errors for that file

#### Scenario: Invalid country file fails schema

- **WHEN** a country YAML file has `iso3code` with fewer than three characters
- **THEN** validation reports a schema error and exits with non-zero status

### Requirement: ISO identifier format validation

Country records SHALL have syntactically valid identifiers: `code` (2-letter alpha-2), `iso3code` (3-letter alpha-3), `numeric_code` (3 digits), and `m49_code` (3 digits when present).

#### Scenario: Malformed alpha-2 rejected

- **WHEN** a country record has `code` equal to `USA`
- **THEN** validation reports an identifier format error

#### Scenario: Duplicate identifiers rejected

- **WHEN** two country YAML files share the same `iso3code`
- **THEN** validation reports a duplicate identifier error

### Requirement: Categorical string normalization

The build pipeline SHALL strip leading and trailing whitespace from categorical string fields including `subregion`, `region.value`, and `adminregion.value` before writing derived datasets.

#### Scenario: Trailing whitespace stripped at build

- **WHEN** a source YAML has `subregion` value `"Western Europe "`
- **THEN** the exported Parquet row has `subregion` equal to `"Western Europe"`

### Requirement: Configurable completeness thresholds

Completeness rules SHALL be defined in `data/schemas/countries_completeness.yaml` with per-field `max_null_rate` and `mode` (`warn` or `error`).

#### Scenario: Advertised field at 100% null warns in Change 1

- **WHEN** `population` is null in all 252 country records and completeness config sets `population.mode: warn`
- **THEN** validation emits a warning but does not fail the build

#### Scenario: Field exceeding threshold fails in error mode

- **WHEN** a field has `mode: error` and null rate exceeds `max_null_rate`
- **THEN** validation fails with a completeness error

### Requirement: Border reference format

Each entry in `borders` SHALL be a three-letter uppercase ISO 3166-1 alpha-3 country code representing a land border neighbor.

#### Scenario: Valid alpha-3 border accepted

- **WHEN** `borders` contains `CAN` and `MEX` for United States
- **THEN** border format validation passes

#### Scenario: Alpha-2 border rejected

- **WHEN** `borders` contains `US` instead of a three-letter code
- **THEN** border format validation reports an error

