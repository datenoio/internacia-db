## ADDED Requirements

### Requirement: Complete intblock scope taxonomy

Every populated `scope_category` SHALL use one of six documented values: `igo`, `treaty_body`, `policy_forum`, `reference_enumeration`, `intergovernmental_body`, or `non_state_organization`. The inclusion policy SHALL define positive criteria and boundary examples for every value, and `igo` SHALL remain limited to standing intergovernmental organizations with independent institutional identity or legal personality.

#### Scenario: Independent intergovernmental organization remains IGO

- **WHEN** a record describes a standing intergovernmental organization such as IOM with an independent institutional identity
- **THEN** its `scope_category` is `igo`

#### Scenario: Subordinate commission uses intergovernmental body

- **WHEN** a record describes a permanent intergovernmental commission or committee that is an organ of another organization and lacks independent IGO status
- **THEN** its `scope_category` is `intergovernmental_body`

#### Scenario: Multilateral financing window uses intergovernmental body

- **WHEN** a record describes a standing fund or financing window governed by states but not constituted as an independent IGO
- **THEN** its `scope_category` is `intergovernmental_body`

#### Scenario: Two-fund umbrella partnership is not a member-state IGO

- **WHEN** CIF describes the enduring CTF+SCF partnership administered through separate trust funds and committees, without its own country-member roster
- **THEN** its `scope_category` is `intergovernmental_body`, its contributor countries are not member-state `includes`, and trustee/hosting roles do not create an organizational `partof` relation

#### Scenario: Continuing intergovernmental implementation platform

- **WHEN** a record names an ongoing cooperation and implementation platform such as the ESCAP Trans-Asian Railway Network, rather than the treaty that supports it
- **THEN** it uses `policy_forum` only after its country coverage is distinguished from formal membership and treaty parties

#### Scenario: International NGO uses non-state organization

- **WHEN** a record describes an international NGO, industry association, professional association, or federation not constituted by states as an IGO
- **THEN** its `scope_category` is `non_state_organization`

#### Scenario: Unknown value is rejected

- **WHEN** an intblock declares a `scope_category` outside the six documented values
- **THEN** JSON Schema validation and the intblock validator reject the record

### Requirement: Reviewed scope-category backfill manifest

Batch scope-category migration SHALL use an explicit, versioned ID-to-category manifest. The manifest SHALL declare an expected assignment count, SHALL reject duplicate or missing IDs and unknown categories, and SHALL NOT infer assignments for additional records from directory or blocktype alone.

#### Scenario: First reviewed cohort is complete

- **WHEN** the direct-backfill manifest is validated
- **THEN** it contains exactly 81 unique IDs distributed as 55 `igo`, 13 `treaty_body`, 7 `policy_forum`, and 6 `reference_enumeration`

#### Scenario: Duplicate manifest ID is rejected

- **WHEN** one intblock ID appears under more than one category
- **THEN** validation fails before any source file is modified

#### Scenario: Repository record is missing

- **WHEN** a manifest ID does not resolve to exactly one source YAML record
- **THEN** validation fails before any source file is modified

### Requirement: Safe scope-category backfill execution

The backfill CLI SHALL be non-mutating by default, SHALL expose explicit dry-run/check/apply behavior, SHALL preserve YAML formatting through surgical insertion, and SHALL never overwrite an existing different `scope_category`. The CLI SHALL validate the complete cohort before writing and SHALL abort the entire apply operation when any conflict exists.

#### Scenario: Default invocation is a dry run

- **WHEN** a maintainer invokes the backfill CLI without `--apply`
- **THEN** the CLI reports planned assignments and writes no intblock YAML

#### Scenario: Existing matching value is idempotent

- **WHEN** a manifest target already equals the record's `scope_category`
- **THEN** the CLI reports `already_set` and leaves the file byte-for-byte unchanged

#### Scenario: Existing different value blocks apply

- **WHEN** any target record contains a different non-empty `scope_category`
- **THEN** the CLI reports a conflict, exits non-zero, and writes none of the pending files

#### Scenario: Check mode detects unapplied cohort

- **WHEN** `--check` runs while reviewed assignments remain pending
- **THEN** it exits non-zero without writing files

#### Scenario: JSON report requested

- **WHEN** a maintainer provides `--report-json <path>`
- **THEN** the CLI writes assignments, actions, conflicts, and summary counts in machine-readable form

### Requirement: Staged formal-record completion

Scope-category completion SHALL be applied in reviewed cohorts with explicit warning-count acceptance targets. The first 81-record cohort SHALL reduce formal missing-category findings from 114 to 33 without changing intblock membership or identity fields.

#### Scenario: First cohort applied

- **WHEN** the approved 81-record manifest is applied and validators run
- **THEN** exactly 81 source records gain `scope_category`, `MISSING_SCOPE_CATEGORY` falls to 33, and includes/membership counts remain unchanged

#### Scenario: Source-backed cohort applied

- **WHEN** all 18 legal-status records are verified, 14 defensible existing-enum assignments are applied with field-level provenance, and ACIL/RDR/GCCPO/TAR are deferred
- **THEN** `MISSING_SCOPE_CATEGORY` falls from 33 to 19 without assigning unsupported categories to the four deferred records

#### Scenario: New-category cohort applied with accurate roster semantics

- **WHEN** twelve reviewed dependent bodies and three reviewed non-state organizations gain the new categories with field-level provenance, and false country-member links on funds, NGO associations, a GCC Secretariat office and an expert council are corrected
- **THEN** `MISSING_SCOPE_CATEGORY` falls from 19 to four (AFDF, CIF, TAR and TELESUR), without introducing orphan provenance or misrepresenting donors, beneficiaries, institutional members or parent-body countries as members

#### Scenario: Model-gap cohort applied

- **WHEN** the 15 original model-gap records and the four source-review deferrals have each received an evidence-backed entity decision under the approved taxonomy
- **THEN** formal `MISSING_SCOPE_CATEGORY` falls from 19 to 0

#### Scenario: Final four entity decisions applied

- **WHEN** AFDF's 29 State Participants replace 82 mixed member claims, CIF has no artificial country-member roster, the TAR network and its 22-party Agreement are separate records, and the out-of-scope TELESUR company is retired with a documented ID migration
- **THEN** the validator and quality analyzer report zero formal missing-category findings; the new Agreement has a distinct ID and no copied network Wikidata ID, and no alias resolves `TELESUR` to a different entity
