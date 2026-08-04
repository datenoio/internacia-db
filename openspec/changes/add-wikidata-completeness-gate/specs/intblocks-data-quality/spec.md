## ADDED Requirements

### Requirement: Wikidata identifier completeness with exclusions

Every intblock record SHALL include a `wikidata_id` OR appear on a maintained exclusion list (`data/schemas/wikidata_exclusions.yaml`) documenting that no Wikidata item exists, with verification date and source. Validation SHALL fail on records missing both.

#### Scenario: Excluded org passes validation

- **WHEN** AFROSAIE lacks wikidata_id but is listed on the exclusion list with verified_at
- **THEN** validation passes

#### Scenario: Unlisted missing id fails

- **WHEN** an intblock with a findable Wikidata item lacks wikidata_id and is not excluded
- **THEN** validation reports a completeness error

#### Scenario: Fixable backfill reduces exclusions

- **WHEN** ACAO is backfilled with Q22686285
- **THEN** it is removed from the exclusion list if present and validation requires wikidata_id
