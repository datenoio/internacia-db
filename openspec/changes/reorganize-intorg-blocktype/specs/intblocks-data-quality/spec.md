## ADDED Requirements

### Requirement: Blocktype semantics

A blocktype SHALL describe the domain or function of an intblock, not its entity form. Entity form (IGO, treaty, forum, non-state organization) SHALL be recorded only in `scope_category`. A new blocktype whose meaning is an entity form SHALL NOT be added to `data/blocktypes/blocktypes.yaml`.

#### Scenario: Domain blocktype for an IGO

- **WHEN** a contributor adds a regional fisheries management organization that is an IGO
- **THEN** the record is stored under `data/intblocks/fisheries/` with `scope_category: igo`, and no blocktype says that it is an IGO

#### Scenario: Consumer filters by entity form

- **WHEN** a consumer needs all intergovernmental organizations
- **THEN** the documentation directs them to `scope_category = 'igo'`, not to a blocktype

### Requirement: Blocktype scope notes

Every entry in `data/blocktypes/blocktypes.yaml` SHALL have a non-empty English `description` that states what the blocktype includes. Where two blocktypes overlap, each description SHALL state the boundary between them. Validation SHALL report an entry without a `description` as an error.

#### Scenario: Missing description rejected

- **WHEN** a blocktype entry has no `description`
- **THEN** intblock validation reports an error that names the blocktype

#### Scenario: Overlapping keys state a boundary

- **WHEN** a contributor must choose between `maritime`, `ocean` and `fisheries`
- **THEN** each of the three descriptions says what belongs to it and what belongs to the other two

### Requirement: Deprecated blocktype usage

A blocktype entry MAY carry a `deprecated` marker with `replacements`, `removal` and `note`. A deprecated blocktype SHALL NOT be the primary (first) blocktype of any record. The set of records that carry a deprecated blocktype SHALL equal the reviewed baseline set of IDs, except IDs that the alias file marks as merged or retired. Validation SHALL report any violation as an error.

#### Scenario: Deprecated blocktype as primary rejected

- **WHEN** a record has `blocktype: [intorg, health]` and `intorg` is deprecated
- **THEN** validation reports that a deprecated blocktype is the primary blocktype

#### Scenario: Secondary use within the baseline passes

- **WHEN** a record in the 358-ID baseline has `blocktype: [fisheries, intorg]`
- **THEN** validation passes, because the record existed when `intorg` was deprecated

#### Scenario: New record with a deprecated blocktype rejected

- **WHEN** a record that is not in the baseline adds `intorg` to its `blocktype` list
- **THEN** validation reports a deprecated-blocktype ratchet error that names the record

#### Scenario: Baseline record drops a deprecated blocktype early

- **WHEN** a baseline record removes `intorg` from its `blocktype` list before the MAJOR release
- **THEN** validation reports a deprecated-blocktype ratchet error that names the record

## MODIFIED Requirements

### Requirement: Blocktype taxonomy validation

Every entry in an intblock's `blocktype` list SHALL reference a defined blocktype in the blocktypes **source** taxonomy file under `data/blocktypes/` (not the generated datasets copy).

#### Scenario: Valid blocktype accepted

- **WHEN** an intblock has `blocktype: [fisheries]` and `fisheries` exists in `data/blocktypes/blocktypes.yaml`
- **THEN** blocktype validation passes

#### Scenario: Unknown blocktype rejected

- **WHEN** an intblock references a blocktype not in the source taxonomy
- **THEN** validation reports a blocktype reference error
