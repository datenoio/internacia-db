## MODIFIED Requirements

### Requirement: Blocktype taxonomy validation

Every entry in an intblock's `blocktype` list SHALL reference a defined blocktype in the blocktypes **source** taxonomy file under `data/blocktypes/` (not the generated datasets copy).

#### Scenario: Valid blocktype accepted

- **WHEN** an intblock has `blocktype: [intorg]` and `intorg` exists in `data/blocktypes/blocktypes.yaml`
- **THEN** blocktype validation passes

#### Scenario: Unknown blocktype rejected

- **WHEN** an intblock references a blocktype not in the source taxonomy
- **THEN** validation reports a blocktype reference error

## ADDED Requirements

### Requirement: Blocktypes source and generated separation

Blocktypes taxonomy SHALL be maintained as source YAML under `data/blocktypes/` and exported to `data/datasets/` by the builder.

#### Scenario: Builder reads source taxonomy

- **WHEN** `scripts/builder.py build` exports blocktypes
- **THEN** it reads from `data/blocktypes/blocktypes.yaml` and writes generated artifacts to `data/datasets/`

#### Scenario: Contributors edit source not generated copy

- **WHEN** a contributor adds a new blocktype
- **THEN** they edit `data/blocktypes/blocktypes.yaml` and rebuild rather than editing generated files directly
