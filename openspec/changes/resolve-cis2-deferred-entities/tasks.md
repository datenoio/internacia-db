## 1. Policy decision

- [ ] 1.1 Review options in `docs/country-code-policy.md` and select approach (document in `design.md`)
- [ ] 1.2 Get stakeholder approval before modifying country dataset

## 2. Implementation

- [ ] 2.1 Implement chosen policy (country YAML files, include type change, or explicit allowlist)
- [ ] 2.2 Update `validate_countries.py` and intblocks validators with new rules
- [ ] 2.3 Update completeness config (`special_entity_allowlist` or equivalent)

## 3. Documentation and validation

- [ ] 3.1 Update `docs/country-code-policy.md` with final policy and filter examples
- [ ] 3.2 Add CHANGELOG entry with consumer guidance
- [ ] 3.3 Run full validation and rebuild datasets
- [ ] 3.4 Run `openspec validate resolve-cis2-deferred-entities --strict`
