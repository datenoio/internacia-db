## ADDED Requirements

### Requirement: Country alias artifact in release

GitHub Release assets and committed `data/datasets/` artifacts SHALL include `countries_aliases.json` when any country code alias is defined.

#### Scenario: Alias ships with release

- **WHEN** a semver release build completes after the Kosovo rename
- **THEN** `countries_aliases.json` is present in release assets alongside countries Parquet and DuckDB
