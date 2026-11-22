## ADDED Requirements

### Requirement: Composite currency blocktype deprecation

`contract.json` SHALL list `eccurr` and `cuscurr` under `deprecated` as `enum_value` entries for `intblocks.blocktype`, with replacements `[economic, currency]` and `[customs, currency]` and `removal: next MAJOR`. Both values SHALL be removed from records and from the taxonomy only in a MAJOR release, and `CHANGELOG.md` SHALL give the replacement queries.

#### Scenario: Deprecation listed in the contract

- **WHEN** `scripts/builder.py build` runs with `eccurr` and `cuscurr` marked deprecated
- **THEN** `contract.json` `deprecated` contains an entry for each value with its replacements and `removal: next MAJOR`

#### Scenario: Query unchanged during the deprecation window

- **WHEN** a consumer runs `list_contains(blocktype, 'cuscurr')` on the MINOR release that deprecates it
- **THEN** the query returns `CEMAC` and `UEMOA`, the same IDs as on the release before

#### Scenario: Replacement query after removal

- **WHEN** a release removes `cuscurr`
- **THEN** the release is MAJOR and `CHANGELOG.md` gives `list_has_all(blocktype, ['customs', 'currency'])` as the replacement query
