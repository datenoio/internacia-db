## ADDED Requirements

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

## MODIFIED Requirements

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
