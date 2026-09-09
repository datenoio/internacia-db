---
name: internacia-discover
description: >-
  Find missing Internacia intblocks or improve existing country and intblock
  YAML — catalogue walks, official rosters, duplicate checks, completeness.
  Use when searching for missing organizations, treaties, FTAs, geographic
  groups, or when updating record metadata and country enrichment.
---

# Internacia discovery and improvement (Cursor)

Read the platform-neutral guide: **[docs/agents/discover.md](../../../docs/agents/discover.md)**

Human narrative and hunt-pattern table: **[docs/discovery.md](../../../docs/discovery.md)**

Also useful:
- [docs/intblock-sources.md](../../../docs/intblock-sources.md) — catalogues already searched
- [docs/intblock-inclusion-policy.md](../../../docs/intblock-inclusion-policy.md) — what belongs
- [docs/agents/contribute.md](../../../docs/agents/contribute.md) — YAML after a find
- `.agent/workflows/discover-intblock.md` — step-by-step workflow

Duplicate-check exports (`internacia.duckdb` or Parquet) and
`data/datasets/intblocks_aliases.json` before adding an `id`. Do not import a
catalogue wholesale. Compile `includes` from the official roster.
