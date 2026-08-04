## 1. Schema
- [x] 1.1 Add optional `geonames_id`, `ioc_code`, `fifa_code`, `fips_code` to `countries.schema.json` with descriptions
- [x] 1.2 Update completeness config if any crosswalk is targeted for high coverage

## 2. Enrichment and backfill
- [x] 2.1 Implement or extend enrichment to populate crosswalks from GeoNames, IOC, FIFA, FIPS sources
- [x] 2.2 Backfill official ISO 3166-1 records first; document nulls on non-standard codes where sources lack entries
- [x] 2.3 Add provenance entries for enriched crosswalk fields

## 3. Documentation and validation
- [x] 3.1 Document join examples in `docs/ai-consumers.md` and `docs/query-examples.md`
- [x] 3.2 Run `validate_countries.py --json` and rebuild artifacts

## 4. Optional bbox (defer or include)
- [x] 4.1 If in scope: add optional `bbox` object to schema and Wikidata enrichment pass
