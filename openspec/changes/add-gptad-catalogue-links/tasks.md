## 0. Approval gate

- [x] 0.1 Maintainer chose on 2026-11-23 to start the GPTAD integration with ids and text links

## 1. Schema, validation and build

- [x] 1.1 Add `gptad_id` and the `treaty_text` link type to `data/schemas/trade_agreements.schema.json`
- [x] 1.2 Report a repeated `wto_rta_id`, `aric_id` or `gptad_id` as `DUPLICATE_IDENTIFIER`
- [x] 1.3 Export `gptad_id`; append a linked record's own links to its intblock's links
- [x] 1.4 Tests for the column, the uniqueness rule and the merged links

## 2. GPTAD walk

- [x] 2.1 Add `scripts/oneoff/fetch_gptad.py` (library table, agreement ids, indexed provisions)
- [x] 2.2 Add `scripts/oneoff/import_gptad.py`: map by hand against the official name of the text, then by parties and date; write `gptad_id` and a `treaty_text` link (the RTA-IS export has no document symbols, so GPTAD's WTO symbols cannot be joined to `wto_rta_id`)
- [x] 2.3 Hand-review the mapping; leave GPTAD duplicates, accessions and agreements missing from the registry unmapped, with a reason in the report (352 ids: 278 mapped, 215 by the automatic rule and 63 by hand; 31 skipped; 43 not in the registry)
- [x] 2.4 Log the walk in `docs/intblock-sources.md`

## 3. Documentation and verification

- [x] 3.1 Document `gptad_id` and `treaty_text` in `docs/data-contract.md`, `docs/ai-consumers.md`, `llms.txt` and regenerated shims
- [x] 3.2 Changelog fragment
- [x] 3.3 Rebuild with the pinned requirements; run the validators, `ruff`, `pytest tests/` and the snapshot, artifact, doc-count and link checks
