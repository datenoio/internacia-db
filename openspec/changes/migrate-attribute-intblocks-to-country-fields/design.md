# Design: Attribute intblocks → country properties

## Context

Internacia mixes true organizational intblocks (IGOs, treaties, forums) with inverted country classifications stored as intblocks with `includes` rosters. The latter are already labeled `scope_category: reference_enumeration` in many cases, but geographic reference sets (SIDS, Maghreb) are legitimate named groupings, while attribute partitions (traffic hand, DVD region, script) are properties of each country.

`car_side` already exists on every country record and duplicates `traffichand` (`LHTRAFFIC` / `RHTRAFFIC`). Remaining attribute blocktypes generate a large share of permanent validation warnings (missing includes, shallow provenance).

Countries scope guardrail: do **not** add socioeconomic profile fields such as government type. `govform` is therefore excluded from country-field migration.

## Goals / Non-Goals

**Goals**
- Make attribute classifications first-class country fields with controlled vocab ids.
- Remove attribute-partition blocktypes from the intblocks corpus.
- Preserve Wikidata/link metadata for vocab values in small catalogs.
- Provide an explicit consumer migration path for retired intblock ids.
- Keep geographic `reference_enumeration` intblocks (SIDS, regional seas, etc.).

**Non-Goals**
- Adding `government_form` / govform values to countries (requires separate scope change).
- Perfecting incomplete historical rosters before migration (invert what exists; document gaps; optional enrichment follow-up).
- Changing geographic reference intblocks or currency/language modeling.
- Redesigning the general intblock alias system beyond what retirement-to-field needs.

## Decisions

### Decision 1: Country field shapes

| Field | Shape | Notes |
|-------|--------|------|
| `car_side` | enum `left` \| `right` | Already present; source of truth after retiring `traffichand` |
| `writing_directions` | array of `{id, primary?}` | Multi-valued (e.g. JP: `ltr` + `ttb`) |
| `writing_systems` | array of `{id, primary?}` | Multi-valued (e.g. IL: `hebrew` + `arabic`) |
| `dvd_region` | integer 1–6 or omitted | Single-valued partition |
| `broadcast_systems` | array of `{id}` | Replaces `teleregion` (ATSC/NTSC/…); often multi |
| `legal_systems` | array of `{id}` | Replaces `lawsystem`; often multi / mixed |
| `rail_gauges` | array of `{id, gauge_mm?, primary?}` | Replaces `railgauge`; allow multi even if current data is mostly single |

Ids are lowercase snake or short tokens (`ltr`, `common_law`, `atsc`, `standard`), not legacy intblock ids (`WDLTR`, `LSCOMMONLAW`).

### Decision 2: Vocab catalogs, not empty intblocks

Store definitions in `data/vocabs/<name>.yaml` (e.g. `writing_systems.yaml`) with entries `{id, name, wikidata_id?, links?, aliases?, gauge_mm?}`.

Rationale: catalogs are not membership entities; they should not appear in intblocks DuckDB tables or trigger includes/provenance IGO rules. Optional build export: `data/datasets/vocabs_*.json` (or embed closed enums only in JSON Schema when tiny).

### Decision 3: `govform` handling

- Do **not** add a country field.
- Remove `govform` intblock YAML and blocktype from the org corpus (same retirement wave).
- Optionally preserve taxonomy definitions in `data/vocabs/government_forms.yaml` for external consumers, without country assignments in this repository.
- Document that a future OpenSpec change is required to put government form on countries.

### Decision 4: Consumer migration for retired ids

Existing `intblocks_aliases.yaml` requires `target` to be a live intblock id (`renamed` / `merged` / `disambiguated`). Attribute retirement does not fit that contract.

Introduce a sibling artifact `data/attribute_intblock_migrations.yaml` (exported to `data/datasets/attribute_intblock_migrations.json`) with entries:

```yaml
- retired_id: RHTRAFFIC
  country_field: car_side
  country_value: right
  since: <next-semver>
  note: Prefer countries.car_side = 'right'
```

Validation: every `retired_id` must not exist as a current intblock; `country_field` must be a documented migrated field; enum/list value must resolve against the vocab or schema enum.

CHANGELOG and `migration.v*.json` record countries fields added and intblock/blocktype removals.

### Decision 5: Phased apply (implementation order)

1. Schema + vocabs + docs/policy (non-destructive).
2. Invert script: traffichand → reconcile with `car_side`; other types → new fields.
3. Delete attribute intblock directories and blocktype entries; write migration artifact.
4. Rebuild datasets; update query examples / AI consumer docs.
5. Completeness thresholds: warn-mode initially for new multi-valued fields until enrichment closes gaps.

### Decision 6: What stays as `reference_enumeration` intblocks

Named geographic or set groupings where the set itself is the entity of interest (e.g. SIDS, Maghreb, Caribbean) remain intblocks. Attribute partitions that merely encode “country has property X = v” move to countries.

## Risks / Trade-offs

| Risk | Mitigation |
|------|------------|
| Incomplete intblock rosters become incomplete country fields | Invert faithfully; mark completeness warn; follow-up enrichment from Wikidata |
| `car_side` vs `traffichand` disagreement | Migration script reports diffs; prefer `car_side` unless traffichand has stronger provenance |
| Downstream breakages | Migration artifact + CHANGELOG; major version bump if release policy requires |
| Alias validator confusion | Keep attribute migrations out of `intblocks_aliases.yaml` |
| Scope creep into govform on countries | Explicit non-goal; vocab-only optional |

## Migration Plan

1. Land OpenSpec proposal; approve.
2. Implement schema/vocabs/validators without deleting intblocks (dual-write optional).
3. Run invert + reconcile; fix outliers.
4. Delete attribute intblocks/blocktypes; ship migration artifact.
5. Tag release with BREAKING notes for intblock consumers.
6. Rollback: restore deleted YAML from git; drop new country fields in a revert commit (datasets regenerated).

## Open Questions

1. Should vocab catalogs be exported as first-class DuckDB tables in v1 of this change, or YAML+JSON only?
2. Is `bijuridical` a first-class `legal_systems` id or a derived flag when multiple systems are present?
3. Retain `data/vocabs/government_forms.yaml` after dropping govform intblocks, or delete taxonomy entirely?
