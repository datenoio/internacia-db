## ADDED Requirements

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
