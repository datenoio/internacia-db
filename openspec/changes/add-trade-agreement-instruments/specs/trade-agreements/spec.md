## ADDED Requirements

### Requirement: Trade agreement instruments

A trade agreement record MAY have an `instruments` list of the instruments that amend or add to the agreement among its parties. Each item SHALL have:

- `id`: matching `^[a-z0-9][a-z0-9-]*$` and unique within the record;
- `kind`: one of `amending_protocol`, `supplementary_agreement`, `early_harvest`, `joint_committee_decision`, `exchange_of_letters` or `other`;
- `name`;
- `status`: one of `negotiating`, `signed`, `in_force`, `terminated` or `abandoned`;
- a non-empty `provenance` list with the same shape as record provenance.

An item MAY have `other_names`, `signed`, `in_force`, `ended`, `coverage` (a subset of `goods`, `services` and `investment`) and `notes`, and SHALL NOT have other properties.

The date rules for items are the same as for records:

- a `signed` item SHALL have `signed`;
- an `in_force` or `terminated` item SHALL have `in_force`;
- a `terminated` item SHALL have `ended`;
- a `negotiating`, `signed` or `abandoned` item SHALL NOT have `in_force`;
- `ended` SHALL NOT be earlier than `signed` or `in_force`.

Instrument ids SHALL NOT change once published.

#### Scenario: Upgrade protocol in force

- **WHEN** the record `CNSG` has an instrument `upgrade-2018` with `kind: amending_protocol`, `status: in_force`, `signed: '2018-11-12'`, `in_force: '2019-10-16'` and provenance
- **THEN** validation passes

#### Scenario: Unknown instrument kind

- **WHEN** an instrument declares `kind: upgrade`
- **THEN** JSON Schema validation rejects the record

#### Scenario: Instrument in force without a date

- **WHEN** an instrument has `status: in_force` and no `in_force` date
- **THEN** the validator reports `TRADE_AGREEMENT_INSTRUMENT_DATE`

#### Scenario: Duplicate instrument id

- **WHEN** two instruments of the record `CNMO` have `id: supplement-10`
- **THEN** the validator reports `DUPLICATE_TRADE_AGREEMENT_INSTRUMENT`

#### Scenario: Numeric field on an instrument

- **WHEN** an instrument adds `tariff_lines_liberalized: 8000`
- **THEN** JSON Schema validation rejects the record

### Requirement: Instrument or separate record

An instrument that amends or adds to an agreement among its parties SHALL be an item of that agreement's record, not a separate record. This includes an instrument that enters into force for some parties first.

Other instruments SHALL be recorded differently:

- An agreement that replaces another SHALL be a separate record with `supersedes`.
- An agreement concluded under an umbrella treaty with its own parties SHALL be a separate record.
- The accession of a new party SHALL be recorded as party data (`parties[].in_force`, or the linked intblock's `includes[].joined`), not as an instrument.

An early harvest arrangement under an agreement that has a record SHALL be an instrument with `kind: early_harvest`. A record whose only signed instrument so far is an early harvest arrangement MAY describe that arrangement itself. When the full agreement is signed, the record SHALL take the agreement's name and dates, the arrangement SHALL become an instrument, and the record id SHALL NOT change.

#### Scenario: Early harvest before the agreement

- **WHEN** China and Nicaragua sign an early harvest arrangement in 2022 and the full FTA in 2023
- **THEN** the record `CNNI` describes the FTA and lists the arrangement as an instrument with `kind: early_harvest`, `signed: '2022-07-12'` and `in_force: '2023-05-01'`

#### Scenario: Replacing agreement

- **WHEN** a modernized agreement replaces the original one between the same parties
- **THEN** it is a separate record with `supersedes` naming the original record, and not an instrument of it

#### Scenario: Partial-scope agreement under an umbrella treaty

- **WHEN** the WTO lists a LAIA partial-scope agreement between Argentina and Uruguay as a change to the LAIA treaty
- **THEN** it is not imported as an instrument of the `ALADI` record

### Requirement: Agreement fields independent of instruments

A record's `status`, `signed`, `in_force` and `ended` SHALL describe the agreement itself. An instrument SHALL NOT change them.

The quality report SHALL list an instrument, other than an early harvest arrangement, whose `signed` date is earlier than its record's `signed` date as `TRADE_AGREEMENT_INSTRUMENT_BEFORE_AGREEMENT`, and the validator SHALL NOT fail on it.

#### Scenario: Upgrade in force

- **WHEN** the Optimization Protocol of `CNPE` enters into force on 2026-11-01
- **THEN** the record keeps `in_force: '2010-05-01'`, and the instrument has `in_force: '2026-11-01'`

#### Scenario: Instrument dated before a linked record's signature

- **WHEN** the record `ACFTA` reads `signed: '2004-11-29'` from its intblock and lists an instrument signed in 2002
- **THEN** the quality report lists `TRADE_AGREEMENT_INSTRUMENT_BEFORE_AGREEMENT`, and the validator does not fail

### Requirement: Trade agreement instruments export

The build SHALL export a `trade_agreement_instruments` table with one row per record and instrument. Its primary key SHALL be `agreement_id` and `instrument_id`, and `agreement_id` SHALL be a foreign key to `trade_agreements.id`. Its columns SHALL be:

- `agreement_id` and `instrument_id`;
- `kind`, `name`, `status`, `signed`, `in_force`, `ended`;
- `coverage`, `other_names`, `notes` and `provenance`.

The table SHALL be exported as Parquet, JSONL and a DuckDB table, and listed in `contract.json` and `datapackage.json`. `kind`, `status` and `coverage` SHALL be open enums. Adding the table SHALL be released as a MINOR change.

#### Scenario: Instruments of an agreement

- **WHEN** a consumer selects from `trade_agreement_instruments` where `agreement_id = 'CNSG'`, ordered by `signed`
- **THEN** the result lists the 2011 amending protocol, the 2018 Upgrade Protocol and the 2023 further upgrading protocol

#### Scenario: Record without instruments

- **WHEN** a record has no `instruments` list
- **THEN** `trade_agreement_instruments` has no rows for it, and its `trade_agreements` row is unchanged
