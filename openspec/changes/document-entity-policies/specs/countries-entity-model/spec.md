## ADDED Requirements

### Requirement: Entity classification policy document

The repository SHALL maintain `docs/entity-classification-policy.md` explaining how `entity_type`, `independent`, `un_member`, `un_status`, and `recognition_status` interact for disputed territories, partially recognized states, and special cases (including Taiwan, Palestine, Kosovo, Western Sahara, Vatican City, and associated states).

#### Scenario: Taiwan classification explained

- **WHEN** a reader asks why Taiwan is `dependent_territory` rather than `disputed_territory`
- **THEN** the policy doc states the rationale and cites the relevant classification dimensions

#### Scenario: Independence vs UN membership distinguished

- **WHEN** a consumer filters `independent: true`
- **THEN** the policy doc explains how Vatican City, Kosovo, and associated states are classified

### Requirement: CIS2 build inclusion policy

`docs/country-code-policy.md` SHALL state explicitly whether user-assigned CIS2 codes (`XA`, `XS`, `XT`, `XN`) are included in all standard build exports (Parquet, DuckDB, JSONL, CSV) and how consumers should filter them for ISO-only views.

#### Scenario: CIS2 codes in DuckDB

- **WHEN** a consumer queries `SELECT code FROM countries` in `internacia.duckdb`
- **THEN** the policy doc matches actual export behavior for XA, XS, XT, and XN
