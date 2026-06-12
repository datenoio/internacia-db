## ADDED Requirements

### Requirement: Scheduled external link validation

The repository SHALL run intblock URL and Wikidata validation on a scheduled cadence independent of pull request CI.

#### Scenario: Weekly scheduled run

- **WHEN** the scheduled workflow triggers on the default branch
- **THEN** `validate_links.py` executes and produces a report artifact

#### Scenario: Scheduled failure does not block merges

- **WHEN** the scheduled link validation finds broken URLs
- **THEN** the workflow completes with failure status but does not block unrelated pull request merges

### Requirement: Link validation report artifact

Scheduled and manual link validation runs SHALL produce a machine-readable or markdown report suitable for triage.

#### Scenario: Report uploaded on scheduled run

- **WHEN** scheduled validation completes
- **THEN** a report file is available as a workflow artifact

#### Scenario: Manual validation with report

- **WHEN** a maintainer runs `validate_links.py --report links-report.json`
- **THEN** a structured report is written to the specified path
