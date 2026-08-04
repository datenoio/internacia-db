## ADDED Requirements

### Requirement: Attribute partitions excluded from intblocks

The intblocks dataset SHALL NOT contain records whose primary purpose is to encode a country attribute partition for DVD region, government form, legal system, rail gauge, television/broadcast system, traffic hand, writing direction, or writing system. Those classifications SHALL live on country records and/or vocab catalogs. Named geographic or set groupings MAY remain as intblocks with `scope_category: reference_enumeration`.

#### Scenario: Traffichand directory removed

- **WHEN** a consumer lists `data/intblocks/` after this change ships
- **THEN** no `traffichand` category directory exists

#### Scenario: Geographic reference enumeration retained

- **WHEN** a consumer filters intblocks with `scope_category = 'reference_enumeration'`
- **THEN** geographic groupings such as SIDS remain available and attribute-partition blocktypes do not

#### Scenario: Blocktype taxonomy drops attribute types

- **WHEN** `data/blocktypes/blocktypes.yaml` is read after retirement
- **THEN** it does not define `dvdregion`, `govform`, `lawsystem`, `railgauge`, `teleregion`, `traffichand`, `writingdirection`, or `writingsystem`

### Requirement: Government form not modeled as country org membership

`govform` intblock records SHALL be retired from the intblocks corpus. Government-form typology SHALL NOT be reintroduced as intblock membership rosters. Optional vocab-only preservation of form definitions is permitted without country `includes` and without adding government-type fields to countries.

#### Scenario: No govform includes after retirement

- **WHEN** intblocks validation runs after this change
- **THEN** no intblock file under a `govform` blocktype exists

#### Scenario: Countries remain without government type field

- **WHEN** `countries.schema.json` is inspected after this change
- **THEN** it does not define government form / govform properties
