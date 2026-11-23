# Change: Walk the UNCTAD IIA Navigator for bilateral investment treaties

## Why

`add-investment-and-trade-relations-types` added the `investment` type with the 41 U.S. bilateral investment treaties from trade.gov, and said that a world walk was not done, so `investment` rows covered the United States only. The UNCTAD Investment Policy Hub's International Investment Agreements Navigator is the standard world catalogue of BITs: each treaty has a stable numeric id, its parties, status, and dates of signature, entry into force and termination. With it the registry can compare investment-treaty links across all countries, as it does for trade agreements.

The maintainer asked on 2026-11-23 for a world walk of the BITs in the IIA Navigator. The live site is behind a Cloudflare human check, so the walk reads the latest Wayback Machine capture of each economy page (captured 2023-12 to 2026-03; nearly all in 2025–2026).

## What Changes

- **New field `unctad_iia_id`** (integer) in `data/schemas/trade_agreements.schema.json` and the `trade_agreements` export, after `aric_id`. Two records SHALL NOT share it (new validator issue `DUPLICATE_UNCTAD_IIA_ID`).
- **`verification: catalogue`** now also covers records taken only from the UNCTAD IIA Navigator.
- **Identifiers.** A pair with one BIT keeps `<pair>-BIT`; when a pair has more than one, each new record takes `<pair>-BIT-<year of signature>`. A bloc party comes first (`BLEUCN-BIT`).
- **New intblock `BLEU`** (Belgium–Luxembourg Economic Union, 1921), because Belgium and Luxembourg conclude BITs jointly as one party. Sources: the Government of Luxembourg. `country_trade_agreements` expands it to Belgium and Luxembourg.
- **Data.** Every BIT row of the IIA Navigator (one per treaty id) becomes a `verification: catalogue` record with `agreement_type: investment`, `unctad_iia_id`, the treaty page as link and the Wayback capture as provenance, unless it maps to an existing record. The 41 U.S. BITs from trade.gov stay `official` and gain `unctad_iia_id`; where UNCTAD gives another date, the record keeps the trade.gov date and notes the UNCTAD one.
- **Status mapping.** `In force` → `in_force`; `Signed (not in force)` → `signed`; `Terminated` → `terminated` with the termination date as `ended`, or `abandoned` with a note when the IIA Navigator gives no date of entry into force.
- **Skipped.** Rows with a party that has no Internacia country or intblock record (the former Yugoslavia), logged in the import report.
- **Not in scope.** Treaties with investment provisions (TIPs: FTAs and framework agreements with investment chapters), which the registry already covers through trade agreement records, and per-treaty mapping of clauses.

## Impact

- Affected specs: `trade-agreements` (UNCTAD identifier, catalogue records, BIT ids).
- Affected source: schema, `data/trade_agreements/` (about 3,100 new files), `data/intblocks/customs/BLEU.yaml`, 41 U.S. BIT records.
- Affected code: `internacia_builder/schemas.py`, `trade_agreements.py`, `validate/trade_agreement_rules.py`, `quality_report.py`; one-off script `scripts/oneoff/import_unctad_bits.py`.
- Affected exports: new nullable column `trade_agreements.unctad_iia_id`; many new `investment` rows in `trade_agreements`, `trade_agreement_parties` and `country_trade_agreements`.
- Versioning: a new nullable column and new rows ship as a MINOR release.
