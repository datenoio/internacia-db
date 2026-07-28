## Context

Topics are a flat key–name list on each intblock record with no central registry file. The report recommends a two-level hierarchy (~30–40 top-level canonical topics) but Phase 1 focuses on synonym consolidation without a full schema restructure.

## Goals / Non-Goals

- Goals: Reduce redundant keys; ensure every record has ≥1 topic; document governance; enable gradual validator enforcement.
- Non-Goals: Full hierarchical topic schema in YAML; automated topic inference from descriptions.

## Decisions

- **Canonical key map**: Maintain `data/schemas/topic_aliases.yaml` (or section in contributor docs) mapping deprecated → canonical keys for migration and validation.
- **Sports consolidation**: Replace event/sport-specific keys (`football`, `world_cup`, etc.) with `sports`; retain `sports_governance` for federations and leagues.
- **Enforcement**: Warn on deprecated keys for one release cycle; tighten to error after migration PR merges.

## Risks / Trade-offs

- Consumer queries using old keys break → publish alias map and CHANGELOG migration table.
- Subjective canonical choice (e.g. `economy` vs `economic_cooperation`) → document rationale per group in alias file.

## Migration Plan

1. Add alias map and governance doc.
2. Batch-update YAML files by synonym group (scripted find-replace with review).
3. Assign topics to empty records manually or via blocktype→topic heuristics.
4. Enable validator warnings; ratchet after backfill.

## Open Questions

- Whether to introduce a machine-readable `data/schemas/topics.yaml` canonical list in a follow-up change.
