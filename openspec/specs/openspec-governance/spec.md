# openspec-governance Specification

## Purpose
TBD - created by archiving change archive-completed-openspec-changes. Update Purpose after archive.
## Requirements
### Requirement: Canonical OpenSpec capabilities for countries domain

Implemented countries-domain capabilities SHALL be recorded in `openspec/specs/` after archival of completed change proposals.

#### Scenario: Specs directory populated

- **WHEN** archival of the four v1.2.0 countries changes completes
- **THEN** `openspec/specs/` contains at minimum capabilities for countries data quality, countries build, countries profile, countries entity model, cross-dataset integrity, and dataset release

#### Scenario: Active changes list excludes archived items

- **WHEN** a developer runs `openspec list`
- **THEN** archived countries changes no longer appear as active proposals

### Requirement: Strict validation after archival

The repository SHALL pass `openspec validate --strict` after promoting archived changes to specs.

#### Scenario: Post-archive validation passes

- **WHEN** archival completes
- **THEN** `openspec validate --strict` exits successfully

