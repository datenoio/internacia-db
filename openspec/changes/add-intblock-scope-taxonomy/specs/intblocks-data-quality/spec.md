## ADDED Requirements

### Requirement: Intblock scope category

Intblock records MAY include an optional `scope_category` field with values from a documented enum (`igo`, `treaty_body`, `policy_forum`, `reference_enumeration`) declared in `intblocks.schema.json`. The inclusion policy document SHALL define each category with examples.

#### Scenario: Core IGO labeled

- **WHEN** a consumer reads `data/intblocks/military/NATO.yaml` after labeling
- **THEN** `scope_category` is `igo`

#### Scenario: Reference enumeration labeled

- **WHEN** a consumer filters intblocks where `scope_category = 'reference_enumeration'`
- **THEN** DVD region records are included and NATO is excluded

### Requirement: Intblock inclusion policy document

The repository SHALL maintain `docs/intblock-inclusion-policy.md` stating what qualifies for an intblock record, how scope categories map to blocktypes, and how consumers should filter mixed corpora.

#### Scenario: Policy answers forum vs IGO question

- **WHEN** a reader asks whether Munich Security Conference belongs in the same filter as NATO
- **THEN** the policy doc explains the scope_category distinction and recommended filters
