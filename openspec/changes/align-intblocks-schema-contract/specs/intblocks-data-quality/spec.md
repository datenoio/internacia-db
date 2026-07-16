## MODIFIED Requirements

### Requirement: Intblock YAML JSON Schema validation

Every file under `data/intblocks/**/*.yaml` SHALL validate against `data/schemas/intblocks.schema.json` before dataset export. The JSON Schema SHALL declare the canonical intblock field set, and its top-level `additionalProperties` SHALL be `false` (or a documented narrow allowlist) so that undeclared fields are rejected rather than silently accepted.

#### Scenario: Valid intblock file passes schema

- **WHEN** `validate_intblocks.py` runs on a well-formed intblock YAML file using only declared fields
- **THEN** validation reports no schema errors for that file

#### Scenario: Invalid intblock file fails schema

- **WHEN** an intblock YAML file has a required field with wrong type
- **THEN** validation reports a schema error and exits with non-zero status

#### Scenario: Undeclared field rejected

- **WHEN** an intblock YAML file contains a key that is not part of the canonical declared field set
- **THEN** validation reports an additional-property error rather than silently accepting the field

## ADDED Requirements

### Requirement: Schema and export field parity

The intblock JSON Schema properties and the Arrow export schema field names SHALL be kept in parity, verified by an automated test with an explicit allowlist for documented source-only or export-normalized fields.

#### Scenario: Export field missing from JSON Schema fails parity

- **WHEN** the Arrow export schema exports a field that is neither declared in the JSON Schema nor on the parity allowlist
- **THEN** the schema-parity test fails

#### Scenario: Declared canonical field is exported

- **WHEN** a field is declared canonical in the JSON Schema and is not source-only
- **THEN** the Arrow export schema includes that field and the parity test passes
