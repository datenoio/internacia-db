## ADDED Requirements

### Requirement: Attribute intblock migration artifact

The repository SHALL maintain `data/attribute_intblock_migrations.yaml` as the source of truth for retired attribute-partition intblock ids. Each entry SHALL include `retired_id`, `country_field`, a value locator (`country_value` for scalars or `country_value_id` for list-member ids), and `since` (semver). The build SHALL export `data/datasets/attribute_intblock_migrations.json`. These retirements SHALL NOT be recorded as ordinary intblock aliases whose `target` must resolve to a live intblock id.

#### Scenario: RHTRAFFIC maps to car_side

- **WHEN** a consumer looks up retired id `RHTRAFFIC` in the migration artifact
- **THEN** the entry points at country field `car_side` with value `right`

#### Scenario: DVD_1 maps to dvd_region

- **WHEN** a consumer looks up retired id `DVD_1`
- **THEN** the entry points at `dvd_region` with value `1`

#### Scenario: Not mixed into intblock alias targets

- **WHEN** alias integrity validation runs
- **THEN** attribute retirements are validated via the migration artifact rules and are not required to appear as `intblocks_aliases.yaml` targets

### Requirement: Attribute migration artifact integrity

Validation SHALL verify that every `retired_id` in the migration artifact does not exist as a current intblock id, that `country_field` is one of the documented migrated fields (`car_side`, `writing_directions`, `writing_systems`, `dvd_region`, `broadcast_systems`, `legal_systems`, `rail_gauges`), and that scalar/list values are consistent with country schema and vocab catalogs.

#### Scenario: Dangling retirement rejected

- **WHEN** the migration artifact lists `retired_id: RHTRAFFIC` but `RHTRAFFIC.yaml` still exists under intblocks
- **THEN** validation reports a migration integrity error

#### Scenario: Unknown country field rejected

- **WHEN** an entry sets `country_field: hdi`
- **THEN** validation reports an unsupported-field error

## MODIFIED Requirements

### Requirement: Identifier stability policy

Country `code` and intblock `id` SHALL be treated as stable join keys. When an intblock id must change (rename, merge, or acronym reassignment), the previous id SHALL be retained as an alias in the alias source (`data/intblocks_aliases.yaml`) with a `reason` of `renamed`, `merged`, or `disambiguated`, rather than removed without trace. When an intblock id is retired because its meaning moved to a country attribute field, the retirement SHALL be recorded in `data/attribute_intblock_migrations.yaml` instead of an intblock alias entry.

#### Scenario: Rename records an alias

- **WHEN** an intblock id is renamed from `OLD` to `NEW`
- **THEN** an alias entry `OLD → NEW` with `reason: renamed` is added to the alias source in the same change

#### Scenario: Merge records an alias

- **WHEN** two intblock records are merged into a single id
- **THEN** the removed id is recorded as an alias pointing to the surviving id with `reason: merged`

#### Scenario: Acronym reassignment records a disambiguation alias

- **WHEN** an entity vacates an id (e.g. `ASF`) which is then reused for a different entity, and the original entity moves to a new id (e.g. `FSA`)
- **THEN** an alias entry `ASF → FSA` with `reason: disambiguated` is recorded, even though `ASF` remains a current id for the different entity

#### Scenario: Attribute retirement records a field migration

- **WHEN** intblock id `LHTRAFFIC` is removed because driving side lives on countries
- **THEN** `data/attribute_intblock_migrations.yaml` contains a `LHTRAFFIC` entry mapping to `car_side: left` and no intblock alias target is required
