## ADDED Requirements

### Requirement: Include date consistency

For each `includes[]` entry, `joined` and `left` dates SHALL parse as `YYYY`, `YYYYs`, `YYYY-MM`, or `YYYY-MM-DD`, SHALL NOT lie in the future, `left` SHALL NOT precede `joined`, and neither SHALL postdate the block's `dissolved` date. Comparisons SHALL be precision-aware (a bare year is not "before" a specific date in the same year). `joined` earlier than `founded` SHALL NOT be flagged, because signature and ratification dates commonly precede entry into force. Violations SHALL be reported as `INCLUDE_DATE_INCONSISTENCY`.

#### Scenario: Left before joined reported

- **WHEN** an include has `joined: 1995` and `left: 1990`
- **THEN** validation reports an `INCLUDE_DATE_INCONSISTENCY` issue

#### Scenario: Join after dissolution reported

- **WHEN** a block has `dissolved: 1991` and an include has `joined: 1994`
- **THEN** validation reports an `INCLUDE_DATE_INCONSISTENCY` issue

#### Scenario: Ratification before entry into force passes

- **WHEN** a block has `founded: 2008-07-03` and an include has `joined: 2008-05-09`
- **THEN** no `INCLUDE_DATE_INCONSISTENCY` issue is reported

### Requirement: Founding members appear in includes

Each `founding_members` entry SHALL resolve to an existing country code and, when the record has a populated `includes` list, SHALL appear in it. Violations SHALL be reported as `FOUNDING_MEMBER_NOT_INCLUDED` warnings (former founders may legitimately be absent and are resolved by adding a `former_member` include entry or removing the founder).

#### Scenario: Founder missing from includes warned

- **WHEN** `founding_members` contains `CU` but no include entry has `id: CU`
- **THEN** validation reports a `FOUNDING_MEMBER_NOT_INCLUDED` warning

### Requirement: Historical entity membership status

An include entry referencing a country with `entity_type: historical_entity` SHALL NOT carry an active-class status (`member`, `founding_member`, `associate`, `associate_member`, `associated`, `participant`) in a block whose `status` is not `historical`. Violations SHALL be reported as `HISTORICAL_ENTITY_ACTIVE_MEMBER`.

#### Scenario: Dissolved country as active member warned

- **WHEN** an active block includes `AN` (Netherlands Antilles, a historical entity) with status `member`
- **THEN** validation reports a `HISTORICAL_ENTITY_ACTIVE_MEMBER` warning

### Requirement: Verification freshness

When `last_verified` is populated and `quality.last_verified_max_age_months` is configured in `intblocks_completeness.yaml`, records whose `last_verified` date is older than the configured age SHALL be reported as `STALE_LAST_VERIFIED` (LOW advisory).

#### Scenario: Old verification date warned

- **WHEN** `last_verified` is more than the configured maximum months in the past
- **THEN** validation reports a `STALE_LAST_VERIFIED` advisory

### Requirement: Canonical topic catalog

Topic keys on intblock records SHALL exist in the canonical catalog `data/schemas/topics.yaml`. Keys absent from the catalog SHALL be reported as `UNKNOWN_TOPIC_KEY` warnings; deprecated keys remain governed by the existing alias rule.

#### Scenario: Unknown topic key warned

- **WHEN** a record uses topic key `undersea_basket_weaving` not present in `topics.yaml`
- **THEN** validation reports an `UNKNOWN_TOPIC_KEY` warning

#### Scenario: Catalogued key passes

- **WHEN** a record uses topic key `water` present in `topics.yaml`
- **THEN** no `UNKNOWN_TOPIC_KEY` issue is reported

### Requirement: Text encoding integrity for intblocks

`name` and `description` fields SHALL NOT contain control characters, U+FFFD replacement characters, or double-encoded UTF-8 artifacts. Violations SHALL be reported as `MOJIBAKE_TEXT`.

#### Scenario: Double-encoded UTF-8 reported

- **WHEN** a description contains the byte sequence rendered as `Ã©` (double-encoded é)
- **THEN** validation reports a `MOJIBAKE_TEXT` issue
