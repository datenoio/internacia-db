## ADDED Requirements

### Requirement: EDIT walk

A registry record that matches an EDIT (Electronic Database of Investment Treaties) document SHALL keep its dates, status and verification level. It MAY gain a `treaty_text` link to the EDIT document page when EDIT has the text, and SHALL note in `notes` each date of signature, entry into force or termination where EDIT differs, citing EDIT in `provenance`. A treaty that only EDIT lists MAY be added at `verification: catalogue` with EDIT cited for every field only when EDIT gives its date of entry into force; its status SHALL be `terminated` with `ended` when EDIT gives a termination date, else `in_force`. A treaty that EDIT lists apart from an agreement that one record already covers (an investment agreement under a framework agreement, a protocol of a bloc) SHALL NOT get its own record.

#### Scenario: Record keeps UNCTAD's date

- **WHEN** UNCTAD gives 2013-06-15 and EDIT gives 2016-06-15 as the entry into force of the BLEU–Côte d'Ivoire BIT
- **THEN** `BLEUCI-BIT` keeps `in_force: '2013-06-15'`, gains a `treaty_text` link to its EDIT page, and its notes give EDIT's date

#### Scenario: EDIT-only treaty with an entry into force

- **WHEN** EDIT lists the Singapore–Taiwan BIT of 1990 with signature and entry into force on 1990-04-09, and the registry has no record of the pair
- **THEN** `SGTW-BIT` is added as `in_force` at `verification: catalogue`, citing EDIT

#### Scenario: EDIT-only treaty without an entry into force

- **WHEN** EDIT lists the Bahrain–Switzerland BIT of 2026 with no date of entry into force
- **THEN** no record is added, and the match report lists the treaty as held

#### Scenario: Investment agreement under a framework

- **WHEN** EDIT lists the ASEAN–China Investment Agreement of 2009
- **THEN** no record is added, because `ACFTA` covers the agreements under the framework agreement

### Requirement: EDIT identifiers

A trade agreement record MAY set `edit_uuid`, the uuid of its EDIT document, as a lower-case uuid string. The build SHALL export it as a nullable string column `edit_uuid` of `trade_agreements`. One `edit_uuid` MAY be set on several records only when they have the same date of signature (a treaty of a former federation that the registry records once per successor state); otherwise the validator SHALL warn.

#### Scenario: EDIT uuid exported

- **WHEN** the record `SGTW-BIT` sets `edit_uuid: fb0f5613-9129-452c-960e-0eea7fa95df0`
- **THEN** `trade_agreements` has that `edit_uuid` for `SGTW-BIT`

#### Scenario: Successor-state records

- **WHEN** `CZDE-BIT` and `DESK-BIT`, both signed on 1990-10-02, set the uuid of EDIT's Czech and Slovak Republic – Germany BIT
- **THEN** the validator reports nothing

#### Scenario: Same uuid on unrelated records

- **WHEN** two records with different dates of signature set the same `edit_uuid`
- **THEN** the validator warns on the second record
