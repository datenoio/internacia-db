# countries-profile Specification

## Purpose
TBD - created by archiving change fill-countries-core-fields. Update Purpose after archive.
## Requirements
### Requirement: Structured population indicator

Every country record where a population estimate exists SHALL store `population` as a struct with at least `value` (integer), `year` (integer), and `source` (string).

#### Scenario: United States has sourced population

- **WHEN** `data/countries/US.yaml` is enriched
- **THEN** `population.value` is a positive integer, `population.year` is set, and `population.source` is non-empty

#### Scenario: Exported Parquet uses struct type

- **WHEN** the builder exports `countries.parquet`
- **THEN** the `population` column is a struct type, not a bare int64

### Requirement: Structured area indicator

Every country record where area data exists SHALL store `area` as a struct with `value` (square kilometers, float), `year`, and `source`.

#### Scenario: Area populated for sovereign state

- **WHEN** enrichment runs for `data/countries/FR.yaml`
- **THEN** `area.value` is greater than zero and includes year and source

### Requirement: Gini with sparse coverage

`gini` SHALL use the same struct shape as other indicators when present. Records without inequality data MAY omit `gini` or leave it null without failing the build if gini completeness is in warn mode. After historical backfill, maintainers SHALL incrementally lower the configured `max_null_rate` toward the report target (below 32.5% missing) in coordination with enrichment refresh governance.

#### Scenario: Gini present when World Bank reports value

- **WHEN** World Bank provides Gini for a country
- **THEN** `gini.value`, `gini.year`, and `gini.source` are populated in YAML and export

#### Scenario: Historical gini counts toward coverage

- **WHEN** only an older Gini estimate is available and enrichment adds it
- **THEN** the record counts as having `gini` populated for completeness metrics

### Requirement: Timezones for inhabited entities

Records for inhabited countries and territories SHALL have a non-empty `timezones` list with IANA timezone identifiers where applicable.

#### Scenario: US has multiple timezones

- **WHEN** enrichment runs for United States
- **THEN** `timezones` includes identifiers such as `America/New_York`

#### Scenario: Uninhabited territory marked not applicable

- **WHEN** a territory has no assigned IANA zones (e.g. Bouvet Island)
- **THEN** `timezones` is an empty list and `timezone_status` is `not_applicable`

### Requirement: Native names map

Every country record SHALL have `native_names` as a map from language key to `{official, common}` for the entity's own languages. The keys SHALL be the record's `languages[]` entries, mapped through `data/vocabs/language_codes.yaml` to ISO 639-1 (or ISO 639-3 when no ISO 639-1 code exists). `official` SHALL come from the Wikidata official name (P1448) in that language. `common` SHALL come from the Wikidata label in that language, or from the native label (P1705) when the label repeats `official`. Aliases SHALL NOT be used. Either value MAY be null, and an entry with neither SHALL be omitted. Names in languages that are not in `languages[]` belong in `other_names`, not in `native_names`. The map SHALL be empty only when `languages[]` is empty.

#### Scenario: Native names populated

- **WHEN** enrichment completes for all country sources
- **THEN** no country record has a null or missing `native_names` key at export time

#### Scenario: Official and common are not swapped

- **WHEN** enrichment builds `native_names` for Germany
- **THEN** the `de` entry has `official` "Bundesrepublik Deutschland" and `common` "Deutschland", and there is no `en` entry

#### Scenario: Aliases are excluded

- **WHEN** a Wikidata alias such as "Red China" exists for an entity
- **THEN** it does not appear in any `native_names` value

#### Scenario: Chinese uses the entity's script

- **WHEN** enrichment builds the `zh` entry for CN and for TW
- **THEN** CN uses Simplified characters (`common` 中国) and TW uses Traditional characters

#### Scenario: Key outside the entity's languages

- **WHEN** a record has a `native_names` key that is not one of its mapped `languages[]`
- **THEN** validation reports a `NATIVE_NAME_LANGUAGE` warning for that key

#### Scenario: Entity without languages

- **WHEN** a record has an empty `languages[]` (for example AQ)
- **THEN** an empty `native_names` map passes completeness, while an empty map on a record with languages fails it

### Requirement: Partial gap reduction

Enrichment SHALL reduce audit gaps for `common_names`, `wikidata_id`, and `capital_city` per the 2026-05-28 report targets.

