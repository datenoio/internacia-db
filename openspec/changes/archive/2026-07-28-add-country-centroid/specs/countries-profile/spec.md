## ADDED Requirements

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
