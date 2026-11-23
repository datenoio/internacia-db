## ADDED Requirements

### Requirement: UNCTAD IIA Navigator identifier

A trade agreement record MAY set `unctad_iia_id`, the integer treaty identifier of the UNCTAD Investment Policy Hub IIA Navigator. The `trade_agreements` export SHALL carry it as a nullable integer column. Two records SHALL NOT share an `unctad_iia_id`.

#### Scenario: BIT mapped to UNCTAD

- **WHEN** the record `RWUS-BIT` sets `unctad_iia_id: 2870`
- **THEN** the `trade_agreements` row for `RWUS-BIT` has `unctad_iia_id = 2870`

#### Scenario: Duplicate identifier

- **WHEN** two records set `unctad_iia_id: 2870`
- **THEN** the validator reports an error

### Requirement: UNCTAD catalogue records

Records taken only from the UNCTAD IIA Navigator SHALL set `verification: catalogue` and SHALL cite the treaty page in `provenance`. A record that a party government or the treaty text confirms stays `official` and only gains `unctad_iia_id`. When one pair of parties has more than one bilateral investment treaty, each record of that pair SHALL take the id `<pair>-BIT-<year of signature>`; a pair with one treaty keeps `<pair>-BIT`.

#### Scenario: Catalogue BIT

- **WHEN** a BIT row from the IIA Navigator matches no existing record
- **THEN** a new record with `agreement_type: investment`, `verification: catalogue`, `unctad_iia_id` and a provenance entry citing the treaty page is written

#### Scenario: Pair with two treaties

- **WHEN** the IIA Navigator lists a 1975 and a 2008 BIT between the same two parties
- **THEN** the records are `<pair>-BIT-1975` and `<pair>-BIT-2008`
