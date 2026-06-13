## 1. Provenance support

- [x] 1.1 Add optional `provenance` definition to `data/schemas/intblocks.schema.json`
- [x] 1.2 Add `provenance` to the intblocks PyArrow schema and `clean_data` normalization in `scripts/builder.py`

## 2. Enrichment tooling

- [x] 2.1 Create `scripts/enrich_intblocks.py` with `enrich` command and `--dry-run`/`--force`/`--limit`/`--id`
- [x] 2.2 B1: resolve `wikidata_id` for missing records via high-confidence matches only
- [x] 2.3 B2: replace templated descriptions with the Wikidata description
- [x] 2.4 B3: backfill multilingual `other_names` and acronym aliases
- [x] 2.5 Record `provenance` on every enriched field

## 3. Quality gates

- [x] 3.1 Add templated-description rate check to `validate_intblocks.py`
- [x] 3.2 Add config keys for description/alias quality in `intblocks_completeness.yaml`
- [x] 3.3 Ratchet `wikidata_id` threshold after backfill (0.42 -> 0.36)

## 4. Run, verify, document

- [x] 4.1 Run `enrich_intblocks.py` (dry-run then apply); rebuild datasets
- [x] 4.2 Add tests for matching, templated detection, and provenance upsert
- [x] 4.3 Update README scripts table and CHANGELOG
- [x] 4.4 Run `openspec validate add-intblocks-enrichment --strict`
