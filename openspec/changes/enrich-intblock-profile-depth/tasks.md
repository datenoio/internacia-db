## 1. Structural metadata enrichment
- [x] 1.1 Add Wikidata claim fetch for headquarters location (`P159`) and coordinates to `enrich_intblocks.py`
- [x] 1.2 Add Wikidata inception (`P571`) mapping to `founded`
- [x] 1.3 Write `provenance` entries for each filled `headquarters`/`founded` field
- [x] 1.4 Support `--dry-run` reporting of how many records would be filled (`backfill-structural --dry-run`)

## 2. wikidata_id backfill
- [ ] 2.1 Run the existing high-confidence `wikidata_id` matcher over the 233 records missing an id — deferred: requires live Wikidata network access; matcher is implemented and ready
- [x] 2.2 Leave ambiguous matches unset and log them for manual review (existing `resolve_wikidata_id` behavior)

## 3. Freshness policy
- [x] 3.1 Stamp `last_verified` (ISO date) on records touched by enrichment or manual verification
- [x] 3.2 Declare `last_verified` in `intblocks.schema.json` if not already present (already declared)
- [x] 3.3 Add a `last_verified` coverage rule to `intblocks_completeness.yaml` (warn mode) and report it in `validate_intblocks.py`

## 4. Validate and rebuild
- [ ] 4.1 Run `enrich_intblocks.py --dry-run`, review, then apply — deferred: data-backfill run requires live Wikidata network access
- [x] 4.2 Run `validate_intblocks.py`, `pytest tests/`, rebuild datasets
- [x] 4.3 Run `openspec validate enrich-intblock-profile-depth --strict`
