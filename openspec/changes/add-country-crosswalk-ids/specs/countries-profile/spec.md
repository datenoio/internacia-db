## ADDED Requirements

### Requirement: Country crosswalk identifiers

Country records MAY include optional crosswalk identifier fields `geonames_id` (integer), `ioc_code` (string), `fifa_code` (string), and `fips_code` (string) declared in `countries.schema.json`. When present, each field SHALL include provenance citing the authoritative source.

#### Scenario: Schema accepts geonames_id

- **WHEN** a country YAML record includes `geonames_id: 2921044`
- **THEN** validation passes against the updated schema

#### Scenario: Crosswalk documented for integrators

- **WHEN** a consumer reads `docs/ai-consumers.md`
- **THEN** they find join guidance for each crosswalk field and known null cases on non-standard codes

### Requirement: Crosswalk backfill for ISO records

Official ISO 3166-1 country records (`code_status: official_iso3166_1`) SHALL be backfilled with crosswalk identifiers where an authoritative mapping exists, targeting high coverage on `geonames_id`, `ioc_code`, and `fifa_code`.

#### Scenario: Major sovereign state has geonames_id

- **WHEN** a consumer reads `data/countries/US.yaml` after backfill
- **THEN** `geonames_id` is populated with a Wikidata- or GeoNames-sourced value and provenance
