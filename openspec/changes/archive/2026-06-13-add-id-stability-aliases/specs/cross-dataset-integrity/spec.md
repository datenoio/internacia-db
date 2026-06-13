## ADDED Requirements

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
