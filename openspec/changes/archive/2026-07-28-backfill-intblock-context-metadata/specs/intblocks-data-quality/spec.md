## ADDED Requirements

### Requirement: High-profile intblock contextual metadata

High-profile intblock records (maintainer-defined cohort including UN principal organs, major regional blocs, and top multilateral institutions) SHALL have non-empty `legal_status`, `geographic_scope`, and `headquarters` after backfill.

#### Scenario: Major IGO has legal status

- **WHEN** backfill completes for a UN specialized agency in the high-profile cohort
- **THEN** the record includes `legal_status` describing its treaty or charter basis

#### Scenario: Major IGO has geographic scope

- **WHEN** backfill completes for NATO in the high-profile cohort
- **THEN** the record includes `geographic_scope` indicating regional or global reach

#### Scenario: Major IGO has headquarters

- **WHEN** backfill completes for the European Union in the high-profile cohort
- **THEN** the record includes `headquarters` with city and country

### Requirement: Context field provenance on enrichment

Automated or semi-automated backfill of `legal_status`, `geographic_scope`, or `headquarters` SHALL add corresponding `provenance` entries.

#### Scenario: Headquarters enrichment provenance

- **WHEN** `headquarters` is filled from an official organization website
- **THEN** a provenance entry documents `field`, `source`, and `retrieved_at`

## MODIFIED Requirements

### Requirement: Description quality gate

`validate_intblocks.py` SHALL measure the share of records using templated boilerplate descriptions
and report it against a configurable threshold in `intblocks_completeness.yaml` (warn or error mode).
After high-profile description replacement, the configured templated-description `max_null_rate` or
equivalent threshold SHALL be tightened incrementally (e.g. from current ~24% toward ≤15% warn target).

#### Scenario: Templated description counted

- **WHEN** a record's description matches the boilerplate pattern (e.g. "International entity focused on …")
- **THEN** it is counted toward the templated-description rate in the validation report

#### Scenario: Rate over threshold warns

- **WHEN** the templated-description rate exceeds the configured `max` with `mode: warn`
- **THEN** validation emits a warning but does not fail the build

#### Scenario: Threshold ratchets after backfill

- **WHEN** high-profile description replacement reduces the templated rate below the previous threshold
- **THEN** maintainers MAY lower the configured warn threshold in `intblocks_completeness.yaml` to prevent regression
