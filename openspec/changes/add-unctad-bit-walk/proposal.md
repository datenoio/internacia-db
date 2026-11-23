# Change: Walk the UNCTAD IIA Navigator for bilateral investment treaties

## Why

`add-investment-agreements` added the `investment` type, the `-BIT` id rule, the `BLEU` intblock and the `unctad_iia_id` identifier, and imported Canada's treaties. It names the walk of the UNCTAD IIA Navigator as a follow-up. The Navigator is the standard world catalogue of BITs: each treaty has a stable numeric id, its parties, status, and dates of signature, entry into force and termination. With it the registry can compare investment-treaty links across all countries.

The maintainer asked on 2026-11-23 for a world walk of the BITs in the IIA Navigator. The live site is behind a Cloudflare human check, so the walk reads the latest Wayback Machine capture of each economy page (364 of 366 economy ids, captured in 2025–2026).

## What Changes

- **Implement `unctad_iia_id`** as specified by `add-investment-agreements`: the schema property, the `trade_agreements` export column, and the duplicate check `DUPLICATE_UNCTAD_IIA_ID`. `verification: catalogue` now names the UNCTAD IIA Navigator as a catalogue.
- **Data.** 3,367 new `verification: catalogue` records with `agreement_type: investment`, `unctad_iia_id`, the treaty page as link and the Wayback capture as provenance: 2,163 in force, 623 signed, 537 terminated and 44 listed as terminated without an entry-into-force date (`abandoned`). 101 have the `BLEU` intblock as one party.
- **Mapped records.** 87 existing official records gain `unctad_iia_id`: the 41 U.S. BITs from trade.gov and 46 of Canada's treaties. Where UNCTAD gives another date or status, the record keeps its own and notes UNCTAD's.
- **Identifiers** follow `add-investment-agreements`: the earliest treaty of a pair takes `<pair>-BIT`, each further one `<pair>-BIT-<year>`.
- **Skipped**, and listed in the import report: a treaty with the former Yugoslavia (no country record), a row whose party list includes a third country by mistake, and the Slovak row of the 1990 Canada–Czechoslovakia treaty, which `CACZSK-BIT` already covers.
- **Not in scope.** Treaties with investment provisions (TIPs: FTAs and framework agreements with investment chapters), which the registry covers through trade agreement records, and treaty-content mapping.

## Impact

- Affected specs: `trade-agreements` (walk rules).
- Affected source: schema property `unctad_iia_id`, about 3,400 new files in `data/trade_agreements/`, 87 mapped records.
- Affected code: `internacia_builder/schemas.py`, `trade_agreements.py`, `validate/trade_agreement_rules.py`, `quality_report.py`; one-off scripts `scripts/oneoff/parse_unctad_pages.py` and `import_unctad_bits.py`.
- Affected exports: new nullable column `trade_agreements.unctad_iia_id`; many new `investment` rows.
- Versioning: MINOR.
