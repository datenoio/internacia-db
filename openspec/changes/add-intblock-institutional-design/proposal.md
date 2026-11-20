# Change: Add institutional design facts to intblocks

## Why

Internacia records who belongs to an organization, but not what the organization can do to its members. A consumer cannot tell a body that adopts binding, majority-voted acts enforced by a court from a forum that issues non-binding communiqués, or from a technical union that coordinates postal rates. Size of membership does not answer this: members of UPU account for about 99% of the world's population, yet its mandate is technical.

The question "which blocs are influential and which play a technical role" has two independent axes:

- **Authority**: what the organization's founding instrument lets it decide and enforce. This is a stable, sourced, reference-like fact about the organization and belongs in intblocks.
- **Capacity**: how much population, output, or military spending its members hold. Population is already a country field; GDP, military spending, and similar indicators are explicitly out of scope for countries and stay downstream.

## What Changes

This change adds the authority axis as optional, sourced facts on intblock records. It publishes the capacity axis only as documented recipes, without new country fields.

The change has five parts:

- Add an optional `institutional_design` object to intblocks with seven subfields:
  - `mandate`: primary policy domain (`general`, `security`, `economic`, `sectoral`, `technical`).
  - `decision_rule`: the default voting rule of the principal decision-making organ.
  - `decision_force`: whether that organ's main acts bind members.
  - `independent_organs`: standing organs whose members do not act as state representatives.
  - `enforcement`: measures the organization can take against a member.
  - `mutual_defence`: whether the founding instrument contains a mutual-defence obligation.
  - `veto_holders`: members with a treaty-granted veto that other members lack.
- Add a reference catalog `data/schemas/institutional_design.yaml` that defines every value, with positive criteria and boundary examples.
- Add validation: enum checks, `none` exclusivity, `veto_holders` resolved against current members, provenance required, and the field forbidden on `reference_enumeration` and `non_state_organization` records.
- Backfill a reviewed pilot cohort of 36 high-profile records from an explicit ID-based manifest, each with field-level provenance to a founding instrument or rules of procedure.
- Document two DuckDB recipes, backed by tests:
  - **Authority level**: derive `none`/`low`/`medium`/`high` from the new facts.
  - **Member capacity concentration**: compute each bloc's share of world population, its largest member's share, the Herfindahl–Hirschman index, and the effective number of members, from the existing `countries.population`.
- Document how consumers join external indicators (GDP, military spending) by `iso3code`, without shipping that data.

The change does not add any field to countries. It does not store a composite influence score, ranking, vote shares, quotas, or budget contributions.

## Impact

The new column is additive and optional, and its enums are open under the contract's `enum_policy`. Under the versioning policy this ships as a MINOR release.

The expected repository impact is:

- Affected specs: new `intblock-institutional-design`.
- Affected source: `data/schemas/intblocks.schema.json`, new `data/schemas/institutional_design.yaml`, new pilot manifest `data/schemas/institutional_design_pilot.yaml`, and 36 records under `data/intblocks/**/*.yaml`.
- Affected code: `internacia_builder/schemas.py` (Arrow struct), `internacia_builder/export.py` (flattened CSV and lite exports), `internacia_builder/validate/intblock_rules.py`, `internacia_builder/validate/completeness.py`, a dry-run-first backfill script, and `tests/`.
- Affected documentation: `docs/intblock-inclusion-policy.md`, `docs/when-to-use-internacia.md`, `docs/ai-consumers.md`, `docs/query-examples.md` (with `tests/test_documented_queries.py`), `docs/data-dictionary.md` (generated), `llms.txt`, agent-shim templates, and `CHANGELOG.md`.
- Affected exports: all intblock formats gain the `institutional_design` struct column; `contract.json` gains the open enums for its subfields automatically from the JSON Schema.
- Not breaking: existing columns, IDs, and memberships do not change. Consumers that use `SELECT *` into a fixed-width schema see one new column.
