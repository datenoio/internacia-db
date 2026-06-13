## ADDED Requirements

### Requirement: Identifier alias map artifact

Each successful build SHALL emit an intblock identifier alias artifact at
`data/datasets/intblocks_aliases.json` (and a Parquet equivalent) mapping every retired or renamed
intblock id to its current id. Each entry SHALL include `alias` (retired id), `target` (current id),
`reason` (`renamed`, `merged`, or `disambiguated`), and `since` (the version that introduced the change).

#### Scenario: Alias artifact written on build

- **WHEN** `scripts/builder.py build` completes an intblocks export
- **THEN** `data/datasets/intblocks_aliases.json` exists and contains an entry for each known retired id

#### Scenario: Retired id is resolvable

- **WHEN** a consumer holds the retired id `ASF`
- **THEN** the alias artifact maps `ASF` to its current id `FSA`

### Requirement: Alias artifact in release assets

The alias artifact SHALL be published as a GitHub Release asset by the tag-triggered release workflow.

#### Scenario: Release includes alias artifact

- **WHEN** a release workflow completes for a `v*` tag
- **THEN** release assets include `intblocks_aliases.json`
