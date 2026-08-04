## ADDED Requirements

### Requirement: Schema migration diff artifacts

When a release build detects a change in `schema_hash` compared to the previous semver release, the build SHALL emit `data/datasets/migration.vX.Y.Z.json` listing field-level schema changes per dataset (added, removed, renamed, type-changed).

#### Scenario: Breaking field change documented

- **WHEN** a release removes or renames a top-level country field
- **THEN** the migration JSON for that version lists the change with old and new names

#### Scenario: Patch release without schema change

- **WHEN** schema_hash is unchanged between releases
- **THEN** no migration file is required or an empty migration document states no schema changes
