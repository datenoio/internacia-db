## ADDED Requirements

### Requirement: Canonical topic alias registry

Deprecated intblock topic keys SHALL be documented in `data/schemas/topic_aliases.yaml` with a `canonical` target and optional `reason` for each deprecated key.

#### Scenario: Deprecated key maps to canonical

- **WHEN** a maintainer looks up `climate` in the alias registry
- **THEN** the canonical target is `climate_change`

#### Scenario: Validator warns on deprecated key

- **WHEN** an intblock record uses a topic key listed as deprecated in the alias registry
- **THEN** `validate_intblocks.py` emits a warning naming the canonical replacement

### Requirement: Minimum topic assignment

Every intblock record SHALL have at least one entry in its `topics` list after consolidation.

#### Scenario: Record with topics passes

- **WHEN** an intblock YAML has `topics` with one or more keys
- **THEN** topic completeness validation passes for that record

#### Scenario: Empty topics fails or warns per config

- **WHEN** an intblock record has an empty or missing `topics` list
- **THEN** validation reports per configured mode in intblocks completeness config

### Requirement: Topic taxonomy governance

The repository SHALL document in `docs/topic-taxonomy.md` the process for proposing, approving, merging, and deprecating topic keys.

#### Scenario: Contributor finds governance doc

- **WHEN** a contributor needs to add a new topic key
- **THEN** `docs/topic-taxonomy.md` describes the approval and alias-update steps
