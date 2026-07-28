## ADDED Requirements

### Requirement: Intblock file path stability on category move

When an intblock YAML file is moved between category directories for blocktype alignment, the record `id` SHALL remain unchanged and any required alias entries SHALL be added per identifier stability policy.

#### Scenario: Move preserves id

- **WHEN** `WTO.yaml` moves from `unagency/` to `trade/`
- **THEN** the record `id` remains `WTO` with no dangling `partof` or include references

#### Scenario: Category move does not require alias

- **WHEN** only the file path changes and `id` is unchanged
- **THEN** no alias entry is required for the move itself
