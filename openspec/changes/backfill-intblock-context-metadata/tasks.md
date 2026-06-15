## 1. High-profile context fields (Critical)

- [x] 1.1 Define high-profile cohort (e.g. UN agencies, NATO, EU, AU, ASEAN, G7, G20, major development banks)
- [x] 1.2 Backfill `legal_status` for cohort from official charters/treaty basis
- [x] 1.3 Backfill `geographic_scope` (global, regional, sub-regional) for cohort
- [x] 1.4 Backfill `headquarters` city/country for cohort
- [x] 1.5 Add `provenance` entries for each enriched field

## 2. Description quality (High)

- [x] 2.1 Identify all records matching templated description pattern (~253 records)
- [x] 2.2 Replace descriptions in high-profile cohort first (batch script + manual review)
- [x] 2.3 Extend Wikidata/Wikipedia sourcing via `enrich_intblocks.py` where high-confidence
- [x] 2.4 Ratchet templated-description completeness threshold in `intblocks_completeness.yaml`

## 3. Founded dates (Low)

- [x] 3.1 Backfill `founded` for high-profile records missing dates
- [x] 3.2 Plan broader `founded` backfill for remaining ~355 records as follow-up batch

## 4. Validation

- [x] 4.1 Measure null rates for `legal_status`, `geographic_scope`, `headquarters` before/after
- [x] 4.2 Run `validate_intblocks.py` and description quality gate
- [x] 4.3 Run `openspec validate backfill-intblock-context-metadata --strict`
