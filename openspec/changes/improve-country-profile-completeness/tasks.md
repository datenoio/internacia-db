## 1. Capital coverage
- [x] 1.1 Identify which of the 15 capital-less records have a de-facto capital or seat of government
- [x] 1.2 Fill `capital_city` (name, lng, lat) with `provenance` for eligible entities (e.g. TW, PS, HK, MO, GI, VA, IL)
- [x] 1.3 Document genuinely capital-less entities (uninhabited territories) as expected exclusions

## 2. Completeness gate rationale
- [x] 2.1 Re-scope or re-threshold the `gini` gate in `countries_completeness.yaml` with a documented rationale
- [x] 2.2 Re-check the `capital_city` threshold after capital backfill and adjust if warranted
- [x] 2.3 Record the rationale in the completeness config or `docs/enrichment.md`

## 3. Borders contract docs
- [x] 3.1 Ensure README schema table and consumer docs consistently describe `borders` as ISO alpha-3

## 4. Validate and rebuild
- [x] 4.1 Run `validate_countries.py` and confirm warnings resolved or intentionally ratcheted
- [x] 4.2 Rebuild datasets and run `openspec validate improve-country-profile-completeness --strict`
