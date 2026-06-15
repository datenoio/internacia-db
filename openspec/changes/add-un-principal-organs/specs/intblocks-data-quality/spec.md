## ADDED Requirements

### Requirement: UN principal organs coverage

The intblocks dataset SHALL include records for the three principal UN organs identified as Tier 1 gaps: UN Security Council (`UNSC`), UN General Assembly (`UNGA`), and UN Human Rights Council (`UNHRC`).

#### Scenario: UNSC record exists

- **WHEN** a consumer queries intblocks by `id: UNSC`
- **THEN** a YAML source file exists with required fields and a description of the Security Council's peace-and-security mandate

#### Scenario: UNGA record exists

- **WHEN** a consumer queries intblocks by `id: UNGA`
- **THEN** a YAML source file exists representing the General Assembly as the UN's main deliberative organ

#### Scenario: UNHRC record exists

- **WHEN** a consumer queries intblocks by `id: UNHRC`
- **THEN** a YAML source file exists with membership and status reflecting the Human Rights Council

### Requirement: UN organ hierarchical linkage

UN principal organ records SHALL declare `partof: [UN]` unless a documented exception applies.

#### Scenario: Organ linked to UN

- **WHEN** `UNSC`, `UNGA`, or `UNHRC` records are added
- **THEN** each includes `partof` referencing the existing `UN` intblock id
