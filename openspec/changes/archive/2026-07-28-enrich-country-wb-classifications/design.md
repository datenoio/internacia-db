## Context

33 country records share missing WB `region`/`incomeLevel`/`lendingType`; 107 lack `adminregion`. These overlap but are not identical sets. Gini has 32.5% missing rate with genuine data availability limits.

## Goals / Non-Goals

- Goals: Fill classifiable gaps from alternative authorities; document expected absences; partial gini backfill.
- Non-Goals: Fabricating WB classifications; requiring gini for all 252 records.

## Decisions

- **Alternative sources**: UN M49 for `region`/`adminregion`; IMF World Economic Outlook or documented manual curation for income proxies where WB absent.
- **Expected nulls**: Territories without WB membership documented in policy doc with `classification_status: not_wb_classified` or equivalent marker if schema extended.
- **Gini**: Accept older estimates with explicit `year` and `source`; tighten completeness only after backfill pass.

## Risks / Trade-offs

- Non-WB income labels may not match WB `incomeLevel` enum → extend enum or use supplemental field in follow-up.

## Open Questions

- Whether to add `classification_source` field to distinguish WB vs M49-sourced region values.
