## 0. Approval gate

- [x] 0.1 Maintainer chose on 2026-11-23 to add the DTA id as a catalogue identifier

## 1. Schema, validation and build

- [x] 1.1 Add `dta_id` to `data/schemas/trade_agreements.schema.json`
- [x] 1.2 Add `dta_id` to the catalogue identifiers checked for `DUPLICATE_IDENTIFIER`
- [x] 1.3 Export `dta_id` after `gptad_id`
- [x] 1.4 Tests for the column and the uniqueness rule

## 2. DTA walk

- [x] 2.1 Add `scripts/oneoff/import_dta.py`: map by `wto_rta_id`, then by hand for placeholder and retired RTA IDs; skip accessions and enlargements; write `dta_id`
- [x] 2.2 Hand-review the mapping and the report (400 ids: 376 mapped, 372 by `wto_rta_id` and 4 by hand; 24 accessions and enlargements skipped; none unmatched)
- [x] 2.3 Log the walk in `docs/intblock-sources.md`

## 3. Documentation and verification

- [x] 3.1 Document `dta_id` in `docs/data-contract.md`, `docs/ai-consumers.md`, `llms.txt` and regenerated shims
- [x] 3.2 Changelog fragment
- [x] 3.3 Rebuild with the pinned requirements; run the validators, `ruff`, `pytest tests/` and the snapshot, artifact, doc-count and link checks
