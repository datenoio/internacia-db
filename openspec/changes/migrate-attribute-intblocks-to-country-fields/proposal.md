# Change: Migrate attribute intblocks to country properties

## Why

Eight intblock blocktypes (`dvdregion`, `govform`, `lawsystem`, `railgauge`, `teleregion`, `traffichand`, `writingdirection`, `writingsystem`) model intrinsic country attributes as fake membership groups. That ontology is wrong: they are not organizations or durable named sets, they fail membership/provenance quality gates chronically, and `traffichand` already duplicates the country field `car_side`. Consumers who want “left-hand traffic” or “common-law jurisdiction” should filter country columns, not join inverted `includes` rosters.

## What Changes

- **BREAKING**: Remove attribute-partition intblocks and their blocktypes from the intblocks corpus (except `govform`, handled separately — see below).
- Add in-scope country schema fields for driving side (already present as `car_side`), writing direction/system, DVD region, broadcast systems, legal systems, and rail gauges.
- Introduce controlled vocab catalogs under `data/vocabs/` for enum definitions (id, name, wikidata_id, links) — not intblock records with `includes`.
- Invert existing `includes` membership into country fields via a one-shot migration script; reconcile `car_side` vs `traffichand`.
- Publish consumer migration guidance (CHANGELOG + migration artifact) mapping retired intblock ids to country field predicates.
- Tighten `docs/intblock-inclusion-policy.md`: `reference_enumeration` remains for named geographic/set groupings; attribute partitions belong on countries.
- **Out of this change for country fields**: `govform` (government form). Explicitly forbidden by countries scope (“government type”). Retire incomplete govform intblocks to a vocab-only catalog or drop them; do not add `government_form` to countries without a separate scope revision.

## Impact

- Affected specs: `countries-profile`, `countries-data-quality`, `intblocks-data-quality`, `cross-dataset-integrity`, `contributor-docs`, `dataset-release`
- Affected data: `data/countries/*.yaml`, `data/intblocks/{dvdregion,lawsystem,railgauge,teleregion,traffichand,writingdirection,writingsystem,govform}/`, `data/blocktypes/blocktypes.yaml`, new `data/vocabs/`
- Affected code: countries schema/completeness, validators, builder/export schemas, enrichment docs, query examples, `llms.txt` / `docs/ai-consumers.md`
- Downstream: any consumer joining on retired intblock ids (`RHTRAFFIC`, `DVD_1`, `LSCOMMONLAW`, …) must switch to country fields; intblock row counts and blocktype taxonomy shrink
