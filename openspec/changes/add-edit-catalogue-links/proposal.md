# Change: Walk EDIT into the trade agreements registry and propose EDIT identifiers

## Why

EDIT (Electronic Database of Investment Treaties, https://edit.wti.org/) is an open academic database of the World Trade Institute (University of Bern) and the University of Ottawa. It holds the full texts of 3,462 bilateral investment treaties and 664 other investment agreements (free trade and partnership agreements with investment provisions, framework agreements, plurilateral investment treaties), with their parties, dates of signature, entry into force and termination, and the languages of the text (2026-11-23). Each document has a stable uuid and a public page with the text. The UNCTAD IIA Navigator, which `add-unctad-bit-walk` read from Wayback captures, links no texts; EDIT can add them, cross-check UNCTAD's dates and cover treaties UNCTAD does not list (Taiwan and Kosovo).

The maintainer asked on 2026-11-23 for an EDIT walk: treaty text links on matched records, the missing treaties with investment provisions and plurilateral treaties, notes where EDIT and UNCTAD differ, and an EDIT identifier proposed in OpenSpec only.

## What Changes

- **EDIT walk (done before approval; no new field).** `scripts/oneoff/fetch_edit.py` saves EDIT's treaty list from its public JSON API (metadata only, no texts). `scripts/oneoff/import_edit.py` matches each EDIT document to a registry record by parties and date of signature, with bloc rosters, successor states and hand decisions; the report is `docs/history/edit-match-2026-11-23.md` with a per-document CSV. 3,797 of 4,126 agreements match 3,827 records.
- **Treaty text links.** 3,653 matched records gain a `treaty_text` link to their EDIT document page when EDIT has the text, after their other links. Records that other walks edit at the same time (CIS/EAEU, AfCFTA) are left for later.
- **Date conflicts.** A record keeps its dates, status and verification level. Where EDIT gives another date of signature, entry into force or termination, the record's notes give EDIT's date (462 records), with an EDIT provenance entry. A date that an `official` record or a record linked to an intblock lacks is not noted.
- **New records.** 25 investment treaties that the registry lacked: the EU investment protection agreements with Singapore and Viet Nam and the EU–Angola Sustainable Investment Facilitation Agreement (`verification: official`, from the European Commission and EUR-Lex), and 22 BITs that only EDIT lists, mostly of Taiwan and Kosovo (`verification: catalogue`, EDIT cited for every field). An EDIT-only BIT is added only when EDIT gives its entry into force; the others are held.
- **`verification: catalogue` names EDIT.** The schema description of `catalogue` adds EDIT to the catalogues, as `add-unctad-bit-walk` added the UNCTAD IIA Navigator.
- **Not added.** An agreement with investment provisions that one registry record already covers stays one record (an FTA with an investment chapter, an investment agreement under an ASEAN+1 framework, a protocol of a bloc). Treaties of friendship, commerce and navigation, trade and investment framework agreements, cooperation agreements, constitutive treaties of recorded organisations and model treaties are out of scope or left to other walks; the report lists them.
- **Proposed, after approval: `edit_uuid`.** An optional string field, the uuid of the agreement's EDIT document, exported as a nullable `trade_agreements` column after the other catalogue identifiers. Unlike the other catalogue identifiers, one uuid may sit on several records with the same date of signature, because EDIT lists a treaty of Czechoslovakia, the USSR or Yugoslavia once and the registry has one record per successor state. A one-off pass applies the uuids from the match CSV (`high` and `medium` rows; `low` rows after review). The alternative is no field: the uuid is already the last part of the `treaty_text` URL, but only for the 3,627 documents with a text, and a join on a URL suffix is awkward.

## Impact

- Affected specs: `trade-agreements` (added: EDIT walk, EDIT identifiers).
- Affected source: `data/schemas/trade_agreements.schema.json` (the `catalogue` description now; `edit_uuid` after approval); 3,672 records in `data/trade_agreements/` changed and 25 new.
- Affected code: one-off scripts `scripts/oneoff/fetch_edit.py`, `import_edit.py`, `write_edit_report.py`. After approval: `internacia_builder/schemas.py`, `trade_agreements.py`, `validate/trade_agreement_rules.py`.
- Affected exports: more `treaty_text` links and `investment` rows now; a nullable `edit_uuid` column after approval (a MINOR change).
- Licence: the registry stores EDIT's uuids, dates and document URLs (facts and links), not its texts or its categorisation.