#### Scenario: Wikidata ID filled where resolvable

- **WHEN** enrichment resolves Wikidata for a country missing `wikidata_id`
- **THEN** the YAML file contains a valid `Q` identifier matching Wikidata entity validation rules

#### Scenario: Island borders use empty list

- **WHEN** a country has no land borders
- **THEN** `borders` is `[]` rather than null or omitted

### Requirement: Strict completeness for former blocker fields

After this change, `countries_completeness.yaml` SHALL set `mode: error` for `population`, `area`, `timezones`, and `native_names`.

#### Scenario: Build fails if population still 100% null

- **WHEN** all country records lack `population` after this change is applied
- **THEN** validation fails with a completeness error

### Requirement: Documented World Bank classification gaps

Country records that World Bank does not classify SHALL be documented in project policy documentation with the list of affected ISO codes and the rationale for expected absence or alternative sourcing.

#### Scenario: Policy lists non-WB entities

- **WHEN** a maintainer reads country classification policy documentation
- **THEN** the 33 entities missing WB `region`/`incomeLevel`/`lendingType` are enumerated with sourcing guidance

### Requirement: Alternative regional classification backfill

For country records where World Bank provides no regional classification, enrichment SHALL attempt UN M49 (or equivalent documented authority) mappings for `region` and `adminregion` before leaving fields empty.

#### Scenario: High-income OECD member gets M49 region

- **WHEN** a country record lacks WB `region` but UN M49 assigns a regional code
- **THEN** `region` is populated with the M49-sourced value and provenance documents the source

#### Scenario: Genuinely unclassifiable entity documented

- **WHEN** no authoritative regional classification exists for a special territory
- **THEN** the record remains without `region` and policy documentation explains why

### Requirement: Historical Gini backfill

Where recent Gini coefficient data is unavailable, enrichment SHALL populate `gini` with the most recent published estimate when an authoritative source exists, using the standard `{value, year, source}` struct and provenance.

#### Scenario: Older Gini estimate accepted

- **WHEN** World Bank provides a Gini value older than five years for a small island state
- **THEN** `gini.year` reflects the estimate year and `gini.source` identifies the publication

### Requirement: Country centroid coordinates

Every country and territory record SHALL include a `centroid` object with `lat` (float, -90 to 90) and `lng` (float, -180 to 180) representing the geographic centroid of the entity.

#### Scenario: Sovereign state has centroid

- **WHEN** `data/countries/US.yaml` is enriched
- **THEN** `centroid.lat` and `centroid.lng` are populated with values from an authoritative geographic source

#### Scenario: All records covered

- **WHEN** enrichment completes for all 252 country sources
- **THEN** no country record lacks `centroid` at export time

#### Scenario: Exported Parquet uses struct type

- **WHEN** the builder exports `countries.parquet`
- **THEN** the `centroid` column is a struct with `lat` and `lng` fields

#### Scenario: Invalid coordinates rejected

- **WHEN** a country record has `centroid.lat` outside -90..90 or `centroid.lng` outside -180..180
- **THEN** validation reports a coordinate range error

### Requirement: Centroid provenance

Centroid values populated from external sources SHALL include a `provenance` entry with `field: centroid`, `source`, and `retrieved_at`.

#### Scenario: Natural Earth sourcing documented

- **WHEN** centroid is imported from Natural Earth
- **THEN** the country record's provenance lists the Natural Earth source and retrieval date

### Requirement: Country crosswalk identifiers

Country records MAY include optional crosswalk identifier fields `geonames_id` (integer), `ioc_code` (string), `fifa_code` (string), and `fips_code` (string) declared in `countries.schema.json`. When present, each field SHALL include provenance citing the authoritative source.

#### Scenario: Schema accepts geonames_id

- **WHEN** a country YAML record includes `geonames_id: 2921044`
- **THEN** validation passes against the updated schema

#### Scenario: Crosswalk documented for integrators

- **WHEN** a consumer reads `docs/ai-consumers.md`
- **THEN** they find join guidance for each crosswalk field and known null cases on non-standard codes

### Requirement: Crosswalk backfill for ISO records

Official ISO 3166-1 country records (`code_status: official_iso3166_1`) SHALL be backfilled with crosswalk identifiers where an authoritative mapping exists, targeting high coverage on `geonames_id`, `ioc_code`, and `fifa_code`.

#### Scenario: Major sovereign state has geonames_id

