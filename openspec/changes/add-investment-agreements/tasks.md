## 0. Approval gate

- [ ] 0.1 Obtain maintainer approval for `add-investment-agreements`
- [ ] 0.2 Resolve the open questions in `design.md`: a `suspended` status, exploratory rows, and the `BLEU` intblock

## 1. Schema and validation

- [ ] 1.1 Add `investment` to `agreement_type` in `data/schemas/trade_agreements.schema.json`, describe it, and change the `services` description to "services only"
- [ ] 1.2 Add the optional integer field `unctad_iia_id`, and extend the `verification: catalogue` description to the UNCTAD IIA Navigator
- [ ] 1.3 Validator rules:
  - an unlinked `investment` record's id ends in `-BIT` or `-BIT-YYYY`;
  - an id with that suffix has `agreement_type: investment`;
  - `unctad_iia_id` is unique.
- [ ] 1.4 Tests for the new rules in `tests/test_trade_agreements.py`
- [ ] 1.5 After `add-trade-agreements-registry` is archived into `openspec/specs/trade-agreements/spec.md`, fold the `investment` value into the "Trade agreement source records" requirement with a MODIFIED delta

## 2. Build and export

- [ ] 2.1 Export `unctad_iia_id` in `trade_agreements` (Parquet, JSONL, DuckDB) and add it to `contract.json` and `datapackage.json`
- [ ] 2.2 Regenerate the data dictionary

## 3. Bloc and plurilateral records

- [ ] 3.1 Add the `BLEU` intblock (Belgium–Luxembourg Economic Union, members `BE` and `LU`) with an official source for the 1921 convention and its current form
- [ ] 3.2 Add registry records linked to `OICIA`, `ACIA`, `UAIA`, `CJKIA`, `PCFI` and `INTRAEUBIT`, with `agreement_type: investment` and `verification: official`

## 4. Canada pilot

- [ ] 4.1 Add `scripts/oneoff/import_canada_fipas.py`. It reads the GAC table and maps each status by `design.md` decision 3. It reads CTS details for each treaty with a CTS id (signature, entry into force, suspension, CTS citation), and writes `-BIT` records.
- [ ] 4.2 Find the CTS ids of the 29 rows that link to international.gc.ca pages (newer FIPAs), from their text pages or by hand
- [ ] 4.3 Hand-review the special rows:
  - Argentina and Uruguay are `in_force`, with the renegotiation in `notes`.
  - Panama, Peru and Ukraine are `superseded` by `CAPA`, `CAPE` and `CAUA`.
  - Ecuador is `terminated`, with the termination date from an official source.
  - Russia is recorded as `RU`, with the U.S.S.R. as the original signatory.
  - The 10 inactive rows are `abandoned`.
- [ ] 4.4 List the CTS "Investment protection" instruments that the GAC table omits, and add them

## 5. Documentation

- [ ] 5.1 `docs/intblock-inclusion-policy.md`: bilateral investment treaties go in the registry; the plurilateral intblock bar is unchanged
- [ ] 5.2 `docs/intblock-sources.md`: log the GAC and CTS walk and the UNCTAD access result
- [ ] 5.3 `docs/discovery.md` and `docs/agents/discover.md`: drop "bilateral BITs" from the skip lists and point to the registry
- [ ] 5.4 `docs/data-contract.md`, `docs/ai-consumers.md`, query examples: the `investment` type, the `agreement_type` filter for trade-only counts, and `unctad_iia_id`
- [ ] 5.5 Changelog fragment, counts and agent shims

## 6. Verification

- [ ] 6.1 Rebuild with the pinned requirements and run the snapshot, artifact, doc-count and link checks
- [ ] 6.2 Run all validators, `openspec validate add-investment-agreements --strict`, `ruff` and `pytest tests/`

## 7. Follow-up changes (not in this change)

- [ ] 7.1 US BITs from `trade.gov/bilateral-investment-treaties` (41 treaties)
- [ ] 7.2 Australian investment treaties from the DFAT Australian Treaties Database
- [ ] 7.3 EU and EFTA investment protection agreements
- [ ] 7.4 UNCTAD IIA Navigator catalogue walk, once an export can be obtained without bypassing the site's bot challenge
