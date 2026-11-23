## 0. Approval gate

- [ ] 0.1 Maintainer approves the `edit_uuid` field (section 2 onwards); the walk in section 1 adds no field

## 1. EDIT walk (done before approval)

- [x] 1.1 Add `scripts/oneoff/fetch_edit.py`: save the 4,271 EDIT documents from `full_search` (500 a page) and the CSV report, 2 s apart, without the texts
- [x] 1.2 Add `scripts/oneoff/import_edit.py`: match by parties (ids, bloc members, overlapping rosters on the same date) and date of signature, year or typing slip; successor-state records; instruments; hand decisions in `MANUAL`
- [x] 1.3 Add `treaty_text` links to the EDIT document page on matched records whose EDIT document has a text (3,636), leaving the records of the CIS/EAEU and AfCFTA walks for later and the 18 UAE CEPA records to the UAE CEPA walk
- [x] 1.4 Note EDIT's dates where they differ from a record's (458 records), without changing dates, statuses or verification levels
- [x] 1.5 Add the missing investment treaties: three EU agreements from the European Commission and EUR-Lex, and 22 EDIT-only BITs with an entry into force at `verification: catalogue`; hold the rest
- [x] 1.6 Name EDIT in the `catalogue` description of `verification`
- [x] 1.7 Write the match report (`docs/history/edit-match-2026-11-23.md`, a per-document CSV with `edit_uuid`, and a date-conflict CSV) with `scripts/oneoff/write_edit_report.py`
- [x] 1.8 Log the walk in `docs/intblock-sources.md`; changelog fragment

## 2. Schema, validation and build (after approval)

- [ ] 2.1 Add `edit_uuid` (string, uuid pattern) to `data/schemas/trade_agreements.schema.json`
- [ ] 2.2 Validator: warn when one `edit_uuid` is on two records with different dates of signature
- [ ] 2.3 Export `edit_uuid` as a nullable string column of `trade_agreements`; list it in `contract.json`
- [ ] 2.4 Tests for the column and the validator rule

## 3. Identifiers (after approval)

- [ ] 3.1 Set `edit_uuid` from `docs/history/edit-match-2026-11-23.csv` in one pass (`high` and `medium` rows; review the 10 `low` ones)
- [ ] 3.2 Add the links and uuids of the records left to the CIS/EAEU and AfCFTA walks (`AfCFTA`, `CISFTASERVICES`, `EAEU`, `EAEUVN`) once those walks merge

## 4. Documentation and verification

- [ ] 4.1 Document `edit_uuid` in `docs/data-contract.md`, `docs/ai-consumers.md`, `llms.txt` and the regenerated shims
- [ ] 4.2 Rebuild with the pinned requirements; run the validators, `ruff`, `pytest tests/` and the snapshot, artifact, doc-count and link checks
