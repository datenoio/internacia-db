## ADDED Requirements

### Requirement: Country writing direction attributes

Country records SHALL represent dominant writing direction(s) on the country record via optional `writing_directions`, an array of objects with required `id` (controlled vocab) and optional `primary` (boolean). Values SHALL resolve against the writing-directions vocab catalog. This field replaces inverted `writingdirection` intblock membership.

#### Scenario: Japan has horizontal and vertical directions

- **WHEN** Japan’s country record is migrated from writingdirection intblocks
- **THEN** `writing_directions` includes vocab ids for left-to-right and top-to-bottom, with one marked `primary: true` when a primary convention is known

#### Scenario: Single-direction country

- **WHEN** a country appears only in the LTR writingdirection intblock at migration time
- **THEN** `writing_directions` contains a single entry with id `ltr`

### Requirement: Country writing system attributes

Country records SHALL represent official or widely used writing system(s) via optional `writing_systems`, an array of objects with required `id` and optional `primary`. Values SHALL resolve against the writing-systems vocab catalog. This field replaces inverted `writingsystem` intblock membership.

#### Scenario: Israel lists Hebrew and Arabic scripts

- **WHEN** Israel’s record is migrated from writingsystem intblocks
- **THEN** `writing_systems` includes both `hebrew` and `arabic` vocab ids

### Requirement: Country DVD region attribute

Country records SHALL store commercial DVD region as optional `dvd_region`, an integer in the closed range 1–6 when assigned. Absence MUST mean unknown or unassigned. This field replaces inverted `dvdregion` intblock membership.

#### Scenario: United States is DVD region 1

- **WHEN** the United States record is migrated from `DVD_1`
- **THEN** `dvd_region` is `1`

#### Scenario: Unassigned territory omits field

- **WHEN** a territory was not present in any dvdregion includes roster and no authoritative assignment is applied
- **THEN** `dvd_region` is omitted or null and validation does not fail in warn-mode completeness

### Requirement: Country broadcast system attributes

Country records SHALL represent terrestrial/digital television system(s) via optional `broadcast_systems`, an array of objects with required `id` resolving against the broadcast-systems vocab. This field replaces inverted `teleregion` intblock membership.

#### Scenario: United States lists ATSC and NTSC

- **WHEN** the United States record is migrated from teleregion intblocks
- **THEN** `broadcast_systems` includes vocab ids corresponding to former `ATSC` and `NTSC` intblocks

### Requirement: Country legal system attributes

Country records SHALL represent legal tradition(s) via optional `legal_systems`, an array of objects with required `id` resolving against the legal-systems vocab. This field replaces inverted `lawsystem` intblock membership. Government form / regime typology SHALL NOT be added under this requirement.

#### Scenario: Mixed jurisdiction lists multiple systems

- **WHEN** Cameroon appears in multiple lawsystem intblocks at migration
- **THEN** `legal_systems` contains multiple vocab ids reflecting those memberships

#### Scenario: Government form excluded

- **WHEN** this change is applied
- **THEN** country schema does not gain a `government_form` or `govform` field

### Requirement: Country rail gauge attributes

Country records SHALL represent railway track gauge(s) in use via optional `rail_gauges`, an array of objects with required `id`, optional `gauge_mm` (positive number), and optional `primary`. Ids SHALL resolve against the rail-gauges vocab. This field replaces inverted `railgauge` intblock membership.

#### Scenario: Russian-gauge countries retain millimeter metadata

- **WHEN** a country migrated from `RUGAUGE` has vocab id `russian`
- **THEN** the entry includes `gauge_mm: 1520` when the vocab or migration mapping supplies it

### Requirement: Driving side remains country-owned

`car_side` (`left` | `right`) SHALL remain the sole source of truth for traffic-hand / driving-side classification. After migration, no `traffichand` intblock SHALL exist, and consumers SHALL NOT need intblock joins for this attribute.

#### Scenario: Left-hand traffic country

- **WHEN** a consumer queries countries that drive on the left
- **THEN** they filter `car_side = 'left'` and do not join intblocks

#### Scenario: Traffichand retired

- **WHEN** the attribute intblock retirement completes
- **THEN** `data/intblocks/traffichand/` no longer exists
