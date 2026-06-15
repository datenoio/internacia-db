## ADDED Requirements

### Requirement: Primary blocktype directory alignment

The first value in an intblock record's `blocktype` list SHALL match the parent directory name under `data/intblocks/` (e.g. a record in `data/intblocks/trade/` must have primary blocktype `trade`).

#### Scenario: Aligned record passes

- **WHEN** `data/intblocks/trade/WTO.yaml` has `blocktype: [trade, intorg]`
- **THEN** directory alignment validation passes

#### Scenario: Misaligned primary blocktype reported

- **WHEN** a record in `data/intblocks/political/` has `blocktype: [economic, political]`
- **THEN** validation reports a primary blocktype–directory mismatch

### Requirement: Directory name matches blocktype value

Category directories under `data/intblocks/` SHALL use blocktype values as directory names, not synonyms (e.g. `tax` not `taxation`, `transport` not `transportation`).

#### Scenario: Renamed directory validates

- **WHEN** records are stored under `data/intblocks/tax/`
- **THEN** no directory named `taxation` exists in the intblocks tree

### Requirement: Orphan blocktype cleanup

Blocktype taxonomy entries that are not referenced by any intblock record SHALL be removed from the blocktypes source file unless explicitly reserved for upcoming records.

#### Scenario: Unused plural blocktype removed

- **WHEN** no record uses blocktype `unregionalblocks`
- **THEN** that entry is absent from the blocktypes taxonomy
