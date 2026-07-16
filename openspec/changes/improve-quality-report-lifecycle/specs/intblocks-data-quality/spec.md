## ADDED Requirements

### Requirement: Duplicate-link classification

The quality analyzer's duplicate-link check SHALL classify findings by link type and SHALL NOT treat country `tld` values as URLs. Expected shared domains and parent/child entity relationships SHALL be allowed, and the report SHALL distinguish "possible duplicate entity" from "shared external citation".

#### Scenario: TLD not flagged as duplicate link

- **WHEN** two country records share a top-level domain such as `.fr`
- **THEN** the analyzer does not emit a `DUPLICATE_LINK` finding derived from a `tld` pseudo-URL

#### Scenario: Shared citation classified separately from duplicate entity

- **WHEN** two distinct organizations legitimately cite the same external source URL
- **THEN** the finding is classified as a shared external citation rather than a possible duplicate entity
