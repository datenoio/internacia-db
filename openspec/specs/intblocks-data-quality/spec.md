# intblocks-data-quality Specification

## Purpose
TBD - created by archiving change add-scheduled-link-validation. Update Purpose after archive.
## Requirements
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

### Requirement: Intblock YAML JSON Schema validation

Every file under `data/intblocks/**/*.yaml` SHALL validate against `data/schemas/intblocks.schema.json` before dataset export.

#### Scenario: Valid intblock file passes schema

- **WHEN** `validate_intblocks.py` runs on a well-formed intblock YAML file
- **THEN** validation reports no schema errors for that file

#### Scenario: Invalid intblock file fails schema

- **WHEN** an intblock YAML file has a required field with wrong type
- **THEN** validation reports a schema error and exits with non-zero status

### Requirement: Intblock identifier uniqueness

Each intblock record SHALL have a unique `id` across all YAML files under `data/intblocks/`.

#### Scenario: Duplicate intblock id rejected

- **WHEN** two intblock YAML files share the same `id`
- **THEN** validation reports a duplicate identifier error

### Requirement: Blocktype taxonomy validation

Every entry in an intblock's `blocktype` list SHALL reference a defined blocktype in the blocktypes taxonomy file.

#### Scenario: Valid blocktype accepted

- **WHEN** an intblock has `blocktype: [intorg]` and `intorg` exists in blocktypes taxonomy
- **THEN** blocktype validation passes

#### Scenario: Unknown blocktype rejected

- **WHEN** an intblock references a blocktype not in the taxonomy
- **THEN** validation reports a blocktype reference error

### Requirement: Configurable intblocks completeness thresholds

Completeness rules for intblocks SHALL be defined in `data/schemas/intblocks_completeness.yaml` with per-field `max_null_rate` and `mode` (`warn` or `error`).

#### Scenario: Field exceeding warn threshold emits warning

- **WHEN** `wikidata_id` null rate exceeds configured `max_null_rate` with `mode: warn`
- **THEN** validation emits a warning but does not fail the build

#### Scenario: Field exceeding error threshold fails build

- **WHEN** a field has `mode: error` and null rate exceeds `max_null_rate`
- **THEN** validation fails with a completeness error

### Requirement: Intblock includes contract enforcement

For each entry in `includes`, `id` SHALL be the authoritative member identifier; `name` is a source label and MAY differ from canonical country names.

#### Scenario: Include with valid country id passes

- **WHEN** an include has `type: country` and `id: US` and `data/countries/US.yaml` exists
- **THEN** include validation passes for that entry

#### Scenario: Include with missing country id fails or warns per config

- **WHEN** an include has `type: country` and `id: ZZ` with no matching country file
- **THEN** validation reports an unresolved include per completeness config mode

