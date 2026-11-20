## ADDED Requirements

### Requirement: Optional institutional design object

Intblock records MAY include an `institutional_design` object. The object SHALL accept only the subfields `mandate`, `decision_rule`, `decision_force`, `independent_organs`, `enforcement`, `mutual_defence`, and `veto_holders`, and every subfield SHALL be optional. An absent object or subfield SHALL mean that the value is unknown, not that the organization lacks the feature.

#### Scenario: Record without the object is valid

- **WHEN** an intblock record has no `institutional_design`
- **THEN** JSON Schema validation and the intblock validator pass for that field

#### Scenario: Unknown subfield is rejected

- **WHEN** an `institutional_design` object contains a key outside the seven documented subfields
- **THEN** JSON Schema validation rejects the record

#### Scenario: Partial object is valid

- **WHEN** an `institutional_design` object contains only `mandate` and `decision_force`, with provenance
- **THEN** validation passes and the other subfields export as null

### Requirement: Institutional design value catalog

Every enumerated `institutional_design` value SHALL be defined in `data/schemas/institutional_design.yaml` with a meaning, positive criteria, and at least one boundary example. The JSON Schema enums and the catalog keys SHALL be identical. The enumerations SHALL be:

- `mandate`: `general`, `security`, `economic`, `sectoral`, `technical`
- `decision_rule`: `consensus`, `unanimity`, `simple_majority`, `qualified_majority`, `weighted_voting`, `mixed`
- `decision_force`: `binding`, `partly_binding`, `non_binding`
- `independent_organs[]`: `executive`, `court`, `dispute_panel`, `parliament`, `central_bank`, `none`
- `enforcement[]`: `sanctions`, `suspension`, `expulsion`, `conditionality`, `none`

`mutual_defence` SHALL be a boolean. `veto_holders` SHALL be a list of country alpha-2 codes.

#### Scenario: Catalog and schema agree

- **WHEN** the test suite compares the JSON Schema enums with the catalog keys
- **THEN** every schema value has a catalog entry and every catalog entry is a schema value

#### Scenario: Unknown enum value is rejected

- **WHEN** a record declares `decision_rule: majority`
- **THEN** JSON Schema validation rejects the record

#### Scenario: Enums are open in the consumer contract

- **WHEN** `contract.json` is generated
- **THEN** it lists each `institutional_design` subfield enum with `"open": true`

### Requirement: Principal-organ convention

`decision_rule` and `decision_force` SHALL describe the principal decision-making organ, which is the organ of member-state representatives that adopts the organization's main acts. When the founding instrument sets different rules for different areas, the record SHALL use the default rule for the main acts. `mixed` SHALL be used only when the instrument sets no default.

#### Scenario: Default rule wins over exceptions

- **WHEN** a founding instrument sets qualified majority as the default for the principal organ and unanimity for a listed set of areas
- **THEN** the record's `decision_rule` is `qualified_majority`

#### Scenario: No default rule

- **WHEN** a founding instrument assigns different voting rules to its core areas and names no default
- **THEN** the record's `decision_rule` is `mixed`

### Requirement: Exclusive none value

In `independent_organs` and `enforcement`, the value `none` SHALL appear only as the single element of the list. List values SHALL be unique.

#### Scenario: None combined with another value

- **WHEN** a record declares `enforcement: [none, suspension]`
- **THEN** the intblock validator reports an error

#### Scenario: Duplicate list value

- **WHEN** a record declares `independent_organs: [court, court]`
- **THEN** the intblock validator reports an error

### Requirement: Asymmetric veto holders

`veto_holders` SHALL list only members that hold a treaty-granted veto that other members lack. Each code SHALL resolve to a current country member of the same record: a country `includes` entry with no `left` date and a `member` or `founding_member` status. Consensus and unanimity SHALL NOT be recorded as veto holders. De-facto vetoes that follow from voting weight SHALL NOT be recorded.

#### Scenario: Permanent member holds a veto

- **WHEN** a record lists `US` in `veto_holders` and `US` is a current country member of that record
- **THEN** validation passes

#### Scenario: Veto holder is not a member

- **WHEN** a record lists a country code in `veto_holders` that is not a current country member of the record
- **THEN** the intblock validator reports an error

#### Scenario: Veto holders under consensus

- **WHEN** a record has a non-empty `veto_holders` and `decision_rule` is `consensus` or `unanimity`
- **THEN** the intblock validator reports a warning

### Requirement: Institutional design scope by entity kind

`institutional_design` SHALL be allowed only on records whose `scope_category` is `igo`, `treaty_body`, `policy_forum`, or `intergovernmental_body`. It SHALL NOT appear on `reference_enumeration` or `non_state_organization` records. On a record with `status: historical`, it SHALL describe the design at dissolution.

#### Scenario: Reference enumeration carries the object

- **WHEN** a record with `scope_category: reference_enumeration` declares `institutional_design`
- **THEN** the intblock validator reports an error

#### Scenario: Non-state organization carries the object

- **WHEN** a record with `scope_category: non_state_organization` declares `institutional_design`
- **THEN** the intblock validator reports an error

#### Scenario: Policy forum carries the object

- **WHEN** a record with `scope_category: policy_forum` declares `decision_force: non_binding` with provenance
- **THEN** validation passes

### Requirement: Institutional design provenance

A record that declares `institutional_design` SHALL have at least one `provenance` entry whose `field` is `institutional_design` or starts with `institutional_design.`. The entry SHALL cite a founding instrument, rules of procedure, or an official organization source.

#### Scenario: Missing provenance

