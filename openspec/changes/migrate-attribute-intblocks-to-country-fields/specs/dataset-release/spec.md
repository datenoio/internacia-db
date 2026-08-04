## ADDED Requirements

### Requirement: Attribute intblock retirement release notes

Retiring attribute-partition intblocks and adding corresponding country fields SHALL be documented as a consumer-affecting change in `CHANGELOG.md` with before/after query examples, a pointer to `attribute_intblock_migrations.json`, and an updated `migration.v*.json` (or Unreleased migration) listing countries fields added and intblock/blocktype removals.

#### Scenario: CHANGELOG shows RHTRAFFIC migration

- **WHEN** a consumer reads the CHANGELOG entry for this release
- **THEN** it shows that `RHTRAFFIC` / `LHTRAFFIC` membership queries are replaced by `car_side` filters

#### Scenario: Migration JSON lists removals

- **WHEN** `data/datasets/migration.vUnreleased.json` (or the versioned migration file for the release) is read
- **THEN** countries `added` includes the new attribute fields and intblocks/blocktypes document the retired attribute categories or ids

### Requirement: Attribute migration artifact in release assets

The exported `attribute_intblock_migrations.json` artifact SHALL be published with dataset releases alongside other consumer aids so offline users can remap retired intblock ids without cloning source YAML.

#### Scenario: Release includes attribute migration map

- **WHEN** a release workflow completes for a `v*` tag that includes this change
- **THEN** release assets include `attribute_intblock_migrations.json`
