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

