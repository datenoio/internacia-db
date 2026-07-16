## ADDED Requirements

### Requirement: Membership list internal consistency

Intblock membership data SHALL be internally consistent: an `includes` list SHALL NOT contain two entries with the same `id`, a populated `membership_count` SHALL match the number of `includes` entries within the tolerance configured in `data/schemas/intblocks_completeness.yaml`, and a record with `membership_applicability: not_applicable` SHALL NOT have a non-empty `includes` list. Violations SHALL be reported as `DUPLICATE_INCLUDE_ENTRY`, `MEMBERSHIP_COUNT_MISMATCH`, and `CONTRADICTORY_APPLICABILITY` respectively at MEDIUM priority.

#### Scenario: Duplicate include entry reported

- **WHEN** an intblock's `includes` list contains two entries with `id: FR`
- **THEN** validation reports a `DUPLICATE_INCLUDE_ENTRY` issue

#### Scenario: Membership count mismatch reported

- **WHEN** an intblock has `membership_count: 10` and 13 `includes` entries with mismatch beyond the configured tolerance
- **THEN** validation reports a `MEMBERSHIP_COUNT_MISMATCH` issue

#### Scenario: Contradictory applicability marker reported

- **WHEN** an intblock has `membership_applicability: not_applicable` and a non-empty `includes` list
- **THEN** validation reports a `CONTRADICTORY_APPLICABILITY` issue

### Requirement: Lifecycle chronology validation

Intblock lifecycle fields SHALL be chronologically coherent: `founded` and `dissolved` SHALL parse as dates or years, `dissolved` SHALL NOT precede `founded`, neither SHALL be in the future, and a record with `status: historical` SHALL declare a `dissolved` date. Violations SHALL be reported as `CHRONOLOGY_ERROR` (dates) or `LIFECYCLE_INCONSISTENCY` (status) at MEDIUM priority.

#### Scenario: Dissolved before founded reported

- **WHEN** an intblock has `founded: '1990'` and `dissolved: '1985'`
- **THEN** validation reports a `CHRONOLOGY_ERROR` issue

#### Scenario: Future founding date reported

- **WHEN** an intblock has a `founded` value later than the current date
- **THEN** validation reports a `CHRONOLOGY_ERROR` issue

#### Scenario: Historical status without dissolved date reported

- **WHEN** an intblock has `status: historical` and no `dissolved` value
- **THEN** validation reports a `LIFECYCLE_INCONSISTENCY` issue

#### Scenario: Dissolved record without historical status reported

- **WHEN** an intblock has a `dissolved` value and `status: formal`
- **THEN** validation reports a `LIFECYCLE_INCONSISTENCY` issue

### Requirement: Intblock quality report parity

Every intblock rule enforced by `validate_intblocks.py` SHALL also be executed by the quality analyzer and surfaced in `dataquality/` reports, including filename-to-`id` alignment, directory-to-blocktype alignment, deprecated topic key detection against `data/schemas/topic_aliases.yaml`, and provenance integrity (each `provenance[].field` naming an existing record field with a valid, non-future `retrieved_at` date).

#### Scenario: Filename and id mismatch appears in quality report

- **WHEN** the file `data/intblocks/bank/ADB.yaml` contains `id: XYZ`
- **THEN** the analyzer reports a `FILENAME_ID_MISMATCH` issue

#### Scenario: Directory and blocktype mismatch appears in quality report

- **WHEN** an intblock file under `data/intblocks/bank/` has no `bank` entry in its `blocktype` list
- **THEN** the analyzer reports a `DIRECTORY_BLOCKTYPE_MISMATCH` issue

#### Scenario: Deprecated topic key appears in quality report

- **WHEN** an intblock uses topic key `climate`, which `topic_aliases.yaml` maps to canonical `climate_change`
- **THEN** the analyzer reports a `DEPRECATED_TOPIC_KEY` issue
