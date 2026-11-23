## 0. Approval gate

- [x] 0.1 Obtain maintainer approval for `add-investment-agreements` (the maintainer asked for the Canada pilot on 2026-11-23)
- [x] 0.2 Resolve the open questions in `design.md` for the pilot, using the design defaults: suspended treaties are `superseded`, with no new status; "1. Exploratory discussions" rows are imported as `proposed`. The `BLEU` intblock stays open until task 3.1, because no Canada treaty needs it.

## 1. Schema and validation

- [x] 1.1 Add `investment` to `agreement_type` in `data/schemas/trade_agreements.schema.json`, describe it, and change the `services` description to "services only"
- [ ] 1.2 Add the optional integer field `unctad_iia_id`, its uniqueness rule, and extend the `verification: catalogue` description to the UNCTAD IIA Navigator (deferred to the UNCTAD walk, task 7.4: no record has an UNCTAD id yet)
- [x] 1.3 Validator rule `TRADE_AGREEMENT_ID_SUFFIX`: an unlinked `investment` record's id ends in `-BIT` or `-BIT-YYYY`, and an id with that suffix has `agreement_type: investment`
- [x] 1.4 Tests for the new rule in `tests/test_trade_agreements.py`
- [ ] 1.5 After `add-trade-agreements-registry` is archived into `openspec/specs/trade-agreements/spec.md`, fold the `investment` value into the "Trade agreement source records" requirement with a MODIFIED delta

## 2. Build and export

- [ ] 2.1 Export `unctad_iia_id` in `trade_agreements` (Parquet, JSONL, DuckDB) and add it to `contract.json` and `datapackage.json` (with task 1.2)
- [x] 2.2 `contract.json` lists `investment` in the open `agreement_type` enum; the data dictionary needed no change

## 3. Bloc and plurilateral records

- [ ] 3.1 Add the `BLEU` intblock (Belgium–Luxembourg Economic Union, members `BE` and `LU`) with an official source for the 1921 convention and its current form
- [ ] 3.2 Add registry records linked to `OICIA`, `ACIA`, `UAIA`, `CJKIA`, `PCFI` and `INTRAEUBIT`, with `agreement_type: investment` and `verification: official`

## 4. Canada pilot

- [x] 4.1 Add `scripts/oneoff/import_canada_fipas.py`. It reads the GAC table and maps each status by `design.md` decision 3. It reads the CTS result list for the subject "Investment protection" and the CTS details of each treaty (signature, entry into force, suspension, CTS citation), and writes `-BIT` records.
- [x] 4.2 Find the CTS ids of the rows that link to international.gc.ca pages: the CTS result list gives every id (41 GAC rows have a CTS treaty)
- [x] 4.3 Hand-review the special rows:
  - Argentina and Uruguay are `in_force`, with the renegotiation in `notes`.
  - Panama, Peru and Ukraine are `superseded` by `CAPA`, `CAPE` and `CAUA`.
  - Ecuador is `terminated` in 2018, per the House of Commons trade committee; only the year is given.
  - Tanzania is `terminated` on 2023-12-09, per GAC. GAC lists it as "In negotiations".
  - Russia is recorded as `RU`, with the U.S.S.R. as the original signatory.
  - The 10 inactive rows are `abandoned`.
- [x] 4.4 Add the CTS "Investment protection" instruments that the GAC table omits:
  - El Salvador 1999 and South Africa 1995, both signed;
  - Uruguay 1991, never in force;
  - Czechoslovakia 1990, terminated;
  - Latvia 1995 and Romania 1996, superseded.

  Two are skipped: the 1979 Yugoslavia agreement, with no source for its successor states, and the ICSID Convention.

## 5. Documentation

- [x] 5.1 `docs/intblock-inclusion-policy.md`: bilateral investment treaties go in the registry; the plurilateral intblock bar is unchanged
- [x] 5.2 `docs/intblock-sources.md`: log the GAC and CTS walk and the UNCTAD access result
- [x] 5.3 `docs/discovery.md` and `docs/agents/discover.md`: point bilateral BITs to the registry
- [x] 5.4 `docs/data-contract.md`, `docs/ai-consumers.md` and `llms.txt`: the `investment` type and the `agreement_type` filter for trade-only counts
- [x] 5.5 Changelog fragment; regenerate `llms-full.txt`

## 6. Verification

- [x] 6.1 Rebuild with the pinned requirements and run the snapshot, artifact, doc-count and link checks
- [x] 6.2 Run all validators, `openspec validate add-investment-agreements --strict`, `ruff` and `pytest tests/`

## 7. Follow-up changes (not in this change)

- [ ] 7.1 US BITs from `trade.gov/bilateral-investment-treaties` (41 treaties)
- [ ] 7.2 Australian investment treaties from the DFAT Australian Treaties Database
- [ ] 7.3 EU and EFTA investment protection agreements
- [ ] 7.4 UNCTAD IIA Navigator catalogue walk, once an export can be obtained without bypassing the site's bot challenge
