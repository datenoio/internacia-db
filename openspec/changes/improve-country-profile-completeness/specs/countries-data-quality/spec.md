## MODIFIED Requirements

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

## ADDED Requirements

### Requirement: Capital coverage for eligible entities

Country and territory records that have a de-facto capital or seat of government SHALL populate `capital_city` (name and coordinates) with a `provenance` entry, while genuinely capital-less entities (for example uninhabited territories) SHALL be documented as expected exclusions rather than counted as data gaps.

#### Scenario: Seat of government populated

- **WHEN** a record represents an entity with a de-facto capital or seat of government and `capital_city` is empty
- **THEN** the field is filled with name and coordinates and a `provenance` entry

#### Scenario: Uninhabited entity documented as exclusion

- **WHEN** a record represents an uninhabited territory with no capital
- **THEN** it is documented as an expected exclusion and does not count as an unexplained gap
