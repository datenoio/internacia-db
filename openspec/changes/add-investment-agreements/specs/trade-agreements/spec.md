## ADDED Requirements

### Requirement: Investment agreement records

The registry SHALL record standalone investment treaties with `agreement_type: investment`, in addition to the values listed in "Trade agreement source records". `investment` SHALL cover treaties whose main object is the promotion, protection or facilitation of investment:

- bilateral investment treaties, including Canada's Foreign Investment Promotion and Protection Agreements;
- investment protection agreements;
- cooperation and facilitation investment agreements;
- plurilateral investment treaties.

An agreement that also covers trade in goods or services with an investment chapter SHALL keep its FTA, PTA or services type. `services` SHALL cover services-only agreements. Investment records SHALL follow the same rules for parties, status, dates, verification and provenance as other records.

#### Scenario: Valid bilateral investment treaty

- **WHEN** a record `AMCA-BIT` has `agreement_type: investment`, `status: in_force`, `signed: '1997-05-08'`, `in_force: '1999-03-29'`, the country parties `CA` and `AM`, and provenance citing the Canada Treaty Series
- **THEN** validation passes

#### Scenario: FTA with an investment chapter

- **WHEN** an agreement covers trade in goods and services and has an investment chapter, as `CETA` does
- **THEN** its record keeps `agreement_type: fta`, and no separate `investment` record is created for the chapter

#### Scenario: Investment treaty in the country view

- **WHEN** a consumer queries `country_trade_agreements` for `country_code = 'AM'` and `agreement_type = 'investment'`
- **THEN** the result includes `AMCA-BIT`

### Requirement: Investment agreement identifiers

The id of an investment record that is not linked to an intblock SHALL end in `-BIT`, or in `-BIT-` followed by a four-digit year of signature when another investment treaty between the same parties already has the `-BIT` id. The part before the suffix SHALL follow the registry rules: the two alpha-2 codes in alphabetical order, or the bloc id first. Ids SHALL NOT be renamed when an earlier treaty is found later. A record whose id ends in `-BIT` or `-BIT-YYYY` SHALL have `agreement_type: investment`. A record linked to an intblock SHALL keep the intblock id.

#### Scenario: Investment treaty and FTA between the same parties

- **WHEN** Canada and Costa Rica have the FTA `CACR` and a FIPA
- **THEN** the FIPA has the id `CACR-BIT`, and the validator reports no id collision

#### Scenario: Missing suffix

- **WHEN** an unlinked record has `agreement_type: investment` and the id `AMCA`
- **THEN** the validator reports an error

#### Scenario: Suffix on another type

- **WHEN** a record has the id `AMCA-BIT` and `agreement_type: fta`
- **THEN** the validator reports an error

#### Scenario: Linked plurilateral treaty

- **WHEN** the record `ACIA` sets `intblock: ACIA` and `agreement_type: investment`
- **THEN** validation passes without a `-BIT` suffix

### Requirement: Suspended and replaced investment treaties

An investment treaty that a later agreement suspends or replaces SHALL have `status: superseded`, `superseded_by` naming that agreement, and `ended` set to the date of suspension or replacement. Its `notes` SHALL say whether the treaty is suspended or terminated, and SHALL record any clause that keeps it applying to existing investments. A terminated treaty SHALL have `status: terminated` and `ended` set to the date of termination, with any survival period in `notes`. A renegotiation of a treaty in force SHALL be recorded in the notes of the record in force. A new record SHALL be added only when a new instrument is signed, and it SHALL set `supersedes` once it replaces the old one.

#### Scenario: Treaty suspended by an FTA

- **WHEN** the Canada Treaty Series records the Canada–Panama FIPA as suspended on 1 April 2013, the date the Canada–Panama FTA entered into force
- **THEN** `CAPA-BIT` has `status: superseded`, `superseded_by: CAPA` and `ended: '2013-04-01'`

#### Scenario: Renegotiation of a treaty in force

- **WHEN** Global Affairs Canada lists Canada–Argentina as "In negotiations", and the Canada Treaty Series shows the 1991 FIPA in force since 29 April 1993
- **THEN** `ARCA-BIT` has `status: in_force` and `in_force: '1993-04-29'`, with the renegotiation in `notes`, and no `negotiating` record is added

### Requirement: Investment treaty parties

A treaty signed by the Belgium–Luxembourg Economic Union SHALL list the `BLEU` intblock as one party, and a treaty signed by the European Union SHALL list the `EU` intblock. `country_trade_agreements` SHALL expand these bloc parties to their current members, with `via` set to the bloc id. A party SHALL be the state that the party government or the depositary records as the current party. The original signatory SHALL be named in `notes` when a successor state is recorded.

#### Scenario: BLEU treaty expanded to Luxembourg

- **WHEN** a record `BLEUCA-BIT` lists the parties `BLEU` (intblock) and `CA`
- **THEN** `country_trade_agreements` has a row for `country_code = 'LU'` with `via = 'BLEU'`, and the quality report does not list the record as an intblock candidate

#### Scenario: Successor state

- **WHEN** the Canada Treaty Series records the 1989 FIPA as signed with the U.S.S.R., and Global Affairs Canada lists it under Russia
- **THEN** the record lists `RU` as a party, and its notes name the U.S.S.R. as the original signatory

### Requirement: Investment treaty catalogue identifier

A record MAY set `unctad_iia_id`, an integer that identifies the treaty in the UNCTAD International Investment Agreements Navigator. The value SHALL be unique across the registry. A record taken only from the UNCTAD IIA Navigator SHALL set `verification: catalogue` and SHALL cite the Navigator treaty page in `provenance`. The `trade_agreements` table SHALL export `unctad_iia_id`.

#### Scenario: Duplicate UNCTAD id

- **WHEN** two records set `unctad_iia_id: 562`
- **THEN** the validator reports an error

#### Scenario: Catalogue-only record

- **WHEN** a treaty is imported from the UNCTAD IIA Navigator without an official source
- **THEN** the record has `verification: catalogue` and a provenance entry citing its Navigator page

### Requirement: Investment agreement scope

Investment records SHALL hold the same kinds of facts as other registry records: agreements, parties, status, dates, catalogue identifiers and provenance. The schema SHALL NOT define fields for investment flows or stocks, investor–state arbitration cases, treaty-content mapping (such as fair and equitable treatment or ISDS clauses), treaty generations or scores. `notes` SHALL hold legal facts only.

#### Scenario: Arbitration count rejected

- **WHEN** a record adds `isds_cases: 4`
- **THEN** JSON Schema validation rejects the record

#### Scenario: Treaty-content field rejected

- **WHEN** a record adds `has_isds_clause: true`
- **THEN** JSON Schema validation rejects the record