- **WHEN** a record declares `institutional_design` and has no matching provenance entry
- **THEN** the intblock validator reports an error

#### Scenario: Subfield provenance satisfies the rule

- **WHEN** a record declares `institutional_design` and has a provenance entry with `field: institutional_design.decision_rule`
- **THEN** the provenance rule passes

### Requirement: Institutional design export

The `institutional_design` object SHALL be exported as a struct column in Parquet, DuckDB, and JSONL intblock exports. The flattened CSV and lite exports SHALL carry one column per subfield, and SHALL join list subfields with the delimiter used for other flattened lists. The JSON Schema and the Arrow schema SHALL stay in parity without a new allowlist entry.

#### Scenario: Populated record in DuckDB

- **WHEN** a consumer queries `SELECT institutional_design.decision_rule FROM intblocks WHERE id = '<pilot id>'`
- **THEN** the query returns the value from the source record

#### Scenario: Absent object in DuckDB

- **WHEN** a consumer queries `institutional_design` for a record that has no such object
- **THEN** the query returns NULL

#### Scenario: Schema parity

- **WHEN** the schema-parity test runs
- **THEN** `institutional_design` is present in both schemas and the test passes

### Requirement: Reviewed institutional design pilot

The first backfill SHALL apply values only from an explicit, versioned manifest `data/schemas/institutional_design_pilot.yaml`. The manifest SHALL declare its expected record count and SHALL give a primary-source URL for every record. The backfill CLI SHALL be non-mutating by default, SHALL validate the whole cohort before writing, SHALL abort the whole apply when any record already has a different value, SHALL be idempotent, and SHALL insert provenance with each value. The CLI SHALL NOT infer values from `blocktype`, directory, or `topics`.

#### Scenario: Default invocation is a dry run

- **WHEN** a maintainer runs the backfill CLI without `--apply`
- **THEN** the CLI reports the planned changes and writes no intblock YAML

#### Scenario: Unknown manifest ID

- **WHEN** a manifest ID does not resolve to exactly one source record
- **THEN** the CLI exits non-zero before writing any file

#### Scenario: Conflicting existing value

- **WHEN** any manifest record already has a different `institutional_design` value
- **THEN** the CLI reports the conflict, exits non-zero, and writes none of the files

#### Scenario: Pilot applied

- **WHEN** the reviewed pilot manifest is applied
- **THEN** exactly the manifest's records change, each gains a matching provenance entry, and no roster, name, or hierarchy changes

### Requirement: Authority level recipe

The query documentation SHALL include a tested DuckDB recipe that derives an authority level per intblock from `scope_category` and `institutional_design`. The rule SHALL be applied in this order:

1. `none` when `scope_category` is `reference_enumeration`.
2. NULL when `decision_force` is absent.
3. `low` when `decision_force` is `non_binding`.
4. `high` when `decision_force` is `binding` and at least one holds: `decision_rule` is `simple_majority`, `qualified_majority`, or `weighted_voting`; `independent_organs` contains `executive` or `court`; `enforcement` contains `sanctions` or `conditionality`.
5. `medium` otherwise.

The documentation SHALL state that the authority level measures institutional authority, not influence, and SHALL NOT be exported as a column in this change.

#### Scenario: Non-binding forum

- **WHEN** the recipe runs on a record with `decision_force: non_binding`
- **THEN** the record's level is `low`

#### Scenario: Binding majority decisions

- **WHEN** the recipe runs on a record with `decision_force: binding` and `decision_rule: qualified_majority`
- **THEN** the record's level is `high`

#### Scenario: Binding consensus without independent organs

- **WHEN** the recipe runs on a record with `decision_force: binding`, `decision_rule: consensus`, `independent_organs: [none]`, and `enforcement: [none]`
- **THEN** the record's level is `medium`

#### Scenario: Unknown design

- **WHEN** the recipe runs on an `igo` record without `institutional_design`
- **THEN** the record's level is NULL

### Requirement: Member capacity concentration recipe

The query documentation SHALL include a tested DuckDB recipe that computes, per intblock, from current `member` and `founding_member` country rows with a known population:

- the bloc's share of world population, with official ISO countries as the denominator;
- the largest member and its share of the bloc's population;
- the Herfindahl–Hirschman index of member population shares;
- the effective number of members (1/HHI);
- the minimum and maximum `population.year` used.

The recipe SHALL use only data already in scope. The documentation SHALL state that population concentration is not power.

#### Scenario: Single-member dominance

- **WHEN** the recipe runs on a bloc in which one member holds most of the bloc's population
- **THEN** that member is reported as the largest member, and the effective number of members is close to 1

#### Scenario: Population years reported

- **WHEN** the recipe runs on any bloc
- **THEN** the output includes the minimum and maximum `population.year` of the rows used

### Requirement: Capacity indicators stay downstream

This capability SHALL NOT add GDP, military spending, armed-forces size, nuclear status, or any similar indicator to countries or intblocks. It SHALL NOT store composite influence scores, rankings, vote shares, quotas, or budget contribution scales. The consumer documentation SHALL show how to join an external indicator table on `countries.iso3code`, and SHALL state that no indicator data ships with Internacia.

#### Scenario: Countries schema unchanged

- **WHEN** `countries.schema.json` is inspected after this change ships
- **THEN** it defines no GDP, military, or influence property

#### Scenario: External indicator join documented

- **WHEN** a consumer reads the consumer documentation for capacity indicators
- **THEN** it finds a join pattern on `countries.iso3code` and a statement that the indicator data comes from an external source
