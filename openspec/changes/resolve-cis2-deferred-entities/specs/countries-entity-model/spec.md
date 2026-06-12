## MODIFIED Requirements

### Requirement: Non-standard country records

The countries dataset MAY include user-assigned or disputed-territory records with explicit `code_status`, `entity_type`, and optional `recognition_status`. CIS2-related codes (`XA`, `XS`, `XT`, `XN`) SHALL be modeled per the policy in `docs/country-code-policy.md` when Option A is chosen.

#### Scenario: User-assigned disputed territory filterable

- **WHEN** CIS2 entity codes are added as country records with `code_status: user_assigned`
- **THEN** consumers filtering `code_status == official_iso3166_1` exclude them

#### Scenario: Recognition metadata present

- **WHEN** a disputed-territory record is added for a CIS2 code
- **THEN** the record includes `entity_type: disputed_territory` and documented `recognition_status` or equivalent metadata
