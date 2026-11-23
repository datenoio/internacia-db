## 0. Approval gate

- [ ] 0.1 Maintainer approves the `desta_id` field
- [ ] 0.2 datenoio/internacia-db#209 (`gptad_id`) and #219 (`dta_id`) are merged

## 1. DESTA walk (done before approval; no schema change)

- [x] 1.1 Add `scripts/oneoff/match_desta.py`: match the 903 DESTA base treaties by WTO name and RTA ID, by parties and year, and by acronym; write the match report (`docs/history/desta-match-2026-11-23.md`, and a `.csv` with DESTA number, record id, method and confidence)
- [x] 1.2 Diff the missing treaties against the open pull requests (#207 to #231)
- [x] 1.3 Add `scripts/oneoff/import_desta.py`: 63 missing agreements with status and dates from ALADI, a party government or the WTO, DESTA cited only in a `desta_id` provenance entry; hold the agreements without such a source
- [x] 1.4 Compare DESTA accession and withdrawal rows with the party rosters; list the gaps without writing party dates
- [x] 1.5 Log the walk in `docs/intblock-sources.md`

## 2. Schema, validation and build (after approval)

- [ ] 2.1 Add `desta_id` to `data/schemas/trade_agreements.schema.json`
- [ ] 2.2 Add `desta_id` to the identifiers checked for `DUPLICATE_IDENTIFIER`
- [ ] 2.3 Export `desta_id` as a nullable `int64` column of `trade_agreements`; list it in `contract.json`
- [ ] 2.4 Tests for the column and the uniqueness rule

## 3. Identifiers

- [ ] 3.1 Set `desta_id` from the match CSV in one pass (`high` and `medium` rows; review `low` rows)
- [ ] 3.2 Move the `desta_id` provenance entries of the 2026-11-23 records into the field

## 4. Documentation and verification

- [ ] 4.1 Document `desta_id` in `docs/data-contract.md`, `docs/ai-consumers.md`, `llms.txt` and regenerated shims
- [ ] 4.2 Changelog fragment
- [ ] 4.3 Rebuild with the pinned requirements; run the validators, `ruff`, `pytest tests/` and the snapshot, artifact, doc-count and link checks
