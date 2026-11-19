## MODIFIED Requirements

### Requirement: Include name is display label only

For intblock `includes` entries with `type: country`, the `id` field SHALL be treated as the authoritative join key to country records. The exported `name` of such an entry SHALL be the referenced country's `name`, filled by the build. The source `name` is optional for `type: country` entries; when present it SHALL equal the country `name`, and a differing value SHALL be reported as an `INCLUDE_NAME_MISMATCH` warning without failing validation. Entries of other types keep their source `name`.

#### Scenario: Stale source name exported as the country name

- **WHEN** an include has `id: MK`, `type: country`, `name: Macedonia, FYR`, and the country record has `name: North Macedonia`
- **THEN** the exported `includes[].name` is `North Macedonia`, and validation reports an `INCLUDE_NAME_MISMATCH` warning with exit status unaffected

#### Scenario: Country entry without a name

- **WHEN** an include has `id: FR` and `type: country` and no `name`
- **THEN** source validation passes and the exported `includes[].name` is the country `name` of FR

#### Scenario: Identifier mismatch fails validation

- **WHEN** an include has `id: ZZ` and `type: country` with no matching country or allowlist entry
- **THEN** cross-dataset validation reports an unresolved reference

#### Scenario: Mismatch report summarizes volume

- **WHEN** the quality analyzer runs against all intblock sources
- **THEN** the `INCLUDE_NAME_MISMATCH` rule report includes the total mismatch count and per-record examples

#### Scenario: Organization entry keeps its label

- **WHEN** an include has `type: organization` and `name: European Union`
- **THEN** the exported `includes[].name` is `European Union`

### Requirement: Include display-name advisory rule

The validators and the quality analyzer SHALL report intblock `includes[].name` values of `type: country` entries that differ from the referenced country's `name` as `INCLUDE_NAME_MISMATCH` at LOW priority and warning severity. The comparison SHALL be exact. The rule SHALL NOT fail validation.

#### Scenario: Display name mismatch reported as a warning

- **WHEN** an include has `id: TR`, `name: Turkey`, and the country record has `name: Türkiye`
- **THEN** validation reports an `INCLUDE_NAME_MISMATCH` warning and validation exit status is unaffected
