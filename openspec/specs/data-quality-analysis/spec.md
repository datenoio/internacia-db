# data-quality-analysis Specification

## Purpose
TBD - created by archiving change add-data-quality-analysis. Update Purpose after archive.
## Requirements
### Requirement: Data quality analysis CLI command

The dataset builder CLI (`scripts/builder.py`) SHALL provide an `analyze-quality` command to run comprehensive quality checks on countries and intblocks datasets, and save the results as structured and human-readable reports in the `dataquality/` directory.

#### Scenario: Default run produces organized reports
- **WHEN** the user runs `scripts/builder.py analyze-quality`
- **THEN** it scans all countries and intblocks YAML sources, executes validation rules, groups issues by country, priority, and rule, and writes `full_report.txt`, `full_report.jsonl`, `primary_priority.jsonl`, and subfolders under `dataquality/` for countries, priorities, and rules.

#### Scenario: Custom output directory specification
- **WHEN** the user runs `scripts/builder.py analyze-quality --output custom_reports`
- **THEN** the generated reports are placed under the directory `custom_reports/` instead of `dataquality/`.

### Requirement: Shared quality rule registry

The data-quality rules SHALL be listed once, in `internacia_builder/validate/registry.py`, with the dataset each rule belongs to and its severity in the validators (`error`, `warning`, or report-only). `validate_countries.py`, `validate_intblocks.py` and `analyze-quality` SHALL all run the rules from this registry. Every issue type a rule can emit SHALL have a priority and a description in the quality report, and the issue types of validator errors SHALL be CRITICAL or IMPORTANT so that the quality gate fails on them as well.

#### Scenario: Validator error appears in the quality report as blocking

- **WHEN** a country record has `dvd_region: 9`
- **THEN** `validate_countries.py` reports an error and `analyze-quality` reports an `INVALID_ATTRIBUTE_FIELD` issue with priority IMPORTANT

#### Scenario: New rule is enforced by both consumers

- **WHEN** a contributor adds a rule with severity `warning` to the registry
- **THEN** `validate_intblocks.py` reports its findings as warnings and `analyze-quality` reports them without further changes

