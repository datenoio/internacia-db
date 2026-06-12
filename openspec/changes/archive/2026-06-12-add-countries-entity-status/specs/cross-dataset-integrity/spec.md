## MODIFIED Requirements

### Requirement: Intblock country includes resolve to country sources

Every `includes` entry in `data/intblocks/**/*.yaml` with `type: country` SHALL reference an existing `data/countries/{id}.yaml` file unless the `id` is listed in `special_entity_allowlist` in `countries_completeness.yaml`.

For allowlisted IDs without country YAML files, validation SHALL emit a **warning** (not error) until a policy change adds profiles or reclassifies the include type. Deferred IDs `XA`, `XS`, `XT`, `XN` remain warn-only with documented rationale in `docs/country-code-policy.md`.

#### Scenario: Valid country reference passes

- **WHEN** an intblock include has `id: US` and `type: country`
- **THEN** cross-dataset validation reports no error for that include

#### Scenario: Deferred CIS2 reference warns with policy note

- **WHEN** an intblock include has `id: XA`, `type: country`, and no country YAML exists
- **THEN** validation emits a warning referencing deferred policy in country-code documentation

#### Scenario: Allowlisted special entity passes without profile

- **WHEN** an include `id` is on `special_entity_allowlist` and no `data/countries/{id}.yaml` exists
- **THEN** validation does not treat the reference as an unresolved error

#### Scenario: Unallowlisted missing reference fails when configured

- **WHEN** completeness config sets `unresolved_country_includes.mode: error` and an unallowlisted missing reference exists
- **THEN** validation fails (default remains warn until policy is decided)

### Requirement: Unresolved references aggregated in report

Cross-dataset validation SHALL produce a summary count of unresolved `type: country` references grouped by `id`, distinguishing allowlisted deferred entities from unexpected gaps.

#### Scenario: Report separates deferred and unexpected ids

- **WHEN** validation runs against intblock sources
- **THEN** the summary groups `XA`, `XS`, `XT`, `XN` under a deferred-policy section when not allowlisted
