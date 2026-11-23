# Change: Add GPTAD identifiers and treaty text links to the trade agreements registry

## Why

The trade agreements registry cites two catalogues, WTO RTA-IS (`wto_rta_id`) and ADB ARIC (`aric_id`). Neither links to the text of an agreement. Most registry records (713 of 839) are `verification: catalogue`, and the spec allows `official` only after the parties and dates are checked against the treaty text, a depositary or a party government.

The World Bank Global Preferential Trade Agreements Database (GPTAD, https://wits.worldbank.org/gptad/) holds the full text of 352 agreements as PDFs, including agreements that were never notified to the WTO. Each agreement has a numeric id in the database (`dispIDS`), and its indexed provisions include the official name of the text and, for notified agreements, the WTO document symbol. The catalogue was last updated around 2010, so its in-force statuses and agreement types are not reliable, but its texts and ids are stable. A walk on 2026-11-22 matched about 280 GPTAD agreements to registry records by parties and date of signature.

The maintainer chose on 2026-11-23 to start the GPTAD integration with its identifiers and text links, and then asked for the agreements that GPTAD lists and the registry lacks.

## What Changes

- **New optional field `gptad_id`** (integer, minimum 1) on trade agreement records: the GPTAD agreement id. It is exported as a nullable `int64` column of `trade_agreements`, after `aric_id`.
- **Catalogue identifiers are unique.** `wto_rta_id`, `aric_id` and `gptad_id` each appear on at most one record; the validator reports a duplicate as `DUPLICATE_IDENTIFIER`. The current data already meets this for `wto_rta_id` and `aric_id`.
- **New link type `treaty_text`** in `links[].type`: a URL of the full text of the agreement (a depositary, a party government or a catalogue copy such as a GPTAD PDF). The registry stores the URL, not the text.
- **Linked records keep their own links.** A record linked to an intblock may list `links`; the export lists the intblock's links followed by the record's own, without repeating a URL. Today the export reads links only from the intblock, so a text link on a linked record would be lost.
- **One-off GPTAD walk.** `scripts/oneoff/fetch_gptad.py` saves the library table and the indexed provisions of every agreement; `scripts/oneoff/import_gptad.py` maps GPTAD agreements to registry records (by hand against the official name of the text, then by parties and date of signature) and writes `gptad_id` and a `treaty_text` link to the GPTAD PDF. The WTO document symbols in GPTAD are not used: the RTA-IS export has none to join them to. The walk changes no status, date or verification level of a mapped record.
- **New records for agreements GPTAD lists and the registry lacks**, after reading each text: bilaterals not notified to the WTO, ALADI complementation agreements, CARICOM agreements with Latin American partners, the ASEAN+1 framework agreements, predecessors of registry records (with `superseded_by`, and `supersedes` on the successor), and the founding treaties of economic communities that are already intblocks (as linked records). Texts that grant only most-favoured-nation treatment, and organisation charters without trade commitments, are skipped. GPTAD statuses date from around 2010, so status, end dates and successors cite another source (ALADI, SICE, the ASEAN Secretariat, party governments). New records are `verification: catalogue` unless linked to an intblock.
- **`Catalogue-level records` names GPTAD** as a catalogue, next to WTO RTA-IS and ADB ARIC.
- **Not in scope.** Raising `verification` to `official` from the texts, and the GPTAD provision index (its coverage of chapters such as labour or environment is a depth measure, out of scope under the registry scope requirement). These follow in later changes.

## Impact

- Affected specs: `trade-agreements` (modified: parties and intblock link, catalogue-level records; added: GPTAD identifiers, treaty text links).
- Affected source: `data/schemas/trade_agreements.schema.json`; `data/trade_agreements/*.yaml` (`gptad_id` and `links` on mapped records, new records, `supersedes` on successors).
- Affected code: `internacia_builder/trade_agreements.py` (links of linked records, `gptad_id`), `internacia_builder/schemas.py`, `internacia_builder/validate/trade_agreement_rules.py`; new `scripts/oneoff/fetch_gptad.py` and `scripts/oneoff/import_gptad.py`.
- Affected exports: `trade_agreements` gains `gptad_id`, so its `schema_hash` changes; `contract.json` lists the column; `links` may hold `treaty_text`.
- Affected documentation: `docs/data-contract.md`, `docs/ai-consumers.md`, `docs/intblock-sources.md`, `llms.txt`, `llms-full.txt`, data dictionary, changelog fragment.
- Versioning: a new optional column and a new open enum value are a MINOR change.
- Licence: GPTAD pages state "All rights reserved". The registry takes facts (ids, the PDF address) and links to the texts; it does not copy them.
