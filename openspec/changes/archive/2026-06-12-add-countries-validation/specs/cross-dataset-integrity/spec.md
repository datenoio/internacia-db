## ADDED Requirements

### Requirement: Intblock country includes resolve to country sources

Every `includes` entry in `data/intblocks/**/*.yaml` with `type: country` SHALL reference an existing `data/countries/{id}.yaml` file unless the `id` is listed in `special_entity_allowlist` in `countries_completeness.yaml`.

#### Scenario: Valid country reference passes

- **WHEN** an intblock include has `id: US` and `type: country`
- **THEN** cross-dataset validation reports no error for that include

#### Scenario: Missing country reference warns

- **WHEN** an intblock include has `id: XA`, `type: country`, and no `data/countries/XA.yaml` exists
- **THEN** validation emits a warning identifying the unresolved reference and source file

#### Scenario: Allowlisted special entity passes

- **WHEN** an include `id` is listed in `special_entity_allowlist`
- **THEN** cross-dataset validation does not report an unresolved reference for that id

### Requirement: Unresolved references aggregated in report

Cross-dataset validation SHALL produce a summary count of unresolved `type: country` references grouped by `id`.

#### Scenario: CIS2 unresolved members summarized

- **WHEN** validation runs against current intblock sources
- **THEN** the report lists `XA`, `XS`, `XT`, `XN` as unresolved (warn) unless allowlisted
