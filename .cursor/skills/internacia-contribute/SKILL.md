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
- `population` / `area` / `gini`: struct `{value, year, source, source_id}` — use `year: null` if unknown, **never `year: 0`**; values must be plausible (no negative population, gini in 0–100, no future years)
- `borders`: ISO **alpha-3** neighbor codes (e.g. `CAN`, `MEX`); each must resolve to an existing country's `iso3code` and should be reciprocal (neighbor lists you back) — exceptions go in `borders.reciprocity_allowlist` of `countries_completeness.yaml`
- `un_member`/`independent` must not be `true` on dependent territories, SARs, or statistical areas
- `tld` is `.xx`-style lowercase; `calling_codes` are `+digits`; `timezones` must be IANA tz names; `flag_emoji` must match the code's regional-indicator pair; `landlocked: true` requires non-empty `borders`
- `capital_city` coordinates must be plausible: the analyzer flags capitals beyond an area-scaled distance from `centroid` (`CAPITAL_FAR_FROM_CENTROID`) — a flag usually means swapped lat/lng; legit outliers go in `geography.capital_distance.allowlist`
- `subregion` must belong to one of the record's `continents`; transcontinental exceptions go in `region_hierarchy.allowlist` of `countries_completeness.yaml`
- Add `provenance` when setting or updating enriched fields
- Refresh via `python scripts/enrich_countries.py` (see [docs/enrichment.md](../../../docs/enrichment.md))

## Intblocks checklist

- Required: `id`, `name`, `blocktype`, `status`
- `includes[].id` is **authoritative** for joins (country alpha-2); `name` is display-only
- `includes[].status` must be a key from `data/schemas/includes_status.yaml`
- Records without `includes` must set `membership_applicability: not_applicable` when membership is intentionally absent
- Completeness priorities: see `data/schemas/intblocks_completeness.yaml` (high: includes; medium: wikidata_id, non-templated description; low: languages, headquarters, regions, other_names, provenance, links)
- Dissolved orgs: `status: historical` + `dissolved` date; do not invent membership. `founded`/`dissolved` must be real dates (`YYYY`, `YYYY-MM`, `YYYY-MM-DD`, or `YYYYs`) — **never `YYYY-00-00`** — and `dissolved` must not precede `founded`
- `predecessor`/`successor`/`suborganizations[].id` must resolve to an existing intblock `id` or alias; affiliated bodies without their own record go in `references.org_ref_allowlist` of `intblocks_completeness.yaml`
- `headquarters.country` must resolve to a `data/countries/{code}.yaml` file
- `wikidata_id` must be unique across all records; intentionally shared concept Q-ids go in `references.wikidata_duplicate_allowlist` with a reason comment
- `membership_count`, when set, should match the `includes` count (total or member-class entries)
- `includes[].joined`/`left` must be real dates, `left` not before `joined`, neither after `dissolved` (joining before `founded` is fine — ratification precedes entry into force)
- `founding_members` entries must resolve to country codes and appear in `includes` (use `former_member` for founders that left)
- Historical entity countries (e.g. `AN`, `SU`) must not carry active statuses in non-historical blocks — use `former_member`
- Topic keys must exist in `data/schemas/topics.yaml`; genuinely new keys are added to that catalog in the same PR
- Lineage: when `predecessor`/`successor` resolves to a record whose inverse field is empty, add the back-reference; a record listed in a parent's `suborganizations` must declare that parent in `partof`
- Shared English acronyms across same-blocktype records flag `DUPLICATE_ACRONYM`; real-world collisions go in `references.acronym_duplicate_allowlist`
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
