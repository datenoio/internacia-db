## ADDED Requirements

### Requirement: No composite blocktypes

A blocktype SHALL NOT be defined as the combination of two or more other blocktypes. A record that belongs to several domains SHALL list each domain blocktype. The composite keys `eccurr` (economic and currency union) and `cuscurr` (customs and currency union) SHALL be deprecated, with replacements `[economic, currency]` and `[customs, currency]`, and SHALL stay only on their reviewed baseline records (`eccurr`: `OECS`; `cuscurr`: `CEMAC`, `UEMOA`) until the next MAJOR release.

#### Scenario: Customs union that shares a currency

- **WHEN** a contributor adds a customs union whose treaty also creates a shared currency
- **THEN** the record has `blocktype` with `customs` first and `currency` as a secondary value, and no `cuscurr`

#### Scenario: New record with a composite blocktype rejected

- **WHEN** a record outside the baseline adds `eccurr` or `cuscurr` to its `blocktype` list
- **THEN** validation reports a deprecated-blocktype ratchet error that names the record

#### Scenario: Composite blocktype as primary rejected

- **WHEN** a record has `blocktype: [eccurr, economic]`
- **THEN** validation reports that a deprecated blocktype is the primary blocktype

### Requirement: Currency union records

Every current currency union or shared-currency area SHALL have its own record with primary blocktype `currency`, whose `includes` list is the roster of countries that use the currency under that arrangement. A record with another primary blocktype SHALL carry `currency` as a secondary blocktype only when its own founding instruments establish or administer the shared currency and every full member uses it.

#### Scenario: Euro area roster

- **WHEN** a consumer needs the countries that use the euro as EU member states
- **THEN** the `EUROAREA` record lists the 21 euro area member states, and `EU` does not carry `currency`, because 6 of its 27 members do not use the euro

#### Scenario: Organization that administers its members' currency

- **WHEN** every full member of an organization uses a currency that the organization's treaties establish
- **THEN** the organization carries `currency` as a secondary blocktype, and the currency union is still a separate `currency` record
