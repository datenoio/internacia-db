# Agent guide: discovering and improving Internacia records

Find intblocks **not yet in this dataset**, or raise the quality of an existing
country / intblock YAML, then hand off to [contribute.md](contribute.md). Human
narrative and hunt-pattern table: [discovery.md](../discovery.md). Catalogues
already walked: [intblock-sources.md](../intblock-sources.md).

This is **not** the query workflow. To look up existing records, use
[query.md](query.md).

## Goal

Produce either:

- a short list of verified **new** intblock candidates (`id`, proposed
  directory/`blocktype`, `scope_category`, official roster URL, whether the `id`
  already exists), or
- a **repair** on one existing YAML (roster diff, provenance, `last_verified`)

Do not invent membership. Do not import a catalogue wholesale. Do not add HDI,
GDP, government type, or similar fields to countries.

## Before probing the web

1. Read [llms.txt](../../llms.txt) if you have not already.
2. Duplicate-check **exports** (`data/datasets/internacia.duckdb` or Parquet),
   then `data/datasets/intblocks_aliases.json`.
3. If DuckDB raises a lock error, query `data/datasets/intblocks.parquet`
   instead. Do not walk YAML to find duplicates.
4. If the user named an `id`, acronym, or YAML path, search that first and stop
   if the record already exists (switch to repair).
5. If this is a catalogue hunt, read [intblock-sources.md](../intblock-sources.md).
   A catalogue listed there with the same retrieval date is exhausted — report
   0 missing and stop unless a new chapter or notification exists.

```sql
SELECT id, name, status, scope_category
FROM intblocks
WHERE id = 'AGADIR'
   OR lower(name) LIKE '%agadir%';
```

```sql
SELECT alias, target, reason
FROM read_json('data/datasets/intblocks_aliases.json')
WHERE alias = 'AGADIR' OR target = 'AGADIR';
```

Match on `id` and official acronym, not display name alone.

## Discovery order

1. **Named catalogues** in [discovery.md](../discovery.md#hunt-patterns) —
   highest yield, fewest false positives. Inclusion bars:
   [intblock-inclusion-policy.md](../intblock-inclusion-policy.md).
2. **Official roster** for each accepted candidate (UNTC status page, org
   membership page, treaty text, USTR / Commission / UNECE). Catalogue index
   cards are not the membership source of truth.
3. **Single-record repair** when the user named a YAML file. Roster first, then
   sibling-field pattern, then provenance / `last_verified`.
4. **Country enrichment** via `python scripts/enrich_countries.py check` /
   `enrich` — not by adding country codes. New user-assigned codes only when an
   intblock needs a join target
   ([country-code-policy.md](../country-code-policy.md)).

You MAY fetch public catalogue pages and official membership lists when the user
asked to discover or improve records and the scope is one catalogue, one
thematic slice, or one YAML path. Do not write internet-wide scanners or
unscoped “all missing IGOs” sweeps. Still duplicate-check exports before adding
an `id`.

## Hunt types \{#hunt-types\}

Match the user prompt to one of these loops. Do not mix them in the same pass.
Accept / reject columns: [discovery.md](../discovery.md#hunt-patterns).

### Catalogue walk

```text
Which {UNTC | WTO RTA-IS | WTO PTA | UNCTAD IIA | Wikipedia .int | UN M49} entries are missing?
```

Walk the named list. For each row: duplicate-check `id` / name / alias; apply
the inclusion bar; compile `includes` from the official roster; stamp
`last_verified` and ≥4 `provenance` entries. Constitutive instruments of an org
already present stay off the list.

If the catalogue in [intblock-sources.md](../intblock-sources.md) is exhausted,
**stop and list 0 missing**.

### Single-record repair

```text
Update record metadata for data/intblocks/{category}/{ID}.yaml
```

1. Fetch the official membership / states-parties page.
2. Diff `includes[].id` (drop non-parties, add missing parties, `former_member`
   + `left` for leavers). Quote `'NO'` / `'no'`.
3. Align metadata with a sibling YAML in the same directory.
4. Unique `wikidata_id`; non-templated `description`; lineage back-references.
5. Provenance ≥4; `last_verified` = today.
6. `python scripts/validate_intblocks.py --json` and fix `errors[]`.

### Country enrichment / repair

```text
Enrich / fix country {CODE}
```

Run `python scripts/enrich_countries.py check` (optionally `--code XX`). Refresh
from World Bank / Wikidata / IANA as in [enrichment.md](../enrichment.md). Fix
borders (alpha-3, reciprocal), capital coordinates, and provenance. Do **not**
add socioeconomic profile fields. Do **not** add a country file unless an
intblock references an entity that has no `code`.

## Accept / reject (short)

**Accept:** named, durable join target; in force (or `historical` to complete a
lineage already in the dataset); official acronym; roster distinct from a parent
IGO / FTA / `LDC` / `GSP`.

**Reject:** untitled bilateral pairs; UK continuity copies of EU EPAs;
services-only EIA of an FTA already recorded; national GSP ID cards; LDC-only
DFQF; bilateral BITs; not-in-force protocols; constitutive acts of existing
IGOs; attribute partitions; socioeconomic rankings; Wikipedia-only membership.

## After a find

Hand off to [contribute.md](contribute.md) and, for a first add,
[add-intblock-example.md](add-intblock-example.md). If the catalogue walk is
new, append a row to [intblock-sources.md](../intblock-sources.md). Update
`CHANGELOG.md` under `[Unreleased]`.

Do not hand-edit `data/datasets/`. Maintainers rebuild exports.

## Related

- [discovery.md](../discovery.md) — hunt patterns and improvement loops
- [intblock-sources.md](../intblock-sources.md) — catalogues and roster authorities
- [intblock-inclusion-policy.md](../intblock-inclusion-policy.md)
- [contribute.md](contribute.md) — YAML checklist
- [query.md](query.md) — look up existing records
- `.agent/workflows/discover-intblock.md` — step-by-step workflow
