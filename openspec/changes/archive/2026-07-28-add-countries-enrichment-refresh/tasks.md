## 1. Refresh runbook

- [x] 1.1 Document enrichment refresh procedure in CONTRIBUTING or `docs/enrichment.md`
- [x] 1.2 Define staleness threshold for provenance `retrieved_at` (e.g. 12 months)

## 2. Validation extensions

- [x] 2.1 Add currency code format validation (warn mode) against ISO 4217 pattern
- [x] 2.2 Add provenance freshness warn in `validate_countries.py`
- [x] 2.3 Plan incremental tightening of `gini` `max_null_rate` in completeness config

## 3. Optional automation

- [x] 3.1 Add scheduled workflow for enrichment check mode (report only) or manual trigger
- [x] 3.2 Run `openspec validate add-countries-enrichment-refresh --strict`
