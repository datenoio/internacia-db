## ADDED Requirements

### Requirement: Formal intblock scope-category completeness gate

Every intblock with `status: formal` SHALL declare a valid `scope_category` after the approved backfill reaches zero formal omissions. During the staged migration the existing warning SHALL remain non-blocking; the validator and quality analyzer SHALL promote the condition to an error only after all formal records are classified.

#### Scenario: Migration still has pending formal records

- **WHEN** an approved migration cohort remains unapplied and a formal record lacks `scope_category`
- **THEN** the validator reports `MISSING_SCOPE_CATEGORY` as a warning and the quality analyzer reports the same finding

#### Scenario: Migration reaches zero

- **WHEN** all formal records have a valid `scope_category` and the strict gate is enabled
- **THEN** validators and quality analysis report zero `MISSING_SCOPE_CATEGORY` findings

#### Scenario: Formal omission regresses after strict gate

- **WHEN** a formal record loses `scope_category` after the strict gate is enabled
- **THEN** validation fails with `MISSING_SCOPE_CATEGORY` in both the CLI validator and quality analyzer

#### Scenario: Non-formal backlog remains visible but non-blocking

- **WHEN** an informal, historical, or de-facto record lacks `scope_category` during this change
- **THEN** the formal-record error gate does not fail solely because of that record, and the remaining backlog is tracked separately

### Requirement: Scope-category semantic safeguards

Validation SHALL enforce semantic rules only for categories with documented deterministic evidence and SHALL use explicit exceptions for mixed blocktypes. Directory membership alone SHALL NOT be sufficient to mutate or validate a category for mixed directories such as `food`, `fund`, `project`, `customs`, or `telecom`.

#### Scenario: World Bank grouping remains a reference enumeration

- **WHEN** an intblock has blocktype `wbgroup`
- **THEN** validation requires `scope_category: reference_enumeration`

#### Scenario: Non-state legal form is labeled IGO

- **WHEN** a record with a confirmed NGO, private federation, or industry-association legal form declares `scope_category: igo`
- **THEN** validation reports a semantic mismatch unless the record is present in a reviewed exception allowlist

#### Scenario: Mixed directory contains different categories

- **WHEN** two records in the same mixed directory have different evidenced entity forms
- **THEN** validation accepts their different categories and does not enforce a directory-wide category
