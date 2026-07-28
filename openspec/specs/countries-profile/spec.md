# countries-profile Specification

## Purpose
TBD - created by archiving change fill-countries-core-fields. Update Purpose after archive.
## Requirements
### Requirement: Structured population indicator

Every country record where a population estimate exists SHALL store `population` as a struct with at least `value` (integer), `year` (integer), and `source` (string).

#### Scenario: United States has sourced population

- **WHEN** `data/countries/US.yaml` is enriched
- **THEN** `population.value` is a positive integer, `population.year` is set, and `population.source` is non-empty

#### Scenario: Exported Parquet uses struct type

- **WHEN** the builder exports `countries.parquet`
- **THEN** the `population` column is a struct type, not a bare int64

### Requirement: Structured area indicator

Every country record where area data exists SHALL store `area` as a struct with `value` (square kilometers, float), `year`, and `source`.

#### Scenario: Area populated for sovereign state

- **WHEN** enrichment runs for `data/countries/FR.yaml`
- **THEN** `area.value` is greater than zero and includes year and source

### Requirement: Gini with sparse coverage

`gini` SHALL use the same struct shape as other indicators when present. Records without inequality data MAY omit `gini` or leave it null without failing the build if gini completeness is in warn mode. After historical backfill, maintainers SHALL incrementally lower the configured `max_null_rate` toward the report target (below 32.5% missing) in coordination with enrichment refresh governance.

#### Scenario: Gini present when World Bank reports value

- **WHEN** World Bank provides Gini for a country
- **THEN** `gini.value`, `gini.year`, and `gini.source` are populated in YAML and export

#### Scenario: Historical gini counts toward coverage

- **WHEN** only an older Gini estimate is available and enrichment adds it
- **THEN** the record counts as having `gini` populated for completeness metrics

### Requirement: Timezones for inhabited entities

Records for inhabited countries and territories SHALL have a non-empty `timezones` list with IANA timezone identifiers where applicable.

#### Scenario: US has multiple timezones

- **WHEN** enrichment runs for United States
- **THEN** `timezones` includes identifiers such as `America/New_York`

#### Scenario: Uninhabited territory marked not applicable

- **WHEN** a territory has no assigned IANA zones (e.g. Bouvet Island)
- **THEN** `timezones` is an empty list and `timezone_status` is `not_applicable`

### Requirement: Native names map

Every country record SHALL have `native_names` as a map from ISO 639 language code to `{official, common}` strings for at least one language where Wikidata or official sources provide labels.

#### Scenario: Native names populated

- **WHEN** enrichment completes for all country sources
- **THEN** no country record has a null or missing `native_names` key at export time

### Requirement: Partial gap reduction

Enrichment SHALL reduce audit gaps for `common_names`, `wikidata_id`, and `capital_city` per the 2026-05-28 report targets.

#### Scenario: Wikidata ID filled where resolvable

- **WHEN** enrichment resolves Wikidata for a country missing `wikidata_id`
- **THEN** the YAML file contains a valid `Q` identifier matching Wikidata entity validation rules

#### Scenario: Island borders use empty list

- **WHEN** a country has no land borders
- **THEN** `borders` is `[]` rather than null or omitted

### Requirement: Strict completeness for former blocker fields

After this change, `countries_completeness.yaml` SHALL set `mode: error` for `population`, `area`, `timezones`, and `native_names`.

#### Scenario: Build fails if population still 100% null

- **WHEN** all country records lack `population` after this change is applied
- **THEN** validation fails with a completeness error

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

### Requirement: Country centroid coordinates

Every country and territory record SHALL include a `centroid` object with `lat` (float, -90 to 90) and `lng` (float, -180 to 180) representing the geographic centroid of the entity.

#### Scenario: Sovereign state has centroid

- **WHEN** `data/countries/US.yaml` is enriched
- **THEN** `centroid.lat` and `centroid.lng` are populated with values from an authoritative geographic source

#### Scenario: All records covered

- **WHEN** enrichment completes for all 252 country sources
- **THEN** no country record lacks `centroid` at export time

#### Scenario: Exported Parquet uses struct type

- **WHEN** the builder exports `countries.parquet`
- **THEN** the `centroid` column is a struct with `lat` and `lng` fields

#### Scenario: Invalid coordinates rejected

- **WHEN** a country record has `centroid.lat` outside -90..90 or `centroid.lng` outside -180..180
- **THEN** validation reports a coordinate range error

### Requirement: Centroid provenance

Centroid values populated from external sources SHALL include a `provenance` entry with `field: centroid`, `source`, and `retrieved_at`.

#### Scenario: Natural Earth sourcing documented

- **WHEN** centroid is imported from Natural Earth
- **THEN** the country record's provenance lists the Natural Earth source and retrieval date

