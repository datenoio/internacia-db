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

For intblock `includes` entries with `type: country`, the `id` field SHALL be treated as the authoritative join key to country records. The `name` field is a source display label and MAY differ from the canonical country `name` without failing validation. Name mismatches are surfaced by the quality analyzer as `INCLUDE_NAME_MISMATCH` advisories (the standalone `report_country_include_names.py` script is retired).

#### Scenario: Name mismatch logged not failed

- **WHEN** an include has `id: TR`, `name: Türkiye`, and the country record has `name: Turkey`
- **THEN** the quality analyzer logs an `INCLUDE_NAME_MISMATCH` advisory and validation exit status is unaffected

#### Scenario: Identifier mismatch fails validation

- **WHEN** an include has `id: ZZ` and `type: country` with no matching country or allowlist entry
- **THEN** cross-dataset validation reports an unresolved reference

#### Scenario: Alias report summarizes volume

- **WHEN** the quality analyzer runs against all intblock sources
- **THEN** the `INCLUDE_NAME_MISMATCH` rule report includes the total mismatch count and per-record examples

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

### Requirement: Organizational lineage reciprocity

When record A's `successor` resolves to record B, B's `predecessor` SHALL reference A back, and vice versa. Violations SHALL be reported as `SUCCESSOR_RECIPROCITY` advisories.

#### Scenario: Missing back-reference warned

- **WHEN** `GATT` lists `successor: WTO` but `WTO` has no `predecessor`
- **THEN** validation reports a `SUCCESSOR_RECIPROCITY` advisory for the pair

#### Scenario: Reciprocal pair passes

- **WHEN** `OAU` lists `successor: AU` and `AU` lists `predecessor: OAU`
- **THEN** no `SUCCESSOR_RECIPROCITY` issue is reported

### Requirement: Suborganization and partof reciprocity

