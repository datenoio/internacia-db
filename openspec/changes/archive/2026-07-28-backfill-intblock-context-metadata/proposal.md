# Change: Backfill intblock contextual metadata

## Why

The Manus report (`dev/research/report_manus_20260615.md`) flags critical gaps in optional but analytically essential intblock fields: `legal_status` (74.6% missing), `geographic_scope` (59.5% missing), `headquarters` (54.1% missing), and templated descriptions in 253 records (23.9%). High-profile organizations should be backfilled first.

## What Changes

- Phase 1: Backfill `legal_status`, `geographic_scope`, and `headquarters` for high-profile records (UN system, major regional blocs, top-50 by notability).
- Phase 2: Replace templated descriptions ("International entity focused on...") with specific summaries from official sources or Wikidata.
- Phase 3 (lower priority): Backfill `founded` for records missing founding dates.
- Tighten `intblocks_completeness.yaml` thresholds incrementally as coverage improves.
- Record `provenance` for enriched fields.

## Impact

- Affected specs: `intblocks-data-quality` (modified)
- Affected code: `data/intblocks/**/*.yaml`, `scripts/enrich_intblocks.py`, completeness config
- Breaking: None
