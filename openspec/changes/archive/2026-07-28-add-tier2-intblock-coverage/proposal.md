# Change: Add Tier 2 intblock coverage gaps

## Why

The Manus report (`dev/research/report_manus_20260615.md`) lists eight **Tier 2 — High Priority** missing organizations across digital/tech, health, humanitarian, political, and legal domains. EPC and D10 remain in `add-intblocks-gap-backlog` for initiative-vs-bloc scope decisions.

## What Changes

- Add intblock records: `CHIP4`, `DEPA`, `PEPFAR`, `MSF`, `UNCITRAL`, `UNCLOS`.
- Defer `EPC` and `D10` to `add-intblocks-gap-backlog` (scope review).
- Populate contextual metadata (`legal_status`, `geographic_scope`, membership model) per entity type.
- Assign appropriate blocktypes and topics (e.g. `digital`/`cybersecurity` for CHIP4, `health`/`humanitarian` for PEPFAR/MSF).

## Impact

- Affected specs: `intblocks-data-quality` (modified)
- Affected code: `data/intblocks/` (likely `digital/`, `health/`, `humanitarian/`, `agreement/`, `court/` or `law/`)
- Breaking: None (additive)
