# cross-dataset-integrity Specification

## Purpose
TBD - created by archiving change add-countries-validation. Update Purpose after archive.
## Requirements
### Requirement: Intblock country includes resolve to country sources

Every `includes` entry in `data/intblocks/**/*.yaml` with `type: country` SHALL reference an existing `data/countries/{id}.yaml` file unless the `id` is listed in `special_entity_allowlist` in `countries_completeness.yaml`.

For allowlisted IDs without country YAML files, validation SHALL emit a **warning** (not error) until policy adds profiles or reclassifies include types. Unresolved, non-allowlisted references SHALL be reported according to the configured `unresolved_country_includes.mode` (warn or error).

#### Scenario: Valid country reference passes

- **WHEN** an intblock include has `id: US` and `type: country`
- **THEN** cross-dataset validation reports no error for that include

#### Scenario: Deferred CIS2 reference warns with policy note

- **WHEN** an intblock include has `id: XA`, `type: country`, and no country YAML exists
- **THEN** validation emits a warning referencing deferred policy in country-code documentation

#### Scenario: Allowlisted special entity passes without profile

- **WHEN** an include `id` is on `special_entity_allowlist` and no `data/countries/{id}.yaml` exists
- **THEN** validation does not treat the reference as an unresolved error

#### Scenario: Unresolved country include uses configured mode

- **WHEN** an intblock includes a country id with no matching YAML file and the id is not allowlisted
- **THEN** validation reports per the configured `unresolved_country_includes.mode`

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

### Requirement: Intblock partof reference validation

Each value in an intblock's `partof` list SHALL reference an existing intblock `id` in `data/intblocks/**/*.yaml`.

#### Scenario: Valid partof reference accepted

- **WHEN** an intblock has `partof: [UN]` and an intblock with `id: UN` exists
- **THEN** partof validation passes

#### Scenario: Invalid partof reference reported

- **WHEN** an intblock references `partof: [NONEXISTENT]` with no matching intblock id
- **THEN** validation reports a partof reference error

### Requirement: Identifier stability policy

Country `code` and intblock `id` SHALL be treated as stable join keys. When an intblock id must change
(rename, merge, or acronym reassignment), the previous id SHALL be retained as an alias in the alias
source (`data/intblocks_aliases.yaml`) with a `reason` of `renamed`, `merged`, or `disambiguated`,
rather than removed without trace.

#### Scenario: Rename records an alias

- **WHEN** an intblock id is renamed from `OLD` to `NEW`
- **THEN** an alias entry `OLD → NEW` with `reason: renamed` is added to the alias source in the same change

#### Scenario: Merge records an alias

- **WHEN** two intblock records are merged into a single id
- **THEN** the removed id is recorded as an alias pointing to the surviving id with `reason: merged`

#### Scenario: Acronym reassignment records a disambiguation alias

- **WHEN** an entity vacates an id (e.g. `ASF`) which is then reused for a different entity, and the
  original entity moves to a new id (e.g. `FSA`)
- **THEN** an alias entry `ASF → FSA` with `reason: disambiguated` is recorded, even though `ASF`
  remains a current id for the different entity

### Requirement: Alias integrity validation

Intblocks validation SHALL verify that every alias `target` resolves to an existing intblock id, that
each `reason` is one of `renamed`/`merged`/`disambiguated`, and that an alias colliding with a current
intblock id is permitted only when its `reason` is `disambiguated`.

#### Scenario: Dangling alias rejected

- **WHEN** an alias `target` references an id that does not exist in the intblocks dataset
- **THEN** validation reports an alias integrity error

#### Scenario: Unexpected alias/id collision rejected

- **WHEN** an alias id equals a current intblock id and its `reason` is not `disambiguated`
- **THEN** validation reports a collision error

#### Scenario: Disambiguation collision allowed

- **WHEN** an alias id equals a current intblock id and its `reason` is `disambiguated`
- **THEN** validation passes for that alias

