## ADDED Requirements

### Requirement: Generated data dictionary

The repository SHALL maintain `docs/data-dictionary.md` generated from `countries.schema.json` and `intblocks.schema.json`, with a script to regenerate it when schemas change.

#### Scenario: Field reference available

- **WHEN** a non-technical user opens the data dictionary
- **THEN** they find every country and intblock field with type and description

#### Scenario: Schema drift detected

- **WHEN** a pull request modifies a JSON Schema without regenerating the dictionary
- **THEN** CI or documented check fails or warns

### Requirement: GitHub issue templates

The repository SHALL provide structured GitHub issue templates for data errors, data/org requests, and code bugs under `.github/ISSUE_TEMPLATE/`.

#### Scenario: Data error report guided

- **WHEN** a user opens a new GitHub issue
- **THEN** they can choose a data error template with fields for record id, expected vs actual, and source URL

### Requirement: Non-programmer getting started guide

The repository SHALL include `docs/getting-started.md` explaining what the datasets contain, how to open CSV or lite exports, and how to cite via DOI.

#### Scenario: Educator finds entry path

- **WHEN** a reader follows README link to getting started
- **THEN** they can open country data in a spreadsheet without installing DuckDB

### Requirement: Pipeline architecture diagram

README or `docs/architecture.md` SHALL include a diagram of the YAML → validate → enrich → build → release pipeline with key paths.

#### Scenario: New contributor understands flow

- **WHEN** a contributor views the architecture diagram
- **THEN** they can identify where validation, enrichment, and export occur

### Requirement: Dev artifact indexes

`dev/research/README.md` and `dev/scripts/README.md` SHALL index research reports and script support status; `data/_legacy/` SHALL carry a warning that contents are obsolete.

#### Scenario: Research reports discoverable

- **WHEN** a reader opens dev/research README
- **THEN** they find links to gap analysis reports and methodology notes
