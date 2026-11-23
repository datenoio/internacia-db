## ADDED Requirements

### Requirement: Investment and trade relations agreement types

`agreement_type` SHALL also accept `investment`, for a treaty on the promotion and protection of investment without trade-in-goods commitments, and `trade_relations`, for a bilateral agreement or treaty that grants most-favoured-nation or normal trade relations treatment without preferential tariff commitments. `services` SHALL mean an agreement on trade in services only. A record of type `investment` or `trade_relations` SHALL follow every other registry rule (parties, dates by status, verification, provenance).

#### Scenario: Investment treaty record

- **WHEN** a record `ALUS-BIT` has `agreement_type: investment`, `status: in_force`, `signed`, `in_force`, two country parties and provenance citing trade.gov
- **THEN** validation passes

#### Scenario: Unknown type rejected

- **WHEN** a record declares `agreement_type: bit`
- **THEN** JSON Schema validation rejects the record

### Requirement: Instrument suffix for investment and trade relations records

A new record of type `investment` or `trade_relations` between two parties SHALL use the sorted alpha-2 pair followed by an instrument suffix (`-BIT` for an investment treaty, `-TRA` for an agreement on trade relations, or the year of signature for an older treaty of commerce such as `-1881`), so that the bare pair id stays available for a trade agreement between the same parties.

#### Scenario: BIT id

- **WHEN** a contributor adds the 1995 Albania–United States investment treaty
- **THEN** its id is `ALUS-BIT`, not `ALUS`
