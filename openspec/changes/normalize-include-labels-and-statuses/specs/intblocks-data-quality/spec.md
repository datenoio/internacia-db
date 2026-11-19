## MODIFIED Requirements

### Requirement: Intblock includes contract enforcement

For each entry in `includes`, `id` SHALL be the authoritative member identifier. For `type: country` entries the exported `name` is the country's `name` (see cross-dataset-integrity); for other types `name` is a source label.

#### Scenario: Include with valid country id passes

- **WHEN** an include has `type: country` and `id: US` and `data/countries/US.yaml` exists
- **THEN** include validation passes for that entry

#### Scenario: Include with missing country id fails or warns per config

- **WHEN** an include has `type: country` and `id: ZZ` with no matching country file
- **THEN** validation reports an unresolved include per completeness config mode

## ADDED Requirements

### Requirement: Associate-tier include statuses

An `includes` entry whose organization's instrument calls the arrangement associate membership SHALL use `status: associate_member`. `status: associated` SHALL be used only for association arrangements that the instrument does not call membership. The values `associate` and `associated_observer` SHALL be listed as deprecated enum values in `contract.json` `deprecated[]` until the next MAJOR release removes them, and validation SHALL report any use as a `DEPRECATED_INCLUDE_STATUS` warning.

#### Scenario: Deprecated status reported

- **WHEN** an include has `status: associate`
- **THEN** validation reports a `DEPRECATED_INCLUDE_STATUS` warning naming `associate_member` or `associated` as replacements

#### Scenario: Deprecation is published in the contract

- **WHEN** a release is built before the MAJOR that removes the values
- **THEN** `contract.json` `deprecated[]` contains `enum_value` entries for `associate` and `associated_observer` on `memberships.status` and `intblocks.includes[].status`

#### Scenario: Associate members share one value

- **WHEN** a consumer selects `status = 'associate_member'` from `memberships` after the recoding
- **THEN** the associate members of UNESCO, IMO, FAO and CERN are all returned
