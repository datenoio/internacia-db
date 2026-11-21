## ADDED Requirements

### Requirement: Shared quality rule registry

The data-quality rules SHALL be listed once, in `internacia_builder/validate/registry.py`, with the dataset each rule belongs to and its severity in the validators (`error`, `warning`, or report-only). `validate_countries.py`, `validate_intblocks.py` and `analyze-quality` SHALL all run the rules from this registry. Every issue type a rule can emit SHALL have a priority and a description in the quality report, and the issue types of validator errors SHALL be CRITICAL or IMPORTANT so that the quality gate fails on them as well.

#### Scenario: Validator error appears in the quality report as blocking

- **WHEN** a country record has `dvd_region: 9`
- **THEN** `validate_countries.py` reports an error and `analyze-quality` reports an `INVALID_ATTRIBUTE_FIELD` issue with priority IMPORTANT

#### Scenario: New rule is enforced by both consumers

- **WHEN** a contributor adds a rule with severity `warning` to the registry
- **THEN** `validate_intblocks.py` reports its findings as warnings and `analyze-quality` reports them without further changes
