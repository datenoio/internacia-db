## ADDED Requirements

### Requirement: UNCTAD IIA Navigator walk

The walk of the UNCTAD IIA Navigator SHALL import every BIT row whose two parties resolve to a country or intblock record as an `investment` record at `verification: catalogue`, unless it maps to an existing investment record. A row maps to an existing record with the same two parties and the same signature date or year, or with the same signature date and a party list that contains both parties (a treaty UNCTAD splits by successor state). A mapped record gains `unctad_iia_id`, keeps its own dates and status, and notes the UNCTAD values that differ. Status SHALL map as `In force` → `in_force`, `Signed (not in force)` → `signed`, and `Terminated` → `terminated` with the termination date as `ended`, or `abandoned` with a note when the Navigator gives no date of entry into force.

#### Scenario: Official record keeps its dates

- **WHEN** the Navigator gives 1999-12-11 as the entry into force of the Georgia–United States BIT and trade.gov gives 1997-08-17
- **THEN** `GEUS-BIT` keeps `in_force: '1997-08-17'`, gains `unctad_iia_id`, and its notes give the UNCTAD date

#### Scenario: Treaty split by successor state

- **WHEN** the Navigator lists the 1990 Canada–Czechoslovakia BIT as a Czech and a Slovak row, and the registry has `CACZSK-BIT` with parties CA, CZ and SK signed on the same date
- **THEN** the first row maps to `CACZSK-BIT`, the second is reported, and no new record is written

#### Scenario: Terminated without entry into force

- **WHEN** the Navigator lists a treaty as terminated and gives no date of entry into force
- **THEN** the record is `abandoned` with a note giving the termination date
