## ADDED Requirements

### Requirement: Provisional application

A trade agreement record and each of its parties MAY have `provisional_application`, the date from which at least two parties, or that party, applied the agreement provisionally. `in_force` SHALL mean the definitive entry into force. A record whose agreement applies only provisionally SHALL keep `status: in_force` and MAY leave out `in_force`. After a linked record reads its intblock, a record with `status` `in_force`, `terminated` or `superseded` SHALL have `in_force` or `provisional_application`. A `proposed`, `negotiating`, `signed` or `abandoned` record SHALL NOT have `provisional_application`. `ended` SHALL NOT be earlier than `provisional_application`. A linked record that sets `provisional_application` SHALL take `in_force` only from itself. The `trade_agreements`, `trade_agreement_parties` and `country_trade_agreements` exports SHALL carry a nullable `provisional_application` column, and `trade_agreement_parties.joined` SHALL be the earlier of the party's provisional application and entry into force, else its signature.

#### Scenario: Applied provisionally only

- **WHEN** a record has `status: in_force`, `provisional_application: '2021-01-01'` and no `in_force`
- **THEN** validation passes and the exported row has an empty `in_force` and `provisional_application = '2021-01-01'`

#### Scenario: Provisional date on a signed agreement

- **WHEN** a record has `status: signed` and `provisional_application: '2024-01-01'`
- **THEN** the validator reports a `TRADE_AGREEMENT_STATUS_DATE` error

#### Scenario: Party applied before entry into force

- **WHEN** a party has `provisional_application: '2021-12-01'` and `in_force: '2022-09-01'`
- **THEN** its `trade_agreement_parties` row has `joined = '2021-12-01'`

#### Scenario: Linked record applied provisionally

- **WHEN** a record linked to an intblock whose `active_period.start` is `2021-01-01` sets `provisional_application: '2021-01-01'` and no `in_force`
- **THEN** the exported `in_force` is empty
