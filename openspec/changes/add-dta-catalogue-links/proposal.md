# Change: Add World Bank Deep Trade Agreements identifiers to the trade agreements registry

## Why

The World Bank Deep Trade Agreements database (DTA, https://datatopics.worldbank.org/dta/) codes the content of 400 preferential trade agreements notified to the WTO and signed between 1957 and 2022. Version 2 (23 January 2024) has DTA 1.0 (horizontal content: 52 policy areas, with legal enforceability) and DTA 2.0 (vertical content: about 1,070 provisions in 18 policy areas, also published as one file per chapter). Every file keys its agreements on the same numeric id, `WB ID` (1–400, column `WBID` in the content sheets).

A comparison with the registry on 2026-11-23 found that the `Agreements` sheet of the DTA files is a copy of the WTO RTA-IS export (its read-me sheet says so). It is older than the export that the registry already walked, so its dates and statuses add nothing. The one new fact is the `WB ID`. Without it, users cannot join a registry record to the DTA content files except through `wto_rta_id`. That join fails for the four agreements DTA gives a placeholder RTA ID (`999A1`–`999A3`) or an RTA ID that the current WTO export no longer lists (136, SPARTECA).

The maintainer chose on 2026-11-23 to add the DTA id as a catalogue identifier, like `gptad_id`.

## What Changes

- **New optional field `dta_id`** (integer, minimum 1) on trade agreement records: the agreement's `WB ID` in the World Bank DTA database. It is exported as a nullable `int64` column of `trade_agreements`, after `gptad_id`.
- **`dta_id` is a catalogue identifier.** It joins `wto_rta_id`, `aric_id` and `gptad_id` in the uniqueness rule: a value set on two records is reported as `DUPLICATE_IDENTIFIER`.
- **One-off DTA walk.** `scripts/oneoff/import_dta.py` reads the `Agreements` sheet of a DTA XLSX file and maps each `WB ID` to a registry record. It maps by `wto_rta_id` first and then by hand for the four placeholder or retired RTA IDs. Accessions and EC/EU enlargements map to no record: the registry records them as party dates of the agreement acceded to. The walk writes only `dta_id`. It adds no record and changes no status, date, party or verification level.
- **Not in scope.** The DTA content data: policy-area coverage, legal enforceability and provision coding. These are depth measures, out of scope under the registry scope requirement. Users join them on `dta_id`. Also out of scope: the DTA `Bilateral Information` country-pair panel, and gaps in the registry that the comparison found (entry into force of records linked to an intblock, party accession dates, date and roster conflicts). Those come from WTO RTA-IS or official sources in later changes.

## Impact

- Affected specs: `trade-agreements` (added: DTA identifiers).
- Affected source: `data/schemas/trade_agreements.schema.json`; `data/trade_agreements/*.yaml` (`dta_id` on mapped records).
- Affected code: `internacia_builder/trade_agreements.py`, `internacia_builder/schemas.py`, `internacia_builder/validate/trade_agreement_rules.py`; new `scripts/oneoff/import_dta.py`.
- Affected exports: `trade_agreements` gains `dta_id`, so its `schema_hash` changes; `contract.json` lists the column.
- Affected documentation: `docs/data-contract.md`, `docs/ai-consumers.md`, `docs/intblock-sources.md`, `llms.txt`, `llms-full.txt`, changelog fragment.
- Versioning: a new optional column is a MINOR change.
- Depends on: `add-gptad-catalogue-links` (the uniqueness rule and the column order).
- Licence: the registry takes identifiers (facts), not the DTA content. The licence of the DTA files was not checked: the World Bank data catalogue API returned HTTP 429.
