## 0. Approval gate

- [ ] 0.1 Obtain maintainer approval for `add-trade-agreements-registry` (the direction was set by the maintainer on 2026-11-22; this proposal fixes the design)
- [ ] 0.2 Resolve the open questions in `design.md` (migration option, candidate agreements, WTO RTA-IS walk)

## 1. Schema and validation

- [ ] 1.1 Add `data/schemas/trade_agreements.schema.json` with the fields and enums in `design.md`
- [ ] 1.2 Add validation rules (party resolution, intblock link, id namespace, status and date consistency, provenance) to `internacia_builder/validate/` and register them
- [ ] 1.3 Add `scripts/validate_trade_agreements.py` with `--json` output, and run it in CI next to the other validators
- [ ] 1.4 Add the `moved` alias reason and the `target_dataset` field to `data/intblocks_aliases.yaml` handling

## 2. Build and export

- [ ] 2.1 Load `data/trade_agreements/*.yaml`, derive parties for intblock-linked records, and build `trade_agreements` and `trade_agreement_parties`
- [ ] 2.2 Add the `country_trade_agreements` DuckDB view
- [ ] 2.3 Export Parquet and JSONL, and add the resources to `contract.json`, `datapackage.json` and the manifests
- [ ] 2.4 Tests for loading, party derivation, the view, and the contract entries

## 3. Migration of existing records

- [ ] 3.1 Move the 34 two-party intblocks to `data/trade_agreements/`, keeping ids, dates, links and provenance
- [ ] 3.2 Add `moved` aliases for the 34 ids
- [ ] 3.3 Add registry records linked to the multilateral `fta`, `pta` and `customs` intblocks
- [ ] 3.4 Fix the documented queries and counts that change

## 4. ARIC import

- [ ] 4.1 Add `scripts/oneoff/import_aric_ftas.py` and the ADB-code crosswalk
- [ ] 4.2 Import every ARIC row, mapping rows that match existing records by `aric_id`
- [ ] 4.3 Hand-review parties taken from titles and the `Discontinued` rows
- [ ] 4.4 Add intblocks for multilateral ARIC agreements that are signed or in force, with rosters from official sources (Tier 2: EAEU, EFTA and GCC external FTAs, `EUGE`)
- [ ] 4.5 Log the ARIC walk in `docs/intblock-sources.md`

## 5. Documentation and release

- [ ] 5.1 Rewrite the trade sections of `docs/intblock-inclusion-policy.md`
- [ ] 5.2 Document the tables and the view in `docs/data-contract.md`, `docs/ai-consumers.md` and `docs/query-examples.md` (with tests)
- [ ] 5.3 Regenerate agent shims and update current counts
- [ ] 5.4 Changelog fragment with migration SQL for the moved ids

## 6. Verification

- [ ] 6.1 Rebuild with the pinned requirements and run the snapshot, artifact, doc-count and link checks
- [ ] 6.2 Run all validators, `ruff` and `pytest tests/`
