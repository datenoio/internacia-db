# trade-agreements Specification

## Purpose

Record every free trade, preferential and customs union agreement in the world, bilateral ones included, and every non-reciprocal preference scheme, as one source file per legal instrument in `data/trade_agreements/`. Each record has its parties, status, dates, catalogue identifiers (WTO RTA-IS, ADB ARIC, WTO PTA Database) and provenance. A multilateral agreement that is signed or in force keeps its roster in a linked intblock, so a roster is never stored twice. The records are exported as the `trade_agreements` and `trade_agreement_parties` tables and the `country_trade_agreements` view. These are reference data, not indicators: no trade values, tariff lines, depth scores or rankings.

## Requirements
### Requirement: Trade agreement source records

The repository SHALL keep trade agreements in `data/trade_agreements/<ID>.yaml`, one file per legal instrument, validated by `data/schemas/trade_agreements.schema.json`. Each record SHALL have `id`, `name`, `agreement_type`, `status`, `verification`, `last_verified` and a non-empty `provenance` list. `agreement_type` SHALL be one of `fta`, `customs_union`, `pta`, `preference_scheme`, `services`, `digital`, `framework` or `other`. `status` SHALL be one of `proposed`, `negotiating`, `signed`, `in_force`, `terminated`, `abandoned` or `superseded`. `verification` SHALL be `official` or `catalogue`. After a linked record reads its intblock, an agreement SHALL have `signed` when its status is `signed`, `in_force` when its status is `in_force`, `terminated` or `superseded`, and `ended` when its status is `terminated` or `superseded`; a `superseded` record SHALL name `superseded_by`. A `proposed`, `negotiating`, `signed` or `abandoned` agreement SHALL NOT have an `in_force` date. `ended` SHALL NOT be earlier than `signed` or `in_force`; `in_force` MAY be earlier than `signed`, because an agreement can apply retroactively.

#### Scenario: Valid bilateral record

- **WHEN** a record `AMGE` has `agreement_type: fta`, `status: in_force`, `signed`, `in_force`, two country parties and provenance
- **THEN** validation passes

#### Scenario: Unknown status

- **WHEN** a record declares `status: ratified`
- **THEN** JSON Schema validation rejects the record

#### Scenario: In force without a date

- **WHEN** a record has `status: in_force` and no `in_force` date
- **THEN** the validator reports an error

#### Scenario: Retroactive entry into force

- **WHEN** a record has `signed: '1983-03-28'` and `in_force: '1983-01-01'`
- **THEN** validation passes

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

### Requirement: Trade agreement identifiers

Registry ids SHALL be unique, SHALL be uppercase for new records (a linked record keeps its intblock's id, such as `AfCFTA`), and SHALL share one namespace with intblock ids and intblock aliases. A registry id MAY equal an intblock id only when the record's `intblock` names that id. Records moved from intblocks SHALL keep their ids, and each moved id SHALL be listed in `data/intblocks_aliases.yaml` with `reason: moved` and `target_dataset: trade_agreements`.

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

### Requirement: Preference scheme beneficiary history

A `verification: catalogue` preference scheme imported from the WTO Preferential Trade Arrangements Database SHALL date its beneficiaries from the database's versions. Only versions that list at least one beneficiary count; they are called populated versions here.

- **Joining.** A beneficiary listed in a populated version after the earliest one SHALL have `in_force` set to the "As of" date of the first populated version that lists it in its latest spell.
- **Baseline.** A beneficiary already listed in the earliest populated version SHALL NOT have `in_force`, unless that version is the scheme's first version.
- **Leaving.** A beneficiary missing from the latest version SHALL have `left` set to the "As of" date of the first populated version that no longer lists it.
- **Former beneficiaries.** A beneficiary that appears only in versions before the latest SHALL be a party with `role: beneficiary` and `left`, and the export SHALL mark it `former_party`.
- **Earlier spells.** Each beneficiary SHALL have one party entry. The dates of spells before the latest SHALL be written in the party's `note`.
- **Provenance and notes.** The record's `parties` provenance SHALL name the range of versions read. Its notes SHALL say that the beneficiary dates are no-later-than dates.
- **Sub-schemes.** A sub-scheme's beneficiaries SHALL be dated by the same rules, from the sub-scheme's list in each version.

#### Scenario: Beneficiary added in a later version

- **WHEN** a country is missing from the AGOA-like scheme's version of 2011-10-25 and listed in its version of 2013-06-01 and every later version
- **THEN** its party has `in_force: '2013-06-01'` and no `left`

#### Scenario: Baseline beneficiary has no start date

- **WHEN** the earliest populated version of `EU-GSP` is dated 2011-12-09, the scheme's first version is dated 1971-07-01, and a country is listed in every version from 2011-12-09
- **THEN** its party has no `in_force` and no `left`

#### Scenario: Graduated beneficiary

- **WHEN** a country is listed in the `EU-GSP` version of 2011-12-09 and not in the version of 2014-01-01 or any later one
- **THEN** `EU-GSP` lists it with `role: beneficiary` and `left: '2014-01-01'`, and `trade_agreement_parties` has the row with `status = 'former_party'`

#### Scenario: Suspended and reinstated beneficiary

- **WHEN** a country is listed from 2011-10-25, missing from 2015-01-01, and listed again from 2018-06-01 to the latest version
- **THEN** its party has `in_force: '2018-06-01'` and no `left`, and its `note` names the earlier spell from 2011-10-25 to 2015-01-01

#### Scenario: Scheme that starts in the database

- **WHEN** the earliest populated version of `GB-DCTS` is also its first version, dated 2023-06-19
- **THEN** every beneficiary in that version has `in_force: '2023-06-19'`

### Requirement: Trade agreement party dates

A party's dates SHALL lie within the agreement's dates, compared at their shared precision:

- the party's `in_force` SHALL NOT be earlier than the agreement's `in_force`;
- the party's `left` SHALL NOT be later than the agreement's `ended`;
- the party's `left` SHALL be later than the party's own `in_force`.

The validator SHALL report a violation as `TRADE_AGREEMENT_PARTY_DATE`.

#### Scenario: Party joins before the agreement starts

- **WHEN** `GB-DCTS` has `in_force: '2023-06-19'` and a party with `in_force: '2021-01-01'`
- **THEN** the validator reports `TRADE_AGREEMENT_PARTY_DATE`

#### Scenario: Party leaves after the agreement ended

- **WHEN** `US-ATPA` has `ended: '2013-07-31'` and a party with `left: '2014-01-01'`
- **THEN** the validator reports `TRADE_AGREEMENT_PARTY_DATE`

#### Scenario: Dates at different precision

- **WHEN** an agreement has `in_force: '2014'` and a party has `in_force: '2014-01-01'`
- **THEN** validation passes

### Requirement: Linked preference scheme rosters are reviewed, not rewritten

The history walk SHALL NOT edit the `includes` of an intblock that a preference scheme links (`AGOA`, `CBERA`, `CARIBCAN`, `SPARTECA`, `GSPPLUS`). It SHALL write a review report for each such scheme. The report SHALL list the `joined` and `left` dates the versions suggest, and the countries the versions list that are missing from `includes`, or the other way round.

#### Scenario: AGOA difference reported

- **WHEN** the AGOA versions list a country that the `AGOA` intblock does not include
- **THEN** the review report lists that country with its suggested dates, and `data/intblocks/pta/AGOA.yaml` is unchanged

