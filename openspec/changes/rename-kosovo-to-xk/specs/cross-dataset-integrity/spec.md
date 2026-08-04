## ADDED Requirements

### Requirement: Country code alias map

The build SHALL emit `data/datasets/countries_aliases.json` documenting retired or renamed country alpha-2 codes mapped to their current primary code, using the same structural pattern as `intblocks_aliases.json`.

#### Scenario: Kosovo alias present after rename

- **WHEN** a consumer reads `countries_aliases.json` after the KV→XK rename
- **THEN** an entry maps `KV` to `XK` with a documented reason

#### Scenario: Intblock includes use current country codes

- **WHEN** validation runs after the rename
- **THEN** no intblock `includes[].id` references a retired country code without a matching alias entry
