---
name: internacia-contribute
description: >-
  Edit Internacia country and intblock YAML safely — validation, enrichment,
  provenance, and OpenSpec gates. Use when modifying data/countries/, data/intblocks/,
  data/blocktypes/, running validate_* scripts, enrich_*.py, or proposing schema changes
  in internacia-db.
---

# Internacia data contribution (Cursor)

Read the platform-neutral guide: **[docs/agents/contribute.md](../../../docs/agents/contribute.md)**

Also useful:
- [CONTRIBUTING.md](../../../CONTRIBUTING.md) — setup and PR checklist
- [docs/agents/add-intblock-example.md](../../../docs/agents/add-intblock-example.md) — worked add-intblock walkthrough
- [docs/agents/openspec-quickstart.md](../../../docs/agents/openspec-quickstart.md) — schema changes
- `.agent/workflows/edit-intblock.md` — intblock edit workflow

Validate with structured output for agents:

```bash
python scripts/validate_countries.py --json
python scripts/validate_intblocks.py --json
```
