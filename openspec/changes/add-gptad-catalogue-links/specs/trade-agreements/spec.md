## ADDED Requirements

### Requirement: GPTAD identifiers

A trade agreement record MAY set `gptad_id`, the agreement id of the World Bank Global Preferential Trade Agreements Database (GPTAD), as an integer of at least 1. The build SHALL export it as a nullable `int64` column `gptad_id` of `trade_agreements`. Each catalogue identifier (`wto_rta_id`, `aric_id`, `gptad_id`) SHALL appear on at most one record, and the validator SHALL report a repeated value as `DUPLICATE_IDENTIFIER`. A GPTAD agreement that duplicates another GPTAD agreement for the same instrument SHALL map to no record.

#### Scenario: GPTAD id exported

- **WHEN** the record `AFIN` sets `gptad_id: 459`
- **THEN** `trade_agreements` has `gptad_id = 459` for `AFIN`

#### Scenario: Repeated catalogue identifier

- **WHEN** two records set `gptad_id: 459`
- **THEN** the validator reports `DUPLICATE_IDENTIFIER` on the second record

### Requirement: Treaty text links

`links[].type` SHALL accept `treaty_text`: a URL of the full text of the agreement, published by a depositary, a party government or a catalogue (such as a GPTAD PDF). The registry SHALL store the URL and SHALL NOT store the text.

#### Scenario: GPTAD text link

- **WHEN** a record lists `{url: 'https://wits.worldbank.org/GPTAD/PDF/archive/Afghanistan-India.pdf', type: treaty_text}`
- **THEN** the record validates and the exported `links` hold that entry

## MODIFIED Requirements

### Requirement: Parties and intblock link

A record SHALL have either `parties` or `intblock`, not both. Each party SHALL have `id` and `type` (`country` or `intblock`), SHALL resolve to an existing country `code` or intblock `id`, and SHALL appear once. A record SHALL NOT link an intblock with fewer than three party entries. The build SHALL derive the parties of a linked record from that intblock's `includes` entries whose status makes them parties (`member`, `founding_member`, `former_member`, `participant`, the associate statuses, and `contributor` and `recipient` on preference schemes), and SHALL take the record's name and Wikidata id from the intblock, its links from the intblock followed by the record's own `links` (a URL listed once), and its dates unless the record sets them. A signed or in-force record that lists three or more current parties and has no `intblock` SHALL be reported by the quality report as an intblock candidate.

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
- **THEN** the quality report lists it as `TRADE_AGREEMENT_INTBLOCK_CANDIDATE`, and the validator does not fail

#### Scenario: Linked record overrides a date

- **WHEN** the record `EAEU` links the `EAEU` intblock, whose `founded` is the entry into force, and sets `signed: '2014-05-29'`
- **THEN** `trade_agreements` has `signed = '2014-05-29'` for `EAEU`

#### Scenario: Linked record adds a text link

- **WHEN** the record `SAFTA` links the `SAFTA` intblock and lists a `treaty_text` link
- **THEN** the exported `links` of `SAFTA` hold the intblock's links followed by the `treaty_text` link

### Requirement: Catalogue-level records

Records taken only from a catalogue (WTO RTA-IS, ADB ARIC or GPTAD) SHALL set `verification: catalogue` and SHALL cite the catalogue row in `provenance`. Records linked to an intblock, and records moved from intblocks, SHALL set `verification: official`. The quality report SHALL count records by verification level. A record created from GPTAD SHALL NOT take its status from GPTAD alone, because GPTAD statuses date from around 2010: the status, and any `ended` date and successor, SHALL cite another source in `provenance`.

#### Scenario: ARIC row imported

- **WHEN** an ARIC row with `aric_id: 2` is imported without an official source
- **THEN** the record has `verification: catalogue` and a provenance entry citing `https://aric.adb.org/fta.php?id=2&ssid=3`

#### Scenario: Linked record must be official

- **WHEN** a record sets `intblock: RCEP` and `verification: catalogue`
- **THEN** the validator reports an error

#### Scenario: GPTAD agreement missing from the registry

- **WHEN** the GPTAD agreement Croatia - Lithuania (`gptad_id: 463`) has no registry record
- **THEN** the new record has `verification: catalogue`, a provenance entry citing the GPTAD text for its parties, and a provenance entry citing another source for its status
