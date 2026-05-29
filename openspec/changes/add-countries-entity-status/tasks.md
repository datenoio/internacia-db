## 1. Schema

- [x] 1.1 Add `entity_type`, `code_status`, optional `recognition_status`, `parent_entity` to JSON Schema and PyArrow
- [x] 1.2 Default `code_status: official_iso3166_1` for standard ISO records in enrichment or migration script

## 2. Policy records

- [x] 2.1 Update `data/countries/AN.yaml`: `entity_type: historical_entity`, `code_status: obsolete`
- [x] 2.2 Update `data/countries/JG.yaml`: `entity_type: supranational_grouping`, `code_status: user_assigned`
- [x] 2.3 Update `data/countries/KV.yaml`: `entity_type: disputed_territory`, `code_status: user_assigned`, `recognition_status`

## 3. Documentation and validation

- [x] 3.1 Add `docs/country-code-policy.md` (ISO, user-assigned, M49 disclaimer, filter examples)
- [x] 3.2 Extend `validate_countries.py`: non-ISO codes require `code_status`; validate enum values
- [x] 3.3 Document deferred CIS2 `XA`–`XN` resolution in design.md (no implementation)

## 4. Export

- [x] 4.1 Regenerate datasets
- [x] 4.2 Run `openspec validate add-countries-entity-status --strict`
