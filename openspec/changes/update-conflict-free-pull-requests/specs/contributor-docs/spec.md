## MODIFIED Requirements

### Requirement: README accuracy

README SHALL list all maintained utility scripts and link to gap analysis files with correct paths. README SHALL state current dataset counts (countries, intblocks, categories, blocktypes) consistent with the build manifests, with the intblock count rounded down to the hundred and written as `N+`, and SHALL accurately describe which validators run before export. README SHALL describe driving side and other migrated attribute classifications as country properties, not intblock categories, after attribute intblock retirement.

#### Scenario: Scripts table complete

- **WHEN** a reader checks the README scripts table
- **THEN** all non-deprecated scripts under `scripts/` are listed with purpose

#### Scenario: Gap analysis link valid

- **WHEN** a reader follows the gap analysis link in README Notes
- **THEN** the linked file path exists and has no typographical errors

#### Scenario: Counts match manifests

- **WHEN** a reader compares README dataset counts to the built `*.manifest.json` files
- **THEN** the stated country and blocktype counts equal the manifests, and the stated intblock count is the manifest count rounded down to the hundred, followed by `+`

#### Scenario: Validation description accurate

- **WHEN** a reader reads the README validation section
- **THEN** it states that both country and intblock validation run before export

#### Scenario: Field table mentions car_side as country property

- **WHEN** a reader opens the README countries field summary after attribute migration
- **THEN** `car_side` and the newly added attribute fields are listed as country properties rather than intblock categories

### Requirement: Documentation count accuracy

Dataset record and category counts stated across maintained documentation (`llms.txt`, `docs/ai-consumers.md`, `openspec/project.md`, and other docs) SHALL match the current build manifests, and referenced generated artifacts SHALL exist. The intblock count SHALL be stated rounded down to the hundred and written as `N+`, so that adding records does not change documentation until the count crosses a hundred.

#### Scenario: llms.txt counts current

- **WHEN** a consumer reads intblock and country counts in `llms.txt`
- **THEN** the country count equals the manifest `row_count`, and the intblock count is the manifest `row_count` rounded down to the hundred, followed by `+`

#### Scenario: Adding a record leaves docs unchanged

- **WHEN** a pull request raises the intblock count from 1304 to 1310
- **THEN** the documentation count check passes without documentation edits

#### Scenario: Dataset card states the rounded count

- **WHEN** the build writes the committed dataset card `data/datasets/README.md` with 1304 intblocks
- **THEN** the card states `1300+` intblocks, so a build with 1310 intblocks writes the same card

#### Scenario: Referenced artifact exists

- **WHEN** documentation references a generated file such as a manifest
- **THEN** that file is produced by the build
