## MODIFIED Requirements

### Requirement: Membership list internal consistency

Intblock membership data SHALL be internally consistent: an `includes` list SHALL NOT contain two entries with the same `id`, a populated `membership_count` SHALL match the number of `includes` entries within the tolerance configured in `data/schemas/intblocks_completeness.yaml` unless the record declares a non-country `membership_count_type`, and a record with `membership_applicability: not_applicable` SHALL NOT have a non-empty `includes` list. Violations SHALL be reported as `DUPLICATE_INCLUDE_ENTRY`, `MEMBERSHIP_COUNT_MISMATCH`, and `CONTRADICTORY_APPLICABILITY` respectively at MEDIUM priority.

#### Scenario: Duplicate include entry reported

- **WHEN** an intblock's `includes` list contains two entries with `id: FR`
- **THEN** validation reports a `DUPLICATE_INCLUDE_ENTRY` issue

#### Scenario: Membership count mismatch reported

- **WHEN** an intblock has `membership_count: 10` and 13 `includes` entries with mismatch beyond the configured tolerance and no non-country `membership_count_type`
- **THEN** validation reports a `MEMBERSHIP_COUNT_MISMATCH` issue

#### Scenario: Non-country count exempt from roster comparison

- **WHEN** an intblock declares `membership_count_type: companies` with `membership_count: 3000` and a short country `includes` list
- **THEN** validation does not report a `MEMBERSHIP_COUNT_MISMATCH` issue

#### Scenario: Contradictory applicability marker reported

- **WHEN** an intblock has `membership_applicability: not_applicable` and a non-empty `includes` list
- **THEN** validation reports a `CONTRADICTORY_APPLICABILITY` issue

## ADDED Requirements

### Requirement: Membership count unit qualifier

The intblock schema SHALL provide an optional `membership_count_type` field (enum: `countries`, `organizations`, `companies`, `individuals`, `mixed`) declaring the unit of `membership_count`. When absent, the count SHALL be interpreted as country members. Records declaring a non-country type SHALL carry a provenance entry for `membership_count`.

#### Scenario: Consumer distinguishes count units

- **WHEN** a consumer reads a record with `membership_count: 3000` and `membership_count_type: companies`
- **THEN** the consumer can tell the count is not a country-member count

#### Scenario: Non-country count requires provenance

- **WHEN** a record declares a non-country `membership_count_type` without a `membership_count` provenance entry
- **THEN** validation reports an issue
