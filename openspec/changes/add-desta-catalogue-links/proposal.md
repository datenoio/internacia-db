# Change: Add DESTA identifiers to the trade agreements registry

## Why

DESTA (Design of Trade Agreements, https://www.designoftradeagreements.org/downloads/) is an academic catalogue of preferential trade agreements. Its list of treaties v2.3 has 903 base treaties signed up to 2025, plus 208 accessions, 72 withdrawals, 77 protocols, 72 consolidated versions and 78 negotiations. About 400 of the base treaties are not WTO-listed, most of them bilateral. DESTA also publishes country-pair files and a coded dataset of agreement design. All of them key agreements on the DESTA `number`.

A walk on 2026-11-23 (`scripts/oneoff/match_desta.py`, report `docs/history/desta-match-2026-11-23.md`) matched 685 DESTA base treaties to registry records on `main` and in the open pull requests, found 90 ambiguous and 128 missing. The walk added 30 missing agreements, each with status and dates from a depositary, a party government or the WTO. Without the DESTA number on the record, users can join the registry to DESTA's files only by name, and DESTA names are short (`Argentina Bolivia`) and not unique (one country pair often has three or four DESTA treaties).

The maintainer asked on 2026-11-23 for a DESTA catalogue field proposed the same way as `aric_id` and `gptad_id`.

## What Changes

- **New optional field `desta_id`** (integer, minimum 1) on trade agreement records: the `number` of the agreement's base treaty in the DESTA list of treaties. It is exported as a nullable `int64` column of `trade_agreements`, after the other catalogue identifiers (`gptad_id`, and `dta_id` if `add-dta-catalogue-links` lands first).
- **`desta_id` is a catalogue identifier.** It joins `wto_rta_id`, `aric_id` and `gptad_id` in the uniqueness rule of `add-gptad-catalogue-links`: a value on two records is reported as `DUPLICATE_IDENTIFIER`.
- **Only base treaties map.** DESTA rows of type accession, withdrawal, protocol or amendment, consolidated version and negotiation (numbers such as `3+1`, `8_1`, `694a`) map to no record: the registry keeps accessions and withdrawals as party dates of the agreement, and amendments as instruments or notes. Two DESTA base treaties that are one instrument in the registry (an early harvest and its agreement, the 1965 and 1968 CARIFTA texts) give the record the number of the treaty with the closer date of signature.
- **Catalogue rule for records created from DESTA.** DESTA gives a year of signature and of entry into force, not a status. A record created from DESTA SHALL take its status and dates from another source (a depositary, a party government, UNTS, EUR-Lex or the WTO) and cite DESTA only for listing the agreement, the rule `add-gptad-catalogue-links` set for GPTAD. The 30 records of the 2026-11-23 walk already follow it and cite their DESTA number in a `desta_id` provenance entry.
- **One-off import.** After approval, one pass writes `desta_id` from the walk's per-treaty CSV (`desta_number`, `record_id`, `method`, `confidence`): `high` and `medium` matches as they are, `low` (ambiguous) ones after review. It changes no status, date, party or verification level.
- **Not in scope.** DESTA's coded design dataset and its depth indices (a depth measure, out of scope under the registry scope requirement), DESTA's country-pair panel, and DESTA's accession and withdrawal years as party dates (the walk lists them as gaps to check against official sources).

## Impact

- Affected specs: `trade-agreements` (added: DESTA identifiers).
- Affected source: `data/schemas/trade_agreements.schema.json`; `data/trade_agreements/*.yaml` (`desta_id` on matched records).
- Affected code: `internacia_builder/trade_agreements.py`, `internacia_builder/schemas.py`, `internacia_builder/validate/trade_agreement_rules.py`; a one-off backfill script reading the match CSV.
- Affected exports: `trade_agreements` gains `desta_id`, so its `schema_hash` changes; `contract.json` lists the column.
- Affected documentation: `docs/data-contract.md`, `docs/ai-consumers.md`, `docs/intblock-sources.md`, `llms.txt`, `llms-full.txt`, changelog fragment.
- Versioning: a new optional column is a MINOR change.
- Depends on: `add-gptad-catalogue-links` (datenoio/internacia-db#209: `gptad_id` and the uniqueness rule) and `add-dta-catalogue-links` (datenoio/internacia-db#219: `dta_id`, the column before `desta_id`). Implementation waits for approval of this change and for both pull requests to merge.
- Licence: the registry takes identifiers (facts) and links to the DESTA downloads page; it does not copy DESTA's coding.
