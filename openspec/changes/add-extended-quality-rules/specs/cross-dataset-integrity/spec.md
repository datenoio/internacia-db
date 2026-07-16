## ADDED Requirements

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
