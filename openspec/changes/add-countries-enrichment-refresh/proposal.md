# Change: Add countries enrichment refresh workflow

## Why

Country profile fields (`population`, `area`, `gini`, etc.) are enriched from external sources but lack a scheduled refresh process. Gini completeness allows 45% null rate; currency and border data have no automated drift detection.

See [docs/improvement-plan.md](../../../docs/improvement-plan.md) §1.4.

## What Changes

- Document enrichment refresh cadence and maintainer runbook.
- Add optional scheduled workflow (monthly) running `enrich_countries.py` in check mode or opening PR with updates.
- Tighten `gini` completeness threshold incrementally after backfill passes.
- Add validation helpers for ISO 4217 currency codes and border list sanity (warn mode).
- Extend provenance `retrieved_at` freshness checks in validator (warn when stale > N months).

## Impact

- Affected specs: `countries-profile` (modified), `countries-data-quality` (modified)
- Affected code: `scripts/enrich_countries.py`, completeness config, optional CI workflow, docs
- Breaking: None (warn-first for new checks)
