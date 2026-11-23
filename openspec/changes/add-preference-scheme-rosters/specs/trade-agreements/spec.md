## ADDED Requirements

### Requirement: Preference scheme party roles

A party of a `preference_scheme` record SHALL be a `grantor` or a `beneficiary`.

- **Records that list `parties`.** Each party SHALL set `role` to `grantor` or `beneficiary`. The record SHALL have at least one grantor. It SHALL have at least one beneficiary, unless another preference scheme names it as `parent`. A record of any other `agreement_type` SHALL NOT set `role`.
- **Linked intblocks.** A linked preference-scheme intblock SHALL use only `contributor` and `recipient` as party statuses in its `includes`. The build SHALL map `contributor` to `grantor` and `recipient` to `beneficiary`.
- **Exports.** `trade_agreement_parties` and `country_trade_agreements` SHALL have a `role` column. It SHALL be `grantor` or `beneficiary` on preference schemes and `party` on all other agreements. A bloc party that `country_trade_agreements` expands to its current members SHALL keep its role. The `role` enum SHALL be open.

#### Scenario: Missing role on a preference scheme

- **WHEN** a record `CN-LDC` has `agreement_type: preference_scheme` and a party without `role`
- **THEN** the validator reports an error

#### Scenario: Role on a reciprocal agreement

- **WHEN** a record `AMGE` has `agreement_type: fta` and a party with `role: grantor`
- **THEN** the validator reports an error

#### Scenario: Scheme without a beneficiary

- **WHEN** a record `IN-DFTP` lists only a grantor, and no other record names it as `parent`
- **THEN** the validator reports an error

#### Scenario: Linked intblock with a member status

- **WHEN** the record `SPARTECA` links the `SPARTECA` intblock, and an entry of its `includes` has `status: member`
- **THEN** the validator reports an error

#### Scenario: Grantor bloc expanded

- **WHEN** a consumer queries `country_trade_agreements` for `country_code = 'FR'` and `agreement_id = 'EU-GSP'`
- **THEN** the row has `role = 'grantor'` and `via = 'EU'`

#### Scenario: Beneficiary row

- **WHEN** a consumer queries `country_trade_agreements` for `country_code = 'BD'` and `agreement_id = 'EU-GSP'`
- **THEN** the row has `role = 'beneficiary'` and `via` NULL

#### Scenario: Reciprocal agreement row

- **WHEN** a consumer queries `trade_agreement_parties` for `agreement_id = 'EUJP'`
- **THEN** every row has `role = 'party'`

### Requirement: Preference sub-schemes

A `preference_scheme` record MAY set `parent` to the id of the preference scheme it belongs to: a framework, or a national scheme of the same grantor.

- `parent` SHALL resolve to a `preference_scheme` record.
- A chain of parents SHALL NOT form a cycle.
- A record of any other `agreement_type` SHALL NOT set `parent`.
- When the parent lists at least one beneficiary, the record's current grantors SHALL equal the parent's current grantors, and its current beneficiaries SHALL be a subset of the parent's current beneficiaries.
- The `trade_agreements` table SHALL have a `parent` column, with a foreign key to `trade_agreements.id`.

#### Scenario: Valid sub-scheme

- **WHEN** `EU-GSP-EBA` sets `parent: EU-GSP`, both records have the `EU` intblock as grantor, and every `EU-GSP-EBA` beneficiary is also a current `EU-GSP` beneficiary
- **THEN** validation passes

#### Scenario: Beneficiary outside the parent

- **WHEN** `EU-GSP-EBA` lists `VU` as a current beneficiary, and `EU-GSP` does not
- **THEN** the validator reports an error

#### Scenario: Framework parent

- **WHEN** `EAEU-GSP` sets `parent: GSP`, and the `GSP` framework lists grantors but no beneficiaries
- **THEN** validation passes, even though `GSP` lists EAEU member states and not the `EAEU` intblock

#### Scenario: Unresolved parent

- **WHEN** a record sets `parent: XX-GSP` and no record has that id
- **THEN** the validator reports an error

### Requirement: WTO PTA Database identifiers

A record MAY set `wto_pta_ids`, a list of unique positive integers. Each integer SHALL be the PTA id of a row in the WTO Preferential Trade Arrangements Database that describes the record's legal instrument. A PTA id SHALL NOT appear in more than one record. The `trade_agreements` table SHALL have a `wto_pta_ids` column, a list of integers.

#### Scenario: One instrument notified by several members

- **WHEN** `EAEU-GSP` sets `wto_pta_ids: [87, 96, 98, 100]`
- **THEN** validation passes, and `trade_agreements` has the four ids for `EAEU-GSP`

#### Scenario: PTA id used twice

- **WHEN** `AGOA` and `US-AGOA` both set `wto_pta_ids: [37]`
- **THEN** the validator reports an error

## MODIFIED Requirements

### Requirement: Parties and intblock link

A record SHALL have either `parties` or `intblock`, not both. Each party SHALL have `id` and `type` (`country` or `intblock`), SHALL resolve to an existing country `code` or intblock `id`, and SHALL appear once. A record SHALL NOT link an intblock with fewer than three party entries.

The build SHALL derive the parties of a linked record from the intblock's `includes` entries whose status makes them parties. These statuses are `member`, `founding_member`, `former_member`, `participant` and the associate statuses, and `contributor` and `recipient` on preference schemes. The build SHALL take the record's name, links and Wikidata id from the intblock, and its dates too unless the record sets them.

A signed or in-force record that lists three or more current parties and has no `intblock` SHALL be reported by the quality report as an intblock candidate. Records with `agreement_type: preference_scheme` are not reported: a non-reciprocal scheme is a set of grantor–beneficiary links, not a country group.

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

#### Scenario: Preference scheme without an intblock

- **WHEN** the record `JP-GSP` is in force, has `agreement_type: preference_scheme` and lists one grantor and 130 beneficiaries
- **THEN** the quality report does not list it as `TRADE_AGREEMENT_INTBLOCK_CANDIDATE`

#### Scenario: Linked record overrides a date

- **WHEN** the record `EAEU` links the `EAEU` intblock, whose `founded` is the entry into force, and sets `signed: '2014-05-29'`
- **THEN** `trade_agreements` has `signed = '2014-05-29'` for `EAEU`

### Requirement: Catalogue-level records

Records taken only from a catalogue (WTO RTA-IS, the WTO Preferential Trade Arrangements Database or ADB ARIC) SHALL set `verification: catalogue` and SHALL cite the catalogue row in `provenance`. When the catalogue dates its roster, as the PTA Database does with "As of" versions, the provenance `source` SHALL include that date. Records linked to an intblock, and records moved from intblocks, SHALL set `verification: official`. The quality report SHALL count records by verification level.

#### Scenario: ARIC row imported

- **WHEN** an ARIC row with `aric_id: 2` is imported without an official source
- **THEN** the record has `verification: catalogue` and a provenance entry citing `https://aric.adb.org/fta.php?id=2&ssid=3`

#### Scenario: PTA Database row imported

- **WHEN** the EU GSP row, whose latest version is dated 2017-06-29, is imported as `EU-GSP`
- **THEN** the record has `verification: catalogue`, `wto_pta_ids: [36]`, and a provenance entry citing `https://ptadb.wto.org/ptaList.aspx` whose `source` names the version date 2017-06-29

#### Scenario: Linked record must be official

- **WHEN** a record sets `intblock: RCEP` and `verification: catalogue`
- **THEN** the validator reports an error
