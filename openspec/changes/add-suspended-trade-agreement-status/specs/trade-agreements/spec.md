## MODIFIED Requirements

### Requirement: Trade agreement source records

The repository SHALL keep trade agreements in `data/trade_agreements/<ID>.yaml`, one file per legal instrument, validated by `data/schemas/trade_agreements.schema.json`. Each record SHALL have `id`, `name`, `agreement_type`, `status`, `verification`, `last_verified` and a non-empty `provenance` list. `agreement_type` SHALL be one of `fta`, `customs_union`, `pta`, `preference_scheme`, `services`, `digital`, `framework` or `other`. `status` SHALL be one of `proposed`, `negotiating`, `suspended`, `signed`, `in_force`, `terminated`, `abandoned` or `superseded`. `suspended` SHALL mean that negotiations were launched and then suspended, paused or put on hold without being formally ended; an agreement in force whose application is suspended SHALL keep `in_force`. `verification` SHALL be `official` or `catalogue`. After a linked record reads its intblock, an agreement SHALL have `signed` when its status is `signed`, `in_force` when its status is `in_force`, `terminated` or `superseded`, and `ended` when its status is `terminated` or `superseded`; a `superseded` record SHALL name `superseded_by`. A `proposed`, `negotiating`, `suspended`, `signed` or `abandoned` agreement SHALL NOT have an `in_force` date, and a `suspended` agreement SHALL NOT have `provisional_application` either. `ended` SHALL NOT be earlier than `signed` or `in_force`; `in_force` MAY be earlier than `signed`, because an agreement can apply retroactively.

#### Scenario: Valid bilateral record

- **WHEN** a record `AMGE` has `agreement_type: fta`, `status: in_force`, `signed`, `in_force`, two country parties and provenance
- **THEN** validation passes

#### Scenario: Unknown status

- **WHEN** a record declares `status: ratified`
- **THEN** JSON Schema validation rejects the record

#### Scenario: In force without a date

- **WHEN** a record has `status: in_force` and no `in_force` date
- **THEN** the validator reports an error

#### Scenario: Retroactive entry into force

- **WHEN** a record has `signed: '1983-03-28'` and `in_force: '1983-01-01'`
- **THEN** validation passes

#### Scenario: Suspended negotiations

- **WHEN** a record `EFTATSOUZ` has `status: suspended`, no dates, seven country parties and provenance
- **THEN** validation passes
- **AND** the quality report does not list it as an intblock candidate

#### Scenario: Suspended with an entry-into-force date

- **WHEN** a record has `status: suspended` and an `in_force` date
- **THEN** the validator reports a `TRADE_AGREEMENT_STATUS_DATE` error
