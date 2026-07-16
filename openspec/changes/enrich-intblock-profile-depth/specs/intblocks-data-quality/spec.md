## ADDED Requirements

### Requirement: Structural metadata enrichment from Wikidata

For intblock records with a resolved `wikidata_id`, enrichment SHALL backfill `headquarters` (from headquarters location and coordinate claims) and `founded` (from the inception claim) when those fields are empty, recording a `provenance` entry for each filled field and never overwriting existing hand-curated values.

#### Scenario: Headquarters filled from Wikidata

- **WHEN** a record has a `wikidata_id`, an empty `headquarters`, and Wikidata exposes a headquarters location claim
- **THEN** enrichment sets `headquarters` and adds a `provenance` entry with `field: headquarters` and `source: Wikidata`

#### Scenario: Existing founded date preserved

- **WHEN** a record already has a `founded` value
- **THEN** enrichment does not overwrite it even if Wikidata exposes an inception claim

### Requirement: Verification timestamp policy

Records touched by enrichment or manual verification SHALL carry a `last_verified` ISO 8601 date, and `validate_intblocks.py` SHALL report `last_verified` coverage against a configurable threshold in `intblocks_completeness.yaml` in warn mode.

#### Scenario: Enrichment stamps last_verified

- **WHEN** `enrich_intblocks.py` updates any field on a record
- **THEN** the record's `last_verified` is set to the run date

#### Scenario: Low coverage warns without failing build

- **WHEN** the share of records with a `last_verified` date is below the configured threshold with `mode: warn`
- **THEN** validation emits a warning but does not fail the build
