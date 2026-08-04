## ADDED Requirements

### Requirement: Partof hierarchy semantic validation

Validation SHALL flag intblock records whose `partof.id` references a target classified as a treaty or agreement (`legal_status: treaty` or blocktype includes `agreement`) rather than a parent organization.

#### Scenario: EU partof EEA flagged

- **WHEN** validation runs on `economic/EU.yaml` with `partof: EEA` before correction
- **THEN** a hierarchy reversal finding is reported

#### Scenario: WHO partof UN passes

- **WHEN** validation runs on `unagency/WHO.yaml` with `partof: UN`
- **THEN** no hierarchy reversal finding is reported

### Requirement: UN specialized agency partof convention documented

`docs/intblock-inclusion-policy.md` SHALL document whether UN specialized agencies link `partof` directly to `UN` or through intermediate bodies such as `ECOSOC`.

#### Scenario: ILO convention documented

- **WHEN** a maintainer edits UN agency hierarchy
- **THEN** the policy doc states the chosen convention and lists affected agencies
