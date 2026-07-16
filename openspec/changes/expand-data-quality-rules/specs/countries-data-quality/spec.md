## ADDED Requirements

### Requirement: Indicator value plausibility

Country indicator structs SHALL contain plausible values: `population.value` and `area.value` positive numbers, `gini.value` between 0 and 100 exclusive, and indicator `year` values not in the future. Violations SHALL be reported as `INVALID_INDICATOR_VALUE` at MEDIUM priority.

#### Scenario: Non-positive population reported

- **WHEN** a country record has `population.value: 0`
- **THEN** validation reports an `INVALID_INDICATOR_VALUE` issue for `population.value`

#### Scenario: Gini outside range reported

- **WHEN** a country record has `gini.value: 140`
- **THEN** validation reports an `INVALID_INDICATOR_VALUE` issue for `gini.value`

#### Scenario: Future indicator year reported

- **WHEN** a country record has `population.year` greater than the current year
- **THEN** validation reports an `INVALID_INDICATOR_VALUE` issue for `population.year`

### Requirement: Entity flag consistency

Boolean status flags SHALL be consistent with `entity_type`: records with `entity_type` of `dependent_territory`, `special_administrative_region`, or `statistical_area` SHALL NOT declare `un_member: true` or `independent: true`. Violations SHALL be reported as `INCONSISTENT_ENTITY_FLAGS` at MEDIUM priority.

#### Scenario: Dependent territory with UN membership reported

- **WHEN** a country record has `entity_type: dependent_territory` and `un_member: true`
- **THEN** validation reports an `INCONSISTENT_ENTITY_FLAGS` issue

#### Scenario: Sovereign state flags pass

- **WHEN** a record has `entity_type: sovereign_state`, `un_member: true`, and `independent: true`
- **THEN** entity flag validation passes

### Requirement: Country quality report parity

Every country rule enforced by `validate_countries.py` SHALL also be executed by the quality analyzer and surfaced in `dataquality/` reports, including currency code validation, coordinate range checks for `centroid` and `capital_city`, filename-to-`code` alignment, and provenance freshness and integrity (each `provenance[].field` naming an existing record field with a valid, non-future `retrieved_at` date).

#### Scenario: Invalid currency code appears in quality report

- **WHEN** a country record has a currency code not matching the ISO 4217 format
- **THEN** the analyzer reports an `INVALID_CURRENCY_CODE` issue in `dataquality/` reports

#### Scenario: Out-of-range coordinates appear in quality report

- **WHEN** a country record has `capital_city.lat` outside the range -90 to 90
- **THEN** the analyzer reports an `INVALID_COORDINATES` issue

#### Scenario: Filename and code mismatch appears in quality report

- **WHEN** the file `data/countries/DE.yaml` contains `code: AT`
- **THEN** the analyzer reports a `FILENAME_ID_MISMATCH` issue

#### Scenario: Provenance referencing unknown field appears in quality report

- **WHEN** a country record's `provenance` list contains `field: nonexistent_field`
- **THEN** the analyzer reports a `PROVENANCE_INTEGRITY` issue
