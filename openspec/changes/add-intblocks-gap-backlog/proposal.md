# Change: Process intblocks gap backlog

## Why

Gap analysis (`dev/research/gaps_merged_20260528.md`) deferred ~15 candidates pending scope, sourcing, or historical-status decisions. No tracked backlog ties research findings to implementation work.

See [docs/improvement-plan.md](../../../docs/improvement-plan.md) §1.2.

## What Changes

- Create `dev/research/backlog.md` (or GitHub issue labels) tracking deferred intblock candidates with status, owner, and sourcing criteria.
- Process backlog in batches: initiative vs bloc scope decisions, historical entity modeling, treaty party sourcing.
- Tighten intblocks completeness gates after remediation (coordinate with `add-intblocks-validation`).
- Update `gaps_merged_20260528.md` reconciliation section as items ship.

## Impact

- Affected specs: `intblocks-data-quality` (modified)
- Affected code: `data/intblocks/`, `dev/research/`, completeness config
- Breaking: None for additions; possible schema/content changes per record