- **WHEN** a consumer reads `data/countries/US.yaml` after backfill
- **THEN** `geonames_id` is populated with a Wikidata- or GeoNames-sourced value and provenance

### Requirement: Country writing direction attributes

Country records SHALL represent dominant writing direction(s) on the country record via optional `writing_directions`, an array of objects with required `id` (controlled vocab) and optional `primary` (boolean). Values SHALL resolve against the writing-directions vocab catalog. This field replaces inverted `writingdirection` intblock membership.

#### Scenario: Japan has horizontal and vertical directions

- **WHEN** Japan’s country record is migrated from writingdirection intblocks
- **THEN** `writing_directions` includes vocab ids for left-to-right and top-to-bottom, with one marked `primary: true` when a primary convention is known

#### Scenario: Single-direction country

- **WHEN** a country appears only in the LTR writingdirection intblock at migration time
- **THEN** `writing_directions` contains a single entry with id `ltr`

### Requirement: Country writing system attributes

Country records SHALL represent official or widely used writing system(s) via optional `writing_systems`, an array of objects with required `id` and optional `primary`. Values SHALL resolve against the writing-systems vocab catalog. This field replaces inverted `writingsystem` intblock membership.

#### Scenario: Israel lists Hebrew and Arabic scripts

- **WHEN** Israel’s record is migrated from writingsystem intblocks
- **THEN** `writing_systems` includes both `hebrew` and `arabic` vocab ids

### Requirement: Country DVD region attribute

Country records SHALL store commercial DVD region as optional `dvd_region`, an integer in the closed range 1–6 when assigned. Absence MUST mean unknown or unassigned. This field replaces inverted `dvdregion` intblock membership.

#### Scenario: United States is DVD region 1

- **WHEN** the United States record is migrated from `DVD_1`
- **THEN** `dvd_region` is `1`

#### Scenario: Unassigned territory omits field

- **WHEN** a territory was not present in any dvdregion includes roster and no authoritative assignment is applied
- **THEN** `dvd_region` is omitted or null and validation does not fail in warn-mode completeness

### Requirement: Country broadcast system attributes

Country records SHALL represent terrestrial/digital television system(s) via optional `broadcast_systems`, an array of objects with required `id` resolving against the broadcast-systems vocab. This field replaces inverted `teleregion` intblock membership.

#### Scenario: United States lists ATSC and NTSC

- **WHEN** the United States record is migrated from teleregion intblocks
- **THEN** `broadcast_systems` includes vocab ids corresponding to former `ATSC` and `NTSC` intblocks

### Requirement: Country legal system attributes

Country records SHALL represent legal tradition(s) via optional `legal_systems`, an array of objects with required `id` resolving against the legal-systems vocab. This field replaces inverted `lawsystem` intblock membership. Government form / regime typology SHALL NOT be added under this requirement.

#### Scenario: Mixed jurisdiction lists multiple systems

- **WHEN** Cameroon appears in multiple lawsystem intblocks at migration
- **THEN** `legal_systems` contains multiple vocab ids reflecting those memberships

#### Scenario: Government form excluded

- **WHEN** this change is applied
- **THEN** country schema does not gain a `government_form` or `govform` field

### Requirement: Country rail gauge attributes

Country records SHALL represent railway track gauge(s) in use via optional `rail_gauges`, an array of objects with required `id`, optional `gauge_mm` (positive number), and optional `primary`. Ids SHALL resolve against the rail-gauges vocab. This field replaces inverted `railgauge` intblock membership.

#### Scenario: Russian-gauge countries retain millimeter metadata

- **WHEN** a country migrated from `RUGAUGE` has vocab id `russian`
- **THEN** the entry includes `gauge_mm: 1520` when the vocab or migration mapping supplies it

### Requirement: Driving side remains country-owned

`car_side` (`left` | `right`) SHALL remain the sole source of truth for traffic-hand / driving-side classification. After migration, no `traffichand` intblock SHALL exist, and consumers SHALL NOT need intblock joins for this attribute.

#### Scenario: Left-hand traffic country

- **WHEN** a consumer queries countries that drive on the left
- **THEN** they filter `car_side = 'left'` and do not join intblocks

#### Scenario: Traffichand retired

- **WHEN** the attribute intblock retirement completes
- **THEN** `data/intblocks/traffichand/` no longer exists

