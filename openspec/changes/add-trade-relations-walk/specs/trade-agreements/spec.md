## ADDED Requirements

### Requirement: UN Treaty Series registration number

A trade agreement record MAY set `unts_registration`, the registration number of the treaty in the United Nations Treaty Series (`I-<number>` for registered treaties, `II-<number>` for treaties filed and recorded). The `trade_agreements` export SHALL carry it as a nullable string column. Two records SHALL NOT share a registration number.

#### Scenario: Registration number exported

- **WHEN** a record sets `unts_registration: I-7494`
- **THEN** its `trade_agreements` row has `unts_registration = 'I-7494'`

#### Scenario: Malformed registration number

- **WHEN** a record sets `unts_registration: 7494`
- **THEN** JSON Schema validation rejects the record

### Requirement: Trade relations walk status policy

`trade_relations` records from the world walk SHALL take their status from a party government's treaty database (`verification: official`) when one lists the agreement. A record found only in the UN Treaty Series SHALL be written, at `verification: catalogue`, only when it was concluded in 2000 or later and neither party is a current member state of the European Union (whose member states' own trade agreements gave way to the common commercial policy); its status SHALL be `in_force` when the UNTS gives an entry-into-force date and `signed` otherwise, with a note that the UNTS records no termination. Older UNTS-only agreements SHALL be listed in the import report as candidates, not written.

#### Scenario: Agreement confirmed by a national database

- **WHEN** the Swiss classified compilation lists a 2011 trade and economic cooperation agreement with Tajikistan as in force, and the UNTS registers it
- **THEN** the record is `official`, `in_force`, and carries the UNTS registration number

#### Scenario: Old UNTS-only agreement

- **WHEN** the UNTS registers a 1958 trade agreement that no national database lists
- **THEN** no record is written and the import report lists it as a candidate
