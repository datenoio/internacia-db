## ADDED Requirements

### Requirement: DESTA identifiers

A trade agreement record MAY set `desta_id`, the `number` of its base treaty in the DESTA (Design of Trade Agreements) list of treaties, as an integer of at least 1. The build SHALL export it as a nullable `int64` column `desta_id` of `trade_agreements`. `desta_id` SHALL be a catalogue identifier like `wto_rta_id`, `aric_id` and `gptad_id`: a value SHALL appear on at most one record, and the validator SHALL report a repeated value as `DUPLICATE_IDENTIFIER`. A DESTA row that is not a base treaty (an accession, withdrawal, protocol or amendment, consolidated version or negotiation) SHALL map to no record. The registry SHALL NOT store DESTA's design coding or depth indices.

#### Scenario: DESTA id exported

- **WHEN** the record `ARCR-1983` sets `desta_id: 37`
- **THEN** `trade_agreements` has `desta_id = 37` for `ARCR-1983`

#### Scenario: Repeated DESTA id

- **WHEN** two records set `desta_id: 37`
- **THEN** the validator reports `DUPLICATE_IDENTIFIER` on the second record

#### Scenario: Accession row

- **WHEN** DESTA lists `MERCOSUR Venezuela accession` with number `604+1`
- **THEN** no record takes that number, and Venezuela's dates on `MERCOSUR` come from an official source

### Requirement: Records created from DESTA

A record created because DESTA lists an agreement the registry lacks SHALL NOT take its status or dates from DESTA. Its status, its dates and any `ended` date or successor SHALL cite another source in `provenance`: a depositary, a party government, the UN Treaty Series, EUR-Lex or the WTO. An agreement without such a source SHALL NOT be added.

#### Scenario: ALADI agreement listed by DESTA

- **WHEN** DESTA lists `Argentina Costa Rica` of 1983 (number 37) and the registry has no record for AAP.A25TM 2
- **THEN** the new record `ARCR-1983` cites the ALADI record of AAP.A25TM 2 for its status and dates, and DESTA only for listing it

#### Scenario: No official source

- **WHEN** DESTA lists `Armenia Belarus` of 2000 and no official source found gives its dates
- **THEN** no record is added, and the match report lists the treaty as held
