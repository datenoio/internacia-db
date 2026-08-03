## ADDED Requirements

### Requirement: UN participation status

Country records SHALL carry a `un_status` field with values `member`, `observer`, or `non_member`, consistent with the boolean `un_member` field. Exactly the UN member states SHALL be `member` (193 as of 2026), and the UN permanent observer states (`PS`, `VA`) SHALL be `observer`.

#### Scenario: Observer states distinguishable

- **WHEN** a consumer filters countries by `un_status = 'observer'`
- **THEN** exactly `PS` and `VA` are returned

#### Scenario: Status consistent with boolean flag

- **WHEN** a record has `un_status: member`
- **THEN** it also has `un_member: true`, and validation fails on any inconsistency

### Requirement: Explicit status flags on non-standard codes

The non-standard code records (`AN`, `JG`, `KV`, `XA`, `XS`, `XT`, `XN`) SHALL state explicit values for `un_member`, `independent`, and `landlocked` rather than omitting them, and their Wikidata-sourced `population` entries SHALL carry a `year`.

#### Scenario: No ambiguous absence

- **WHEN** a consumer reads `data/countries/KV.yaml`
- **THEN** `un_member`, `independent`, and `landlocked` are explicitly present

#### Scenario: Population year present

- **WHEN** a consumer reads the population of `XA`
- **THEN** the entry includes a `year` value

### Requirement: Documented disputed-territory inclusion policy

`docs/country-code-policy.md` SHALL state the inclusion rule for disputed territories that explains which de facto states receive user-assigned records and which do not, SHALL warn that the `JG` aggregate population is not the sum of `GG` and `JE`, and SHALL note the exceptionally reserved ISO codes (`EU`, `EZ`, `UN`) with a pointer to the `EU` intblock.

#### Scenario: Inclusion rule answers the Somaliland question

- **WHEN** a reader asks why Abkhazia has a record but Somaliland does not
- **THEN** the policy doc states the inclusion criterion that produces this outcome (or documents planned additions)

#### Scenario: Aggregation trap warned

- **WHEN** a consumer sums populations over records including `JG`, `GG`, and `JE`
- **THEN** the policy doc warns about the double-count
