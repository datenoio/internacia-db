## ADDED Requirements

### Requirement: Deprecated blocktype values in the contract

A blocktype marked `deprecated` in `data/blocktypes/blocktypes.yaml` SHALL be listed under `deprecated` in `contract.json` with `kind: enum_value`, `table: intblocks`, `column: blocktype`, the blocktype `value`, its `replacements` and its `removal`. The blocktype SHALL stay on its baseline records until the next MAJOR release. It SHALL be removed from records and from the taxonomy only in a MAJOR release, with migration SQL in `CHANGELOG.md`.

#### Scenario: Deprecation listed in the contract

- **WHEN** `scripts/builder.py build` runs with `intorg` marked deprecated
- **THEN** `contract.json` `deprecated` contains an entry for `intblocks.blocktype` value `intorg` with `removal: next MAJOR`

#### Scenario: Query unchanged during the deprecation window

- **WHEN** a consumer runs `list_contains(blocktype, 'intorg')` on a MINOR release that deprecated `intorg`
- **THEN** the query returns the same record IDs as on the release before the deprecation

#### Scenario: Removal only in a MAJOR release

- **WHEN** a release removes `intorg` from records or from the taxonomy
- **THEN** the release is MAJOR, an earlier MINOR release listed `intorg` under `deprecated`, and `CHANGELOG.md` gives the replacement query `scope_category = 'igo'`
