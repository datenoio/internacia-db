## ADDED Requirements

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
