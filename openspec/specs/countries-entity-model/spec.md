# countries-entity-model Specification

## Purpose
TBD - created by archiving change add-countries-entity-status. Update Purpose after archive.
## Requirements
### Requirement: Entity type classification

Every country YAML record SHALL include `entity_type` from the allowed enumeration: `sovereign_state`, `dependent_territory`, `special_administrative_region`, `disputed_territory`, `historical_entity`, `supranational_grouping`, or `statistical_area`.

#### Scenario: Sovereign state classified

- **WHEN** a record represents an independent UN member state such as France
- **THEN** `entity_type` is `sovereign_state`

#### Scenario: Invalid entity type rejected

- **WHEN** a record has `entity_type: country`
- **THEN** validation reports an enum error

### Requirement: Code status classification

Every country record SHALL include `code_status` from: `official_iso3166_1`, `user_assigned`, `obsolete`, or `exceptionally_reserved`.

#### Scenario: Current ISO code marked official

- **WHEN** a record uses a current ISO 3166-1 alpha-2 code such as `FR`
- **THEN** `code_status` is `official_iso3166_1`

#### Scenario: Non-ISO code requires explicit status

- **WHEN** a record has `code` not in the current ISO 3166-1 set
- **THEN** `code_status` MUST NOT be `official_iso3166_1` and MUST be set explicitly

### Requirement: Netherlands Antilles obsolete status

Record `AN` SHALL have `entity_type: historical_entity` and `code_status: obsolete`.

#### Scenario: AN filtered from current ISO views

- **WHEN** a consumer queries records with `code_status == official_iso3166_1`
- **THEN** record `AN` is excluded

### Requirement: Channel Islands grouping status

Record `JG` SHALL have `entity_type: supranational_grouping` and `code_status: user_assigned`.

#### Scenario: JG documented as non-ISO collective

- **WHEN** `docs/country-code-policy.md` is read
- **THEN** it states that `GG` and `JE` are canonical territory codes for Channel Islands constituents

### Requirement: Kosovo user-assigned status

Record `KV` SHALL have `entity_type: disputed_territory`, `code_status: user_assigned`, and `recognition_status` indicating disputed or partially recognized status.

#### Scenario: KV retains code with metadata

- **WHEN** the entity status change is applied
- **THEN** `KV` remains in the dataset with explicit non-ISO metadata rather than being deleted

### Requirement: Current ISO filter cardinality

Records with `code_status: official_iso3166_1` SHALL number 249 when aligned with the 2026-05-28 ISO-style audit baseline.

#### Scenario: Official ISO count matches audit

- **WHEN** all country sources are annotated
- **THEN** exactly 249 records have `code_status: official_iso3166_1`

