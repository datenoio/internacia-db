## 1. Policy decision

- [x] 1.1 Review options in `docs/country-code-policy.md` and select approach (document in `design.md`)
- [x] 1.2 Get stakeholder approval before modifying country dataset

## 2. Implementation

- [x] 2.1 Implement chosen policy (country YAML files, include type change, or explicit allowlist)
- [x] 2.2 Update `validate_countries.py` and intblocks validators with new rules
- [x] 2.3 Update completeness config (`special_entity_allowlist` or equivalent)

## 3. Documentation and validation

- [x] 3.1 Update `docs/country-code-policy.md` with final policy and filter examples
- [x] 3.2 Add CHANGELOG entry with consumer guidance
- [x] 3.3 Run full validation and rebuild datasets
- [x] 3.4 Run `openspec validate resolve-cis2-deferred-entities --strict`
