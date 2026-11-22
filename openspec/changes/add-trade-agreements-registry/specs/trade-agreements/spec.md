## ADDED Requirements

### Requirement: Trade agreement source records

The repository SHALL keep trade agreements in `data/trade_agreements/<ID>.yaml`, one file per legal instrument, validated by `data/schemas/trade_agreements.schema.json`. Each record SHALL have `id`, `name`, `agreement_type`, `status`, `verification`, `last_verified` and a non-empty `provenance` list. `agreement_type` SHALL be one of `fta`, `customs_union`, `pta`, `services`, `digital`, `framework` or `other`. `status` SHALL be one of `proposed`, `negotiating`, `signed`, `in_force`, `terminated`, `abandoned` or `superseded`. `verification` SHALL be `official` or `catalogue`. A record SHALL have `signed` when its status is `signed`, `in_force`, `terminated`, `superseded` or `abandoned` after signature, `in_force` when its status is `in_force`, `terminated` or `superseded`, and `ended` when its status is `terminated` or `superseded`.

#### Scenario: Valid bilateral record

- **WHEN** a record `AMGE` has `agreement_type: fta`, `status: in_force`, `signed`, `in_force`, two country parties and provenance
- **THEN** validation passes

#### Scenario: Unknown status

- **WHEN** a record declares `status: ratified`
- **THEN** JSON Schema validation rejects the record

#### Scenario: In force without a date

- **WHEN** a record has `status: in_force` and no `in_force` date
- **THEN** the validator reports an error

### Requirement: Parties and intblock link

A record SHALL have either `parties` or `intblock`, not both. Each party SHALL have `id` and `type` (`country` or `intblock`), and SHALL resolve to an existing country `code` or intblock `id`. A record with exactly two parties ever SHALL NOT set `intblock`. A record whose agreement has three or more parties ever and whose status is `signed`, `in_force`, `terminated` or `superseded` SHALL set `intblock` to the intblock that holds its roster. The build SHALL derive parties of a linked record from that intblock's `includes`.

#### Scenario: Both parties and intblock

- **WHEN** a record sets `intblock: RCEP` and also lists `parties`
- **THEN** the validator reports an error

#### Scenario: Unresolved party

- **WHEN** a party has `id: XZ` and no country or intblock has that id
- **THEN** the validator reports an error

#### Scenario: Derived parties

- **WHEN** the record `RCEP` sets `intblock: RCEP`
- **THEN** `trade_agreement_parties` has one row per entry of the `RCEP` intblock's `includes`, with `joined` as `in_force` and `left` copied

#### Scenario: Multilateral agreement in force without an intblock

- **WHEN** a record in force lists three country parties and no `intblock`
- **THEN** the validator reports an error

### Requirement: Trade agreement identifiers

Registry ids SHALL be unique, uppercase, and SHALL share one namespace with intblock ids. A registry id MAY equal an intblock id only when the record's `intblock` names that id. Records moved from intblocks SHALL keep their ids, and each moved id SHALL be listed in `data/intblocks_aliases.yaml` with `reason: moved` and `target_dataset: trade_agreements`.

#### Scenario: Collision with an unrelated intblock

- **WHEN** a registry record `SAFTA` lists Australia and Singapore as parties while the intblock `SAFTA` is the South Asian Free Trade Area
- **THEN** the validator reports an id collision

#### Scenario: Moved id resolves

- **WHEN** a consumer looks up `USKR` in `intblocks_aliases`
- **THEN** it gets `reason: moved`, `target: USKR` and `target_dataset: trade_agreements`

### Requirement: Trade agreement exports

The build SHALL export a `trade_agreements` table (primary key `id`) and a `trade_agreement_parties` table (primary key `agreement_id`, `party_id`; foreign key `agreement_id` to `trade_agreements.id`) as Parquet, JSONL and DuckDB tables, listed in `contract.json` and `datapackage.json`. The enum columns SHALL be open. The DuckDB export SHALL include a view `country_trade_agreements` with one row per country and agreement, where country parties map directly and bloc parties expand to the bloc's current members with `via` set to the bloc id.

#### Scenario: Country agreements through a bloc

- **WHEN** a consumer queries `country_trade_agreements` for `country_code = 'FR'`
- **THEN** the result includes `EUJP` with `via = 'EU'`

#### Scenario: Former bloc member

- **WHEN** a consumer queries `country_trade_agreements` for `country_code = 'GB'`
- **THEN** the result does not include `EUKR`, because the United Kingdom is not a current EU member

### Requirement: Trade agreement scope

The registry SHALL record agreements, parties, status, dates, catalogue identifiers and provenance only. It SHALL NOT store trade values, tariff lines, preference margins, depth or coverage scores, or rankings, and the schema SHALL NOT define numeric trade fields.

#### Scenario: Numeric trade field rejected

- **WHEN** a record adds `trade_value_usd`
- **THEN** JSON Schema validation rejects the record

### Requirement: Catalogue-level records

Records taken only from a catalogue (WTO RTA-IS or ADB ARIC) SHALL set `verification: catalogue` and SHALL cite the catalogue row in `provenance`. Records linked to an intblock, and records moved from intblocks, SHALL set `verification: official`. The quality report SHALL count records by verification level.

#### Scenario: ARIC row imported

- **WHEN** an ARIC row with `aric_id: 2` is imported without an official source
- **THEN** the record has `verification: catalogue` and a provenance entry citing `https://aric.adb.org/fta.php?id=2`

#### Scenario: Linked record must be official

- **WHEN** a record sets `intblock: RCEP` and `verification: catalogue`
- **THEN** the validator reports an error
