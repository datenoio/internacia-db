## ADDED Requirements

### Requirement: DTA identifiers

A trade agreement record MAY set `dta_id`, the agreement id (`WB ID`) of the World Bank Deep Trade Agreements database (DTA), as an integer of at least 1. The build SHALL export it as a nullable `int64` column `dta_id` of `trade_agreements`. `dta_id` SHALL be a catalogue identifier like `wto_rta_id`, `aric_id` and `gptad_id`: a value SHALL appear on at most one record, and the validator SHALL report a repeated value as `DUPLICATE_IDENTIFIER`. A DTA row for an accession or an EC/EU enlargement SHALL map to no record. The registry SHALL NOT store the DTA content data (policy-area coverage, legal enforceability, provision coding).

#### Scenario: DTA id exported

- **WHEN** the record `AANZFTA` sets `dta_id: 183`
- **THEN** `trade_agreements` has `dta_id = 183` for `AANZFTA`

#### Scenario: Repeated DTA id

- **WHEN** two records set `dta_id: 183`
- **THEN** the validator reports `DUPLICATE_IDENTIFIER` on the second record

#### Scenario: Agreement with a placeholder RTA ID

- **WHEN** DTA lists RCEP with `WB ID` 395 and RTA ID `999A1`
- **THEN** the record `RCEP` sets `dta_id: 395`, and its `wto_rta_id` is unchanged

#### Scenario: Accession row

- **WHEN** DTA lists `Eurasian Economic Union (EAEU) - Accession of Armenia` with `Accession?` set to `Yes`
- **THEN** no record takes its `WB ID`
