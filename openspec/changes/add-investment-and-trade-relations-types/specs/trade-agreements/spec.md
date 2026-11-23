## ADDED Requirements

### Requirement: Trade relations agreement type

`agreement_type` SHALL also accept `trade_relations`, for a bilateral agreement or treaty that grants most-favoured-nation or normal trade relations treatment without preferential tariff commitments. A `trade_relations` record SHALL follow every other registry rule (parties, dates by status, verification, provenance).

#### Scenario: Trade relations record

- **WHEN** a record `AMUS-TRA` has `agreement_type: trade_relations`, `status: in_force`, `signed`, `in_force`, two country parties and provenance citing Treaties in Force
- **THEN** validation passes

#### Scenario: Unknown type rejected

- **WHEN** a record declares `agreement_type: mfn`
- **THEN** JSON Schema validation rejects the record

### Requirement: Instrument suffix for trade relations records

A new `trade_relations` record between two parties SHALL use the sorted alpha-2 pair followed by `-TRA`, or by the year of signature for an older treaty of commerce (`-1881`), so that the bare pair id stays available for a trade agreement between the same parties.

#### Scenario: Trade relations id

- **WHEN** a contributor adds the 1992 Armenia–United States agreement on trade relations
- **THEN** its id is `AMUS-TRA`, not `AMUS`