When record P lists record C in `suborganizations` and C exists, C SHALL declare P (directly or among multiple parents) in `partof`. The inverse (every `partof` child appearing in the parent's `suborganizations`) SHALL NOT be required, since large umbrella organizations do not enumerate every affiliated body. Violations SHALL be reported as `PARTOF_SUBORG_RECIPROCITY` advisories.

#### Scenario: Child missing partof warned

- **WHEN** `OECD` lists `DAC` in `suborganizations` but `DAC` has no `partof` referencing `OECD`
- **THEN** validation reports a `PARTOF_SUBORG_RECIPROCITY` advisory

#### Scenario: Unlisted child passes

- **WHEN** `DAC` declares `partof: OECD` but `OECD` does not enumerate `DAC` in `suborganizations`
- **THEN** no `PARTOF_SUBORG_RECIPROCITY` issue is reported

### Requirement: Acronym uniqueness advisory

Two or more records that share an English acronym, share at least one blocktype, and are not hierarchically or lineally related SHALL be reported as `DUPLICATE_ACRONYM` advisories, indicating a possible duplicate entity. Real-world acronym collisions SHALL be suppressed via `references.acronym_duplicate_allowlist` in `intblocks_completeness.yaml`.

#### Scenario: Colliding acronym warned

- **WHEN** two unrelated records with a shared blocktype both declare English acronym `IDB` and the acronym is not allowlisted
- **THEN** validation reports a `DUPLICATE_ACRONYM` advisory listing both records

#### Scenario: Allowlisted collision suppressed

- **WHEN** `ISA` is listed in `references.acronym_duplicate_allowlist`
- **THEN** no `DUPLICATE_ACRONYM` issue is reported for records sharing `ISA`

### Requirement: Headquarters coordinate plausibility

When `headquarters.coordinates` and `headquarters.country` are both populated and the country has a centroid, the great-circle distance between them SHALL NOT exceed the area-scaled threshold configured under `geography.hq_distance` in `intblocks_completeness.yaml`. Violations SHALL be reported as `HQ_COORDINATES_OUTSIDE_COUNTRY`, catching swapped or mis-signed coordinates.

#### Scenario: HQ coordinates in the wrong hemisphere warned

- **WHEN** a record's headquarters country is `CH` but its coordinates point to the southern Pacific
- **THEN** validation reports an `HQ_COORDINATES_OUTSIDE_COUNTRY` warning

### Requirement: Border reference resolution

Each entry in a country's `borders` list SHALL resolve to the `iso3code` of an existing country record, and SHALL NOT equal the record's own `iso3code`. Unresolved or self-referencing borders SHALL be reported as `UNRESOLVED_BORDER_REFERENCE` at IMPORTANT priority.

#### Scenario: Border resolving to existing country passes

- **WHEN** Germany's `borders` contains `FRA` and a country record with `iso3code: FRA` exists
- **THEN** border resolution reports no issue for that entry

#### Scenario: Unresolved border reported

- **WHEN** a country's `borders` contains `ZZZ` and no country record has `iso3code: ZZZ`
- **THEN** validation reports an `UNRESOLVED_BORDER_REFERENCE` issue

#### Scenario: Self-referencing border reported

- **WHEN** a country with `iso3code: DEU` lists `DEU` in its own `borders`
- **THEN** validation reports an `UNRESOLVED_BORDER_REFERENCE` issue

### Requirement: Border reciprocity advisory

When country A lists country B in `borders` but B does not list A, validation SHALL report a `NONRECIPROCAL_BORDER` advisory at MEDIUM priority, unless the pair is listed in the reciprocity allowlist in `data/schemas/countries_completeness.yaml`.

#### Scenario: Non-reciprocal border warned

- **WHEN** country A lists B's `iso3code` in `borders` and B's `borders` does not contain A's `iso3code`
- **THEN** validation reports a `NONRECIPROCAL_BORDER` issue at MEDIUM priority

#### Scenario: Allowlisted pair suppressed

- **WHEN** a non-reciprocal border pair is present in the reciprocity allowlist
- **THEN** validation reports no issue for that pair

### Requirement: Intblock organizational reference resolution

Every intblock id referenced in `predecessor`, `successor`, or `suborganizations[].id` SHALL resolve to an existing intblock `id`, a registered alias, or an entry in the `references.org_ref_allowlist` of `data/schemas/intblocks_completeness.yaml` (affiliated bodies that intentionally have no standalone record). Unresolved references SHALL be reported as `UNRESOLVED_ORG_REF` at IMPORTANT priority.

#### Scenario: Valid successor reference passes

- **WHEN** an intblock has `successor: AU` and an intblock with `id: AU` exists
- **THEN** organizational reference validation passes

#### Scenario: Unresolved suborganization reported

- **WHEN** an intblock lists a suborganization id with no matching intblock or alias
- **THEN** validation reports an `UNRESOLVED_ORG_REF` issue

#### Scenario: Allowlisted affiliated body suppressed

- **WHEN** a suborganization id is listed in `references.org_ref_allowlist`
- **THEN** validation reports no issue for that reference

### Requirement: Headquarters country resolution

An intblock's `headquarters.country` SHALL resolve to an existing `data/countries/{code}.yaml` file or an entry in `special_entity_allowlist`. Unresolved values SHALL be reported as `UNRESOLVED_HQ_COUNTRY` at IMPORTANT priority.

#### Scenario: Valid headquarters country passes

- **WHEN** an intblock has `headquarters.country: GB` and `data/countries/GB.yaml` exists
- **THEN** headquarters resolution passes

#### Scenario: Unresolved headquarters country reported

- **WHEN** an intblock has `headquarters.country: ZZ` with no matching country file or allowlist entry
- **THEN** validation reports an `UNRESOLVED_HQ_COUNTRY` issue

### Requirement: Wikidata identifier uniqueness

A `wikidata_id` value SHALL identify at most one record across the countries and intblocks datasets combined, except Q-ids listed in `references.wikidata_duplicate_allowlist` of `data/schemas/intblocks_completeness.yaml` (concept-level items intentionally shared by several records, with a documented reason). Records sharing a non-allowlisted Q-id SHALL be reported as `DUPLICATE_WIKIDATA_ID` at IMPORTANT priority.

#### Scenario: Shared Q-id reported

- **WHEN** two intblock records both declare `wikidata_id: Q123`
- **THEN** validation reports a `DUPLICATE_WIKIDATA_ID` issue naming both records

#### Scenario: Unique Q-ids pass

- **WHEN** every populated `wikidata_id` value appears on exactly one record
- **THEN** validation reports no duplicate wikidata issues

#### Scenario: Allowlisted concept-level Q-id suppressed

- **WHEN** several records share a Q-id listed in `references.wikidata_duplicate_allowlist`
- **THEN** validation reports no duplicate wikidata issue for that Q-id

### Requirement: Include display-name advisory rule

The quality analyzer SHALL report intblock `includes[].name` values that differ from the referenced country's canonical `name` as `INCLUDE_NAME_MISMATCH` at LOW priority. Because `name` is a display label per the includes contract, this rule SHALL be advisory only and SHALL NOT fail validation.

#### Scenario: Display name mismatch reported as advisory

- **WHEN** an include has `id: TR`, `name: Türkiye`, and the country record has `name: Turkey`
- **THEN** the analyzer reports an `INCLUDE_NAME_MISMATCH` issue at LOW priority and validation exit status is unaffected

### Requirement: Intblock file path stability on category move

When an intblock YAML file is moved between category directories for blocktype alignment, the record `id` SHALL remain unchanged and any required alias entries SHALL be added per identifier stability policy.

#### Scenario: Move preserves id

- **WHEN** `WTO.yaml` moves from `unagency/` to `trade/`
- **THEN** the record `id` remains `WTO` with no dangling `partof` or include references

#### Scenario: Category move does not require alias

- **WHEN** only the file path changes and `id` is unchanged
- **THEN** no alias entry is required for the move itself

