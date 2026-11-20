## ADDED Requirements

### Requirement: Infrastructure include roles

Intblock `includes` entries MAY carry an optional `role` with one of the values `origin`, `transit`, or `destination`, defined in `data/schemas/include_roles.yaml`. The JSON Schema enum and the catalog keys SHALL be identical, and `contract.json` SHALL list `includes[].role` as an open enum. A `role` SHALL appear only on records whose `blocktype` includes `gaspipeline`. `origin` SHALL mean the route starts in that country, `transit` that the route crosses it and continues into another country, and `destination` that the route ends there; offtake along the route SHALL NOT change a `transit` role.

#### Scenario: Pipeline roles are valid

- **WHEN** a `gaspipeline` record gives AZ `role: origin`, GE `role: transit`, and TR `role: destination`, with provenance
- **THEN** validation passes

#### Scenario: Role on a non-infrastructure record

- **WHEN** an `igo` record without the `gaspipeline` blocktype gives an include `role: transit`
- **THEN** the intblock validator reports an error

#### Scenario: Unknown role

- **WHEN** an include declares `role: supplier`
- **THEN** JSON Schema validation rejects the record

#### Scenario: Role catalog matches the schema

- **WHEN** the test suite compares `include_roles.yaml` with the JSON Schema enum
- **THEN** the key sets are identical

### Requirement: Complete roles per infrastructure record

When any current country entry of a record has a `role`, every current country entry of that record SHALL have one. The record SHALL then have at least one `origin` and at least one `destination`. Every record with roles SHALL have a `provenance` entry with `field: includes` that cites the route.

#### Scenario: Partial roles

- **WHEN** a pipeline record gives roles to two of its three current country entries
- **THEN** the intblock validator reports an error naming the entry without a role

#### Scenario: Missing destination

- **WHEN** every role on a pipeline record is `origin` or `transit`
- **THEN** the intblock validator reports an error

#### Scenario: Missing route provenance

- **WHEN** a pipeline record has roles but no provenance entry with `field: includes`
- **THEN** the intblock validator reports an error

### Requirement: Reviewed infrastructure role backfill

The role backfill SHALL apply values only from an explicit, versioned manifest that gives a role for every current country entry of each listed record and a source URL for each record. The backfill CLI SHALL be non-mutating by default, SHALL validate the whole cohort before writing, SHALL abort the whole apply on any conflicting existing role, SHALL be idempotent, and SHALL change only `includes[].role` and `provenance`. Records whose route the sources do not settle SHALL be listed as deferred with a reason.

#### Scenario: Default invocation is a dry run

- **WHEN** a maintainer runs the role backfill without `--apply`
- **THEN** it reports planned roles and writes no intblock YAML

#### Scenario: Conflicting role blocks apply

- **WHEN** a manifest role differs from an existing role on the same include
- **THEN** the CLI reports the conflict, exits non-zero, and writes no file

#### Scenario: Only roles change

- **WHEN** the reviewed manifest is applied
- **THEN** the diff of each changed record touches only `includes[].role` and `provenance`

### Requirement: Sea-access gateway recipe

The query documentation SHALL include a tested DuckDB recipe that returns, for every official landlocked country, each first-hop neighbour that lies on a crossable path to a coastal country, the smallest number of borders from that neighbour to a coast, whether the path crosses a `restricted` border, the count of direct coastal gateways, and a flag for a single direct coastal gateway. A coastal country SHALL be an official country with `landlocked = false`, and a border SHALL be crossable unless its current `border_status` is `closed`. The documentation SHALL state that the result is a structural lower bound that ignores corridors, capacity, cost, and sanctions.

#### Scenario: Single gateway

- **WHEN** the recipe runs on the current data
- **THEN** Lesotho has exactly one direct coastal gateway, ZAF

#### Scenario: Doubly landlocked

- **WHEN** the recipe runs on the current data
- **THEN** Liechtenstein and Uzbekistan have no direct coastal gateway and a smallest distance of two borders

#### Scenario: Closed borders remove gateways

- **WHEN** `border_status` records the ARM–TUR and ARM–AZE borders as `closed`
- **THEN** Armenia's direct coastal gateways are GEO and IRN only

#### Scenario: Lower-bound caveat is documented

- **WHEN** a consumer reads the recipe
- **THEN** the documentation states that it is not a route model and gives a counter-example

### Requirement: Trade dependence is documented and downstream

The consumer documentation SHALL define partner share, asymmetry, exposure, partner concentration, and in-bloc leverage for an externally loaded bilateral trade table. It SHALL state that import dependence gives leverage to the supplier and export dependence to the buyer. It SHALL list candidate sources with their redistribution terms, and SHALL show a join on `countries.iso3code` and `current_memberships`. Internacia SHALL NOT store trade values, shares, balances, transit volumes, or route capacity.

#### Scenario: Join pattern documented

- **WHEN** a consumer reads the trade dependence section
- **THEN** it finds the measure definitions and a join pattern on `iso3code`, marked as needing external data

#### Scenario: No trade data in exports

- **WHEN** the intblocks, countries, and `border_status` exports are inspected
- **THEN** none has a trade value, share, balance, volume, or capacity column
