# Change: Add identifier stability policy and alias map

## Why

Intblock identifiers are custom and have already churned: v1.3.0 renamed `ASF`→`FSA` and
`CAF`→`CAFBANK` and merged 8 duplicate records, which the CHANGELOG flags as **breaking for
consumers joining on ids**. There is no machine-readable map from retired/renamed ids to current
ids, so downstream joins (Dateno enrichment, SDK, API) break silently on upgrade and there is no
documented policy governing when ids may change.

See [docs/strategy-and-user-needs.md](../../../docs/strategy-and-user-needs.md) §4.2 / Track A2.

## What Changes

- Define an **identifier stability policy**: country `code` and intblock `id` are stable join keys;
  when an id must change (rename/merge), the old id SHALL be recorded as an alias rather than removed
  without trace.
- Add a generated **alias artifact** `data/datasets/intblocks_aliases.{json,parquet}` mapping each
  retired/renamed id to its current id, with `reason` (`renamed`|`merged`) and `since` version.
- Maintain alias entries in a source file (e.g. `data/intblocks_aliases.yaml`) authored alongside the
  rename/merge that introduces them; the builder exports the derived artifacts.
- Validate in CI that every alias `target` resolves to an existing intblock id and that no current id
  collides with a retired alias.
- Publish the alias artifact as a GitHub Release asset (extend `dataset-release`).

## Impact

- Affected specs: `dataset-release` (added), `cross-dataset-integrity` (added)
- Affected code: `data/intblocks_aliases.yaml` (source), `scripts/builder.py`,
  `scripts/validate_intblocks.py`, `.github/workflows/release.yml`, tests
- Breaking: None (additive artifact; gives consumers a migration path for prior breaking renames)
