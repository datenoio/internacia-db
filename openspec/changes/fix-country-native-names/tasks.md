## 1. Vocabulary
- [x] 1.1 Generate `data/vocabs/language_codes.yaml` (ISO 639-3 → map key, Wikidata label codes) for every code in `languages[]`
- [x] 1.2 Review collisions and macrolanguages by hand (`ron`, `nor`, `ber`, `smi`, `kon`, `lin`, `gsw`, `fil`, …)

## 2. Enricher
- [x] 2.1 Rewrite `build_native_names` with the selection rules in design.md; drop aliases and the `c[:2]` fallback
- [x] 2.2 Fetch P1448 and P1705 claims and labels for the mapped codes (respect the Wikidata API's 50-language limit)
- [x] 2.3 Write `native_names` provenance with the entity URL
- [x] 2.4 Unit tests: swapped-variant regression, alias exclusion, zh script per entity, nor → nb, empty `languages[]`

## 3. Validation
- [x] 3.1 `NATIVE_NAME_LANGUAGE` warning rule in `country_rules.py`, registered in the rule registry
- [x] 3.2 `is_null_field`: accept `{}` when `languages[]` is empty
- [x] 3.3 Keep `_country_name_variants` (include display names) working with the smaller map

## 4. Data
- [x] 4.1 Regenerate `native_names` for all 256 records; attach the diff summary to the PR
- [x] 4.2 Add sourced `languages[]` for XK and review CH

## 5. Docs and consumers
- [x] 5.1 Schema description, `docs/data-dictionary.md`, README, `docs/ai-consumers.md`, `docs/enrichment.md`, `llms*.txt`
- [x] 5.2 Migration notes in CHANGELOG and `docs/data-contract.md`
- [x] 5.3 `internacia-python`: add `other_names` to `search` (internacia-python#11, released in 0.4.1)
- [ ] 5.4 Schedule for the next MAJOR release (maintainer)
