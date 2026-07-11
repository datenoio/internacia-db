---
name: internacia-contribute
description: >-
  Edit Internacia country and intblock YAML safely — validation, enrichment,
  provenance, and OpenSpec gates. Use when modifying data/countries/, data/intblocks/,
  data/blocktypes/, running validate_* scripts, enrich_*.py, or proposing schema changes
  in internacia-db.
---

# Internacia data contribution

## Before editing

1. Read [CONTRIBUTING.md](../../../CONTRIBUTING.md) and [docs/country-code-policy.md](../../../docs/country-code-policy.md).
2. For **consumers** querying exported data, use [docs/ai-consumers.md](../../../docs/ai-consumers.md) — do not parse YAML unless authoring.
3. **Scope guardrail:** countries are reference data only. Do **not** add HDI, GDP, government type, internet penetration, or similar socioeconomic profile fields.

## Source layout

| Path | Rule |
|------|------|
| `data/countries/{CODE}.yaml` | One file per entity; filename = ISO alpha-2 `code` |
| `data/intblocks/{category}/{ID}.yaml` | Filename must match `id`; `id` unique globally |
| `data/blocktypes/blocktypes.yaml` | Taxonomy; every intblock `blocktype` value must exist here |
| `data/datasets/` | **Generated only** — never hand-edit |

## Countries checklist

- Required: `code`, `name`, `iso3code`, `numeric_code`, `entity_type`, `code_status`
- Non-ISO codes (`user_assigned`, `obsolete`): document in [country-code-policy.md](../../../docs/country-code-policy.md); add `recognition_status` when needed
- `population` / `area` / `gini`: struct `{value, year, source, source_id}` — use `year: null` if unknown, **never `year: 0`**
- `borders`: ISO **alpha-3** neighbor codes (e.g. `CAN`, `MEX`)
- Add `provenance` when setting or updating enriched fields
- Refresh via `python scripts/enrich_countries.py` (see [docs/enrichment.md](../../../docs/enrichment.md))

## Intblocks checklist

- Required: `id`, `name`, `blocktype`, `status`
- `includes[].id` is **authoritative** for joins (country alpha-2); `name` is display-only
- Dissolved orgs: `status: historical` + `dissolved` date; do not invent membership
- Quote YAML boolean lookalikes: `'NO'` (Norway), `'no'` (Norwegian)
- New blocktype: add to `data/blocktypes/blocktypes.yaml` first

## Validate before PR

```bash
python scripts/validate_countries.py
python scripts/validate_intblocks.py
pytest tests/
ruff check internacia_builder/ scripts/ tests/
python scripts/builder.py build --formats parquet,duckdb
```

CI mirrors `.github/workflows/validate.yml`.

## Schema or breaking changes

New capabilities, schema changes, or breaking exports require an OpenSpec proposal first:

1. Read [openspec/AGENTS.md](../../../openspec/AGENTS.md)
2. Scaffold `openspec/changes/<change-id>/` with `proposal.md`, `tasks.md`, spec deltas
3. Run `openspec validate <change-id> --strict`
4. Do **not** implement until approved

Update `CHANGELOG.md` under `[Unreleased]` for consumer-visible changes.

## Common fixes

| Mistake | Fix |
|---------|-----|
| Alpha-2 in `borders` | Use alpha-3 (`iso3code` of neighbor) |
| Plain number for `population` | Use struct with `value`, `source` |
| Intblock id collision | Pick new unique `id`; add alias in `intblocks_aliases` only via maintainer workflow |
| Invalid `blocktype` | Add entry to `blocktypes.yaml`, re-validate |
| Missing provenance on enrichment | Append `{field, source, retrieved_at}` to `provenance` list |
