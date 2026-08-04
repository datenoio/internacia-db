## ADDED Requirements

### Requirement: Attribute vocab id validation

When present, country fields `writing_directions`, `writing_systems`, `broadcast_systems`, `legal_systems`, and `rail_gauges` SHALL use `id` values that exist in the corresponding `data/vocabs/` catalog. `dvd_region` SHALL be an integer in 1–6 when present. `car_side` SHALL remain restricted to `left` | `right`.

#### Scenario: Unknown writing system id rejected

- **WHEN** a country record sets `writing_systems: [{id: not_a_script}]`
- **THEN** country validation reports a vocab resolution error

#### Scenario: Invalid DVD region rejected

- **WHEN** a country record sets `dvd_region: 9`
- **THEN** country validation reports a range/schema error

### Requirement: Attribute field list shape validation

List-valued attribute fields SHALL be arrays of objects with a string `id`. At most one element MAY set `primary: true` within each list. Duplicate `id` values within a single field SHALL be rejected.

#### Scenario: Two primaries rejected

- **WHEN** `writing_directions` contains two entries with `primary: true`
- **THEN** validation reports a primary-cardinality error

#### Scenario: Duplicate id rejected

- **WHEN** `legal_systems` lists `common_law` twice
- **THEN** validation reports a duplicate-id error

### Requirement: Attribute completeness warn mode

Initial completeness configuration for the new attribute fields SHALL use `mode: warn` (not `error`) so incomplete historical intblock coverage does not block builds, while still surfacing coverage regressions.

#### Scenario: Sparse legal_systems does not fail the build

- **WHEN** many country records omit `legal_systems` after migration of incomplete lawsystem rosters
- **THEN** completeness emits warnings within configured thresholds and does not fail validation in error mode
