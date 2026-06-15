## ADDED Requirements

### Requirement: Tier 2 high-priority intblock coverage

The intblocks dataset SHALL include records for the six Tier 2 gaps identified in `dev/research/report_manus_20260615.md`: `CHIP4`, `DEPA`, `PEPFAR`, `MSF`, `UNCITRAL`, and `UNCLOS`.

#### Scenario: Digital alliance record exists

- **WHEN** a consumer queries intblocks by `id: CHIP4`
- **THEN** a source record exists describing the semiconductor coordination alliance

#### Scenario: Digital trade agreement exists

- **WHEN** a consumer queries intblocks by `id: DEPA`
- **THEN** a source record exists for the Digital Economy Partnership Agreement

#### Scenario: Major health program exists

- **WHEN** a consumer queries intblocks by `id: PEPFAR`
- **THEN** a source record exists with documented membership or partner-country model

#### Scenario: Humanitarian NGO exists

- **WHEN** a consumer queries intblocks by `id: MSF`
- **THEN** a source record exists for Médecins Sans Frontières with appropriate non-IGO classification

#### Scenario: Trade law body exists

- **WHEN** a consumer queries intblocks by `id: UNCITRAL`
- **THEN** a source record exists for the UN Commission on International Trade Law

#### Scenario: Law of the Sea treaty exists

- **WHEN** a consumer queries intblocks by `id: UNCLOS`
- **THEN** a source record exists for the UN Convention on the Law of the Sea with party membership
