## ADDED Requirements

### Requirement: Documented World Bank classification gaps

Country records that World Bank does not classify SHALL be documented in project policy documentation with the list of affected ISO codes and the rationale for expected absence or alternative sourcing.

#### Scenario: Policy lists non-WB entities

- **WHEN** a maintainer reads country classification policy documentation
- **THEN** the 33 entities missing WB `region`/`incomeLevel`/`lendingType` are enumerated with sourcing guidance

### Requirement: Alternative regional classification backfill

For country records where World Bank provides no regional classification, enrichment SHALL attempt UN M49 (or equivalent documented authority) mappings for `region` and `adminregion` before leaving fields empty.

#### Scenario: High-income OECD member gets M49 region

- **WHEN** a country record lacks WB `region` but UN M49 assigns a regional code
- **THEN** `region` is populated with the M49-sourced value and provenance documents the source

#### Scenario: Genuinely unclassifiable entity documented

- **WHEN** no authoritative regional classification exists for a special territory
- **THEN** the record remains without `region` and policy documentation explains why

### Requirement: Historical Gini backfill

Where recent Gini coefficient data is unavailable, enrichment SHALL populate `gini` with the most recent published estimate when an authoritative source exists, using the standard `{value, year, source}` struct and provenance.

#### Scenario: Older Gini estimate accepted

- **WHEN** World Bank provides a Gini value older than five years for a small island state
- **THEN** `gini.year` reflects the estimate year and `gini.source` identifies the publication

## MODIFIED Requirements

### Requirement: Gini with sparse coverage

`gini` SHALL use the same struct shape as other indicators when present. Records without inequality data MAY omit `gini` or leave it null without failing the build if gini completeness is in warn mode. After historical backfill, maintainers SHALL incrementally lower the configured `max_null_rate` toward the report target (below 32.5% missing) in coordination with enrichment refresh governance.

#### Scenario: Gini present when World Bank reports value

- **WHEN** World Bank provides Gini for a country
- **THEN** `gini.value`, `gini.year`, and `gini.source` are populated in YAML and export

#### Scenario: Historical gini counts toward coverage

- **WHEN** only an older Gini estimate is available and enrichment adds it
- **THEN** the record counts as having `gini` populated for completeness metrics
