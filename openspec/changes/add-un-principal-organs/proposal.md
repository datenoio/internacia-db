# Change: Add UN principal organs (Tier 1 coverage)

## Why

The Manus report (`dev/research/report_manus_20260615.md`) identifies UNSC, UNGA, and UNHRC as **Tier 1 — Critical** gaps: principal UN organs absent from a dataset claiming comprehensive international-body coverage. UNHRC was previously deferred in gap analysis; this change elevates it with UNSC and UNGA.

Coordinate with `add-intblocks-gap-backlog` for UNHRC sourcing decisions already tracked there.

## What Changes

- Add intblock records for `UNSC`, `UNGA`, and `UNHRC` with required fields, membership, links, and Wikidata IDs.
- Place records under appropriate directories (`unagency/` or `political/` per primary blocktype decision).
- Link `partof` relationships to `UN` where applicable.
- Update gap backlog / research reconciliation when shipped.

## Impact

- Affected specs: `intblocks-data-quality` (modified)
- Affected code: `data/intblocks/`, completeness metrics
- Breaking: None (additive)
