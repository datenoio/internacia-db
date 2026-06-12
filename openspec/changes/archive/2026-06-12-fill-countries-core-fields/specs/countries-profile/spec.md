## ADDED Requirements

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

`gini` SHALL use the same struct shape as other indicators when present. Records without inequality data MAY omit `gini` or leave it null without failing the build if gini completeness is in warn mode.

#### Scenario: Gini present when World Bank reports value

- **WHEN** World Bank provides Gini for a country
- **THEN** `gini.value`, `gini.year`, and `gini.source` are populated in YAML and export

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
