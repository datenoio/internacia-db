# border-crossing-status Specification

## Purpose

Record which land borders are closed or restricted to regular traffic, as an edge dataset over `countries.borders` with dates and official sources. Export it as the `border_status` table and the `country_borders` view. Absence of an entry means that no closure is recorded, not that the border is verified open, and the status never judges the legitimacy of a closure, a boundary or a state.

## Requirements
### Requirement: Border crossing status source

The repository SHALL keep land-border crossing status in `data/borders/border_status.yaml`, validated by `data/schemas/border_status.schema.json`, and SHALL NOT add a border status field to country records. The file SHALL hold an `entries` list and MAY hold a `deferred` map of candidate pairs with reasons. Each entry SHALL have `countries` (a sorted pair of distinct `iso3code` values), `status` (`closed` or `restricted`), an optional `since` (omitted when no qualifying source gives the start), an optional `until`, an optional `note`, `last_verified`, and a non-empty `provenance` list. `closed` SHALL mean that no land crossing on that border is open to regular traffic of goods; `restricted` SHALL mean that at least one crossing is closed or that traffic is limited to named categories. Absence of an entry SHALL mean that no closure is recorded, not that the border is verified open.

#### Scenario: Valid closure

- **WHEN** an entry records `countries: [ARM, TUR]`, `status: closed`, `since: '1993'`, with an official source
- **THEN** validation passes

#### Scenario: Unknown status

- **WHEN** an entry declares `status: partially_open`
- **THEN** JSON Schema validation rejects the entry

#### Scenario: Country records unchanged

- **WHEN** `countries.schema.json` is inspected after this change
- **THEN** it defines no border status property

### Requirement: Border status integrity

Each `border_status` pair SHALL resolve to two existing country records, and each country SHALL list the other in `borders`. A border SHALL have at most one entry; when a border closes again after reopening, the ended entry SHALL be replaced. An entry with `until` SHALL have `since`, and `since` SHALL NOT be after `until`. Every entry SHALL cite a government, an intergovernmental organization, or an official border or customs authority. An entry older than the configured freshness threshold SHALL be reported as a warning.

#### Scenario: Non-adjacent pair

- **WHEN** an entry pairs two countries that do not list each other in `borders`
- **THEN** the validator reports an error

#### Scenario: Two entries for one border

- **WHEN** two entries name the same pair
- **THEN** the validator reports an error

#### Scenario: Reopened border keeps history

- **WHEN** a closure entry gains an `until` date and no later entry exists for the pair
- **THEN** validation passes and the pair has no current status

#### Scenario: Missing provenance

- **WHEN** an entry has an empty `provenance` list
- **THEN** JSON Schema validation rejects the entry

### Requirement: Border status export and view

The build SHALL export `border_status` like the alias artifacts: a committed `border_status.json`, a `border_status.parquet`, and a DuckDB table, all listed in `datapackage.json`. The table SHALL have the primary key (`country_a`, `country_b`), foreign keys from `country_a` and `country_b` to `countries.iso3code`, and an open enum for `status` in `contract.json`. The DuckDB export SHALL include a view `country_borders` with one row per entry of `countries.borders` and the pair's current status (from the entry with no `until`), or NULL when none is recorded.

#### Scenario: Current status in the view

- **WHEN** a consumer queries `country_borders` for `country_code = 'AM'`
- **THEN** it gets one row per Armenian neighbour, with `closed` for each recorded current closure and NULL for the others

#### Scenario: Historical closure is not current

- **WHEN** a pair's only entry has an `until` date
- **THEN** `country_borders` shows NULL status for that pair

### Requirement: Reviewed border status pilot

Border status entries SHALL be added only after review of each candidate pair against an official source, with the date checked. Candidates without such a source SHALL be listed in the file's `deferred` map with a reason. Notes SHALL describe whether crossings are open and SHALL NOT judge the legitimacy of a closure, a boundary, or a state.

#### Scenario: Candidate without official source

- **WHEN** a candidate closure has only news or think-tank sources
- **THEN** it is listed as deferred and no entry is added

#### Scenario: Neutral note

- **WHEN** a reviewer writes a `note` for a closure
- **THEN** the note states which crossings are closed and since when, without attributing blame

