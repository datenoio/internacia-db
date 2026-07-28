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

Completeness rules SHALL be defined in `data/schemas/countries_completeness.yaml` with per-field `max_null_rate` and `mode` (`warn` or `error`). Thresholds and denominators SHALL be documented with a rationale, and fields that are structurally unavailable for some entity classes (such as `gini`) MAY scope their denominator to the entity classes where a value can exist so the configured budget reflects data reality rather than remaining permanently exceeded.

#### Scenario: Advertised field at high null rate warns

- **WHEN** a field's null rate exceeds its configured `max_null_rate` with `mode: warn`
- **THEN** validation emits a warning but does not fail the build

#### Scenario: Field exceeding threshold fails in error mode

- **WHEN** a field has `mode: error` and null rate exceeds `max_null_rate`
- **THEN** validation fails with a completeness error

#### Scenario: Scoped denominator documented

- **WHEN** a structurally-sparse field like `gini` scopes its completeness denominator to eligible entities
- **THEN** the completeness config or documentation records the scope and rationale

### Requirement: Border reference format

Each entry in `borders` SHALL be a three-letter uppercase ISO 3166-1 alpha-3 country code representing a land border neighbor.

#### Scenario: Valid alpha-3 border accepted

- **WHEN** `borders` contains `CAN` and `MEX` for United States
- **THEN** border format validation passes

#### Scenario: Alpha-2 border rejected

- **WHEN** `borders` contains `US` instead of a three-letter code
- **THEN** border format validation reports an error

### Requirement: Country contact and locale field validity

Validation SHALL check `tld` against the `.xx`-style lowercase format, each `calling_codes` entry against the `+digits` format, each `timezones` entry against the IANA tz database (when available to the runtime), and `start_of_week`-independent locale fields for structural validity. Violations SHALL be reported as `INVALID_TLD`, `INVALID_CALLING_CODE`, and `INVALID_TIMEZONE` warnings.

#### Scenario: Malformed calling code warned

- **WHEN** a country record has `calling_codes` containing `+35818` with more than four digits
- **THEN** validation reports an `INVALID_CALLING_CODE` warning for that entry

#### Scenario: Unknown timezone warned

- **WHEN** a country record lists a timezone not present in the IANA tz database
- **THEN** validation reports an `INVALID_TIMEZONE` warning

### Requirement: Flag emoji consistency

For records whose `code` is a two-letter uppercase code with `code_status: official_iso3166_1`, a populated `flag_emoji` SHALL equal the Unicode regional-indicator pair derived from `code`. Mismatches SHALL be reported as `FLAG_EMOJI_MISMATCH`.

#### Scenario: Wrong flag emoji warned

- **WHEN** the record for `FR` has `flag_emoji` equal to the German flag emoji
- **THEN** validation reports a `FLAG_EMOJI_MISMATCH` warning

### Requirement: Landlocked and border consistency

A record with `landlocked: true` SHALL have a non-empty `borders` list, since an entity with no land neighbors cannot be landlocked. Violations SHALL be reported as `LANDLOCKED_INCONSISTENCY`.

#### Scenario: Landlocked island warned

- **WHEN** a record has `landlocked: true` and an empty or missing `borders` list
- **THEN** validation reports a `LANDLOCKED_INCONSISTENCY` warning

### Requirement: Continent and subregion hierarchy consistency

A record's `subregion` SHALL belong to at least one of its `continents` per a canonical continent→subregion table. Documented exceptions (transcontinental and administratively reassigned entities) SHALL be suppressed via `region_hierarchy.allowlist` in `countries_completeness.yaml`. Violations SHALL be reported as `REGION_HIERARCHY_MISMATCH`.

#### Scenario: Subregion outside continent warned

- **WHEN** a record lists continent `Asia` with subregion `Caribbean` and is not allowlisted
- **THEN** validation reports a `REGION_HIERARCHY_MISMATCH` warning

#### Scenario: Allowlisted exception suppressed

- **WHEN** `CX` (continent `Asia`, subregion `Australia and New Zealand`) is present in `region_hierarchy.allowlist`
- **THEN** no `REGION_HIERARCHY_MISMATCH` issue is reported for `CX`

### Requirement: Parent entity resolution

When `parent_entity.code` is populated, it SHALL resolve to an existing country record. Violations SHALL be reported as `UNRESOLVED_PARENT_ENTITY`.

#### Scenario: Unresolved parent entity reported

- **WHEN** a record has `parent_entity.code: ZZ` and no `data/countries/ZZ.yaml` exists
- **THEN** validation reports an `UNRESOLVED_PARENT_ENTITY` issue

### Requirement: Capital coordinate plausibility

The great-circle distance between `capital_city` and `centroid` coordinates SHALL NOT exceed an area-scaled threshold (`max(min_km, area_multiplier × √area_km²)`, configurable under `geography.capital_distance` in `countries_completeness.yaml`). Legitimate outliers (external capitals, dispersed territories) SHALL be suppressed via the rule's allowlist. Violations SHALL be reported as `CAPITAL_FAR_FROM_CENTROID`, catching swapped or mis-signed coordinates that pass range validation.

#### Scenario: Swapped capital coordinates warned

- **WHEN** a record's capital coordinates place the city thousands of kilometres from the centroid because lat and lng are swapped
- **THEN** validation reports a `CAPITAL_FAR_FROM_CENTROID` warning

#### Scenario: Large-country capital passes

- **WHEN** Russia's capital is ~3,500 km from its centroid and its area-scaled threshold exceeds that distance
- **THEN** no `CAPITAL_FAR_FROM_CENTROID` issue is reported

### Requirement: Text encoding integrity for countries

Name fields (`name`, `official_name`, `common_names`) SHALL NOT contain control characters, U+FFFD replacement characters, or double-encoded UTF-8 artifacts. Violations SHALL be reported as `MOJIBAKE_TEXT`.

#### Scenario: Replacement character reported

- **WHEN** a country name contains U+FFFD
- **THEN** validation reports a `MOJIBAKE_TEXT` issue

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

### Requirement: Capital coverage for eligible entities

Country and territory records that have a de-facto capital or seat of government SHALL populate `capital_city` (name and coordinates) with a `provenance` entry, while genuinely capital-less entities (for example uninhabited territories) SHALL be documented as expected exclusions rather than counted as data gaps.

#### Scenario: Seat of government populated

- **WHEN** a record represents an entity with a de-facto capital or seat of government and `capital_city` is empty
- **THEN** the field is filled with name and coordinates and a `provenance` entry

#### Scenario: Uninhabited entity documented as exclusion

- **WHEN** a record represents an uninhabited territory with no capital
- **THEN** it is documented as an expected exclusion and does not count as an unexplained gap

