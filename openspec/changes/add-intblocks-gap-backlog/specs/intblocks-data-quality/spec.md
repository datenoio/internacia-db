## ADDED Requirements

### Requirement: Intblocks gap backlog tracking

Deferred intblock candidates from gap analysis SHALL be tracked in `dev/research/backlog.md` with status, rationale, and sourcing requirements.

#### Scenario: Backlog lists deferred candidates

- **WHEN** a maintainer opens `dev/research/backlog.md`
- **THEN** each candidate from the gap analysis **Still Deferred** section appears with a documented status

#### Scenario: Shipped item updated

- **WHEN** a deferred candidate is added to the dataset
- **THEN** backlog status changes to `shipped` with reference to the YAML file path

### Requirement: Historical entity modeling consistency

Intblock records representing dissolved or historical organizations SHALL use consistent `status`, `dissolved`, and optional `predecessor`/`successor` fields per documented taxonomy.

#### Scenario: Historical alliance modeled consistently

- **WHEN** a historical military alliance record is added from the backlog
- **THEN** it includes `dissolved` date and `status` indicating historical status

### Requirement: Initiative scope exclusion criteria

Candidates classified as initiatives or programs without fixed membership SHALL be documented as `excluded` with rationale rather than added as intblocks.

#### Scenario: Initiative excluded with rationale

- **WHEN** a candidate is determined to be a program without stable membership
- **THEN** backlog marks it `excluded` with a documented reason
