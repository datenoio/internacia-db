## MODIFIED Requirements

### Requirement: README accuracy

README SHALL list all maintained utility scripts and link to gap analysis files with correct paths. README SHALL state current dataset counts (countries, intblocks, categories, blocktypes) consistent with the build manifests, and SHALL accurately describe which validators run before export.

#### Scenario: Scripts table complete

- **WHEN** a reader checks the README scripts table
- **THEN** all non-deprecated scripts under `scripts/` are listed with purpose

#### Scenario: Gap analysis link valid

- **WHEN** a reader follows the gap analysis link in README Notes
- **THEN** the linked file path exists and has no typographical errors

#### Scenario: Counts match manifests

- **WHEN** a reader compares README dataset counts to `data/datasets/*.manifest.json`
- **THEN** the stated country, intblock, and blocktype counts match the manifests

#### Scenario: Validation description accurate

- **WHEN** a reader reads the README validation section
- **THEN** it states that both country and intblock validation run before export

## ADDED Requirements

### Requirement: Documentation count accuracy

Dataset record and category counts stated across maintained documentation (`llms.txt`, `docs/ai-consumers.md`, `openspec/project.md`, and other docs) SHALL match the current build manifests, and referenced generated artifacts SHALL exist.

#### Scenario: llms.txt counts current

- **WHEN** a consumer reads intblock and country counts in `llms.txt`
- **THEN** they equal the current manifest `row_count` values

#### Scenario: Referenced artifact exists

- **WHEN** documentation references a generated file such as a manifest
- **THEN** that file is produced by the build

### Requirement: Internal documentation link checking

CI SHALL run an internal Markdown link checker over repository docs and fail on broken internal links.

#### Scenario: Broken internal link fails CI

- **WHEN** a Markdown file links to a repository path that does not exist
- **THEN** the link-check step fails
