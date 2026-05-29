## MODIFIED Requirements

### Requirement: Intblock country includes resolve to country sources

Every `includes` entry in `data/intblocks/**/*.yaml` with `type: country` SHALL reference an existing `data/countries/{id}.yaml` file unless the `id` is listed in `special_entity_allowlist` in `countries_completeness.yaml`.

For allowlisted IDs without country YAML files, validation SHALL emit a **warning** (not error) until policy adds profiles or reclassifies include types.

#### Scenario: Valid country reference passes

- **WHEN** an intblock include has `id: US` and `type: country`
- **THEN** cross-dataset validation reports no error for that include

#### Scenario: Deferred CIS2 reference warns with policy note

- **WHEN** an intblock include has `id: XA`, `type: country`, and no country YAML exists
- **THEN** validation emits a warning referencing deferred policy in country-code documentation

#### Scenario: Allowlisted special entity passes without profile

- **WHEN** an include `id` is on `special_entity_allowlist` and no `data/countries/{id}.yaml` exists
- **THEN** validation does not treat the reference as an unresolved error

### Requirement: Unresolved references aggregated in report

Cross-dataset validation SHALL produce a summary count of unresolved `type: country` references grouped by `id`, distinguishing allowlisted deferred entities from unexpected gaps.

#### Scenario: Report separates deferred and unexpected ids

- **WHEN** validation runs against intblock sources
- **THEN** the summary groups deferred ids separately from unexpected missing references

### Requirement: Include name is display label only

For intblock `includes` entries with `type: country`, the `id` field SHALL be treated as the authoritative join key to country records. The `name` field is a source display label and MAY differ from the canonical country `name` without failing validation.

#### Scenario: Name mismatch logged not failed

- **WHEN** an include has `id: TR`, `name: Türkiye`, and the country record has `name: Turkey`
- **THEN** `report_country_include_names.py` logs a mismatch warning and exits with status 0

#### Scenario: Identifier mismatch fails validation

- **WHEN** an include has `id: ZZ` and `type: country` with no matching country or allowlist entry
- **THEN** cross-dataset validation reports an unresolved reference

#### Scenario: Alias report summarizes volume

- **WHEN** the alias report runs against all intblock sources
- **THEN** output includes a total count of name mismatches and top examples by frequency
