## 1. Documentation

- [x] 1.1 Document WB classification gaps and expected absences in country policy / enrichment docs (report §1.1)
- [x] 1.2 List the 33 records missing `region`/`incomeLevel`/`lendingType` and sourcing plan per entity type

## 2. Alternative classification backfill (High)

- [x] 2.1 Map UN M49 regional classifications for non-WB-classified records where applicable
- [x] 2.2 Backfill `adminregion` for high-income/special-status records from M49 or documented manual values
- [x] 2.3 Backfill `region`, `incomeLevel`, `lendingType` where authoritative non-WB source exists
- [x] 2.4 Add provenance for all alternative-sourced classification fields

## 3. Gini backfill (Medium)

- [x] 3.1 Identify 82 countries missing recent gini; source older estimates from World Bank archives or national statistics
- [x] 3.2 Populate `gini` struct (`value`, `year`, `source`) where data exists (170/252; remaining 82 lack WB observations)
- [x] 3.3 Coordinate incremental `gini` `max_null_rate` tightening with `add-countries-enrichment-refresh`

## 4. Validation

- [x] 4.1 Run `validate_countries.py` and measure classification field null rates
- [x] 4.2 Run `openspec validate enrich-country-wb-classifications --strict`
