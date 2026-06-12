## MODIFIED Requirements

### Requirement: Intblock country includes resolve to country sources

Every `includes` entry in `data/intblocks/**/*.yaml` with `type: country` SHALL reference an existing `data/countries/{id}.yaml` file unless the `id` is listed in `special_entity_allowlist` in `countries_completeness.yaml`.

For allowlisted IDs without country YAML files, validation SHALL emit a **warning** (not error) until policy adds profiles or reclassifies include types. Unresolved, non-allowlisted references SHALL be reported according to the configured `unresolved_country_includes.mode` (warn or error).

#### Scenario: Valid country reference passes

- **WHEN** an intblock include has `id: US` and `type: country`
- **THEN** cross-dataset validation reports no error for that include

#### Scenario: Deferred CIS2 reference warns with policy note

- **WHEN** an intblock include has `id: XA`, `type: country`, and no country YAML exists
- **THEN** validation emits a warning referencing deferred policy in country-code documentation

#### Scenario: Allowlisted special entity passes without profile

- **WHEN** an include `id` is on `special_entity_allowlist` and no `data/countries/{id}.yaml` exists
- **THEN** validation does not treat the reference as an unresolved error

#### Scenario: Unresolved country include uses configured mode

- **WHEN** an intblock includes a country id with no matching YAML file and the id is not allowlisted
- **THEN** validation reports per the configured `unresolved_country_includes.mode`

## ADDED Requirements

### Requirement: Intblock partof reference validation

Each value in an intblock's `partof` list SHALL reference an existing intblock `id` in `data/intblocks/**/*.yaml`.

#### Scenario: Valid partof reference accepted

- **WHEN** an intblock has `partof: [UN]` and an intblock with `id: UN` exists
- **THEN** partof validation passes

#### Scenario: Invalid partof reference reported

- **WHEN** an intblock references `partof: [NONEXISTENT]` with no matching intblock id
- **THEN** validation reports a partof reference error
