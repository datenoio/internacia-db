## ADDED Requirements

### Requirement: Audited roster accuracy

Rosters of intblock records flagged by the 2026-08 external audit (`AFUNION`, `INTERPOL`, `CIS`, `UN`, `AIIB`, cricket `ICC`) SHALL match the membership published by the organization's official source at verification time, with `membership_count` equal to the current-member roster, correct `geographic_scope`, and membership status transitions (`former_member`, `associate_member`, `observer`, `left` dates) recorded instead of stale plain `member` entries. Each corrected field SHALL carry a provenance entry naming the official source.

#### Scenario: African Union includes SADR

- **WHEN** a consumer counts current members of `AFUNION`
- **THEN** the result is 55 and includes `EH`

#### Scenario: Interpol roster matches official count

- **WHEN** a consumer counts current members of `INTERPOL`
- **THEN** the result is 196 (matching the official member list, in which `FM` and `PW` are members and Aruba, Curaçao, and Sint Maarten appear as territory members), and `geographic_scope` is `global`

#### Scenario: CIS withdrawals recorded

- **WHEN** a consumer queries `CIS` includes for Georgia and Ukraine
- **THEN** both carry `status: former_member` with a `left` date, and Turkmenistan carries an associate status

#### Scenario: UN record is globally scoped with observers

- **WHEN** a consumer reads `political/UN.yaml`
- **THEN** `geographic_scope` is `global`, `PS` and `VA` appear with `status: observer`, and the member count remains 193

#### Scenario: Membership count matches roster for audited records

- **WHEN** validation compares `membership_count` to the includes roster for `AIIB` and cricket `ICC`
- **THEN** the values agree within the configured tolerance
