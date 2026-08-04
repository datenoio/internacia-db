## 1. Exclusion list
- [x] 1.1 Create `data/schemas/wikidata_exclusions.yaml` with id, reason, verified_at, source
- [x] 1.2 Populate from deep-review audit (INTOSAI branches, ICAO RSOOs, etc.)

## 2. Validation gate
- [x] 2.1 Add rule: missing wikidata_id fails unless id is on exclusion list
- [x] 2.2 Wire into `validate_intblocks.py` and CI

## 3. Backfill
- [x] 3.1 Run `enrich_intblocks.py` wikidata matcher for non-excluded records
- [x] 3.2 Remove ids from exclusion list when Wikidata entries are created or found

## 4. Documentation
- [x] 4.1 Document exclusion criteria and review cadence in enrichment or inclusion policy docs
