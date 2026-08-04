## ADDED Requirements

### Requirement: Attribute vs geographic enumeration guidance

Contributor and AI-consumer documentation SHALL explain that country attribute partitions (traffic hand, scripts, DVD region, broadcast systems, legal traditions, rail gauges) are country fields, while named geographic reference sets may remain intblocks. Documentation SHALL link to `docs/intblock-inclusion-policy.md` and the attribute migration artifact for retired ids.

#### Scenario: Agent discovers car_side instead of traffichand

- **WHEN** an agent reads `docs/ai-consumers.md` or `llms.txt` for driving-side queries
- **THEN** the docs prescribe filtering `countries.car_side` and mention that `traffichand` intblocks are retired

#### Scenario: Inclusion policy distinguishes attribute partitions

- **WHEN** a contributor reads `docs/intblock-inclusion-policy.md`
- **THEN** the policy states attribute partitions are out of intblock scope and points to country fields / vocabs

## MODIFIED Requirements

### Requirement: README accuracy

README SHALL list all maintained utility scripts and link to gap analysis files with correct paths. README SHALL state current dataset counts (countries, intblocks, categories, blocktypes) consistent with the build manifests, and SHALL accurately describe which validators run before export. README SHALL describe driving side and other migrated attribute classifications as country properties, not intblock categories, after attribute intblock retirement.

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

#### Scenario: Field table mentions car_side as country property

- **WHEN** a reader opens the README countries field summary after attribute migration
- **THEN** `car_side` and the newly added attribute fields are listed as country properties rather than intblock categories
