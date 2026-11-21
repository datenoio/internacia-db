## ADDED Requirements

### Requirement: Artificial intelligence blocktype

The blocktype taxonomy SHALL define `artificial_intelligence` with an English `description` that covers artificial intelligence governance, safety and cooperation, including partnerships on AI compute and semiconductor supply chains. The key SHALL be an additional (secondary) blocktype: no `data/intblocks/artificial_intelligence/` directory SHALL exist, and adding the key SHALL NOT change a record's primary blocktype. A record SHALL carry the key when artificial intelligence is its main subject, and SHALL NOT carry it when AI is one topic among several. The `digital` scope note SHALL point AI bodies to the key.

#### Scenario: Consumer selects AI bodies

- **WHEN** a consumer runs `SELECT id FROM intblocks WHERE list_contains(blocktype, 'artificial_intelligence')`
- **THEN** the result includes `WAICO`, `PAXSILICA`, `CHIP4`, `GPAI`, `NAAIMES`, `HAIPFRIENDS`, `OECDAIPRINCIPLES`, `MILITARYAIDECLARATION` and `COEAICONVENTION`

#### Scenario: Primary blocktype is kept

- **WHEN** `artificial_intelligence` is added to `GPAI`
- **THEN** the record stays in `data/intblocks/forum/` with `forum` as its first blocktype

#### Scenario: Incidental AI coverage is not tagged

- **WHEN** a record covers AI as one area among several, such as `AUKUS` (Pillar II) or `DEPA` (an AI module)
- **THEN** the record does not carry `artificial_intelligence`

#### Scenario: Deprecated blocktype stays last

- **WHEN** `artificial_intelligence` is added to a record in the `intorg` baseline, such as `WAICO`
- **THEN** it is inserted before `intorg`, and `intorg` remains the last blocktype
