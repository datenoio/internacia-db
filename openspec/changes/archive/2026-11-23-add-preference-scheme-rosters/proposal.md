# Change: Add non-reciprocal preference schemes from the WTO PTA Database

## Why

The trade agreements registry has `agreement_type: preference_scheme`, but only 6 such schemes are in it: `GSP`, `GSPPLUS`, `AGOA`, `CBERA`, `CARIBCAN` and `SPARTECA`. The WTO Preferential Trade Arrangements Database (`https://ptadb.wto.org/ptaList.aspx`, walked on 2026-11-23) lists 37 notified schemes in 38 rows: 17 GSP schemes, 10 LDC-only schemes and 10 other preference programmes. Their beneficiary lists add about 2,200 current grantor–beneficiary links, and about 310 more for 8 schemes that have ended. The registry holds none of these links, except for the 4 waiver programmes and GSP+. Without them `country_trade_agreements` cannot show which countries get non-reciprocal preferences from which grantor. That link is part of how countries are connected by trade arrangements.

The registry cannot store these schemes well today:

- **No party role.** On a non-reciprocal scheme one party grants and the others receive. The intblock `includes` keep this as `contributor` and `recipient`, but the build exports both as `status: party`. A record that lists its own `parties` has no field for the role at all.
- **No sub-schemes.** The EU GSP has two named sub-schemes with their own beneficiary lists, GSP+ and Everything but Arms. Norway, Canada, the United Kingdom, Türkiye, Switzerland, the United States and the EAEU grantors have similar tiers. The PTA Database lists 20 sub-scheme rosters.
- **No catalogue id.** RTA-IS rows have `wto_rta_id`, but PTA Database rows have no matching field.
- **Wrong quality signal.** Every scheme with 3 or more parties and no intblock is reported as `TRADE_AGREEMENT_INTBLOCK_CANDIDATE`. A national GSP with 100 to 177 beneficiaries should not become an intblock. `docs/intblock-sources.md` already rules out national GSP and LDC-only schemes as intblocks.

## What Changes

- **Party role.** A new `parties[].role` field takes `grantor` or `beneficiary`. Every party of a `preference_scheme` record that lists its own parties must set it, and no other record may. `trade_agreement_parties` and `country_trade_agreements` get a `role` column: `grantor` and `beneficiary` on preference schemes, `party` on every other agreement. On a linked intblock, `contributor` maps to `grantor` and `recipient` to `beneficiary`. Linked preference-scheme intblocks may use only these two statuses for their parties. Two data fixes follow: `GSP` (16 `participant` grantors become `contributor`) and `SPARTECA` (AU and NZ become `contributor`, the Forum Island Countries `recipient`).
- **Sub-schemes.** A new optional `parent` field holds the id of the preference scheme a record belongs to. It gives a tree: the `GSP` framework, then a national scheme (`EU-GSP`), then a named sub-scheme (`GSPPLUS`, `EU-GSP-EBA`). A sub-scheme has the same grantors as its parent. Its current beneficiaries are a subset of the parent's, unless the parent is a framework with no beneficiaries. `trade_agreements` gets a `parent` column.
- **Catalogue id.** A new optional `wto_pta_ids` list holds the WTO PTA Database PTA ids of the record, such as `[36]` for the EU GSP. It is a list because one legal instrument can have several catalogue rows: the EAEU unified system of tariff preferences is notified separately by Armenia, Kazakhstan, the Kyrgyz Republic and Russia. Each id may appear in only one record. `trade_agreements` gets a `wto_pta_ids` column.
- **Quality report.** Preference schemes are no longer reported as `TRADE_AGREEMENT_INTBLOCK_CANDIDATE`. The 6 existing intblocks stay as they are.
- **Catalogue import.** 33 of the 37 PTA Database schemes are not in the registry. A one-off script, `scripts/oneoff/import_wto_ptadb.py`, writes 29 scheme records for them: the 4 EAEU rows become one record, and China's LDC scheme is skipped because the database lists no beneficiaries for it. It also writes 16 new sub-scheme records: the 20 PTA Database sub-schemes, less 3 duplicate EAEU rows and the existing `GSPPLUS`. Records use `verification: catalogue`, and provenance cites the PTA Database and the version date of the roster. The script also adds `wto_pta_ids` to the 4 existing records that match a row (`AGOA` 37, `CBERA` 78, `CARIBCAN` 70, `SPARTECA` 80). The "Tariffs & Trade" data of the PTA Database (tariff lines, preference margins, import values) is not imported.
- **Documentation.** Update `docs/intblock-sources.md` (the PTA Database row now covers the registry), the data dictionary, `docs/query-examples.md` (filter by `role`), the AI-consumer guide and current counts. Add a `changelog.d` fragment.
- **Not in scope.** Historical beneficiary dates from the PTA Database version history: one version per roster change, which would give `in_force` and `left` per beneficiary. A follow-up handles them. New intblocks for preference schemes are also out of scope.

## Impact

- Affected specs: `trade-agreements` (added by `add-trade-agreements-registry`, archived on 2026-11-23).
- Affected source:
  - `data/schemas/trade_agreements.schema.json`: `role`, `parent` and `wto_pta_ids`; the `catalogue` description names the PTA Database.
  - `data/trade_agreements/`: 45 new files; `wto_pta_ids` added to `AGOA`, `CBERA`, `CARIBCAN` and `SPARTECA`; `parent` added to `GSPPLUS`.
  - `data/intblocks/pta/GSP.yaml` and `data/intblocks/pta/SPARTECA.yaml`: include statuses.
- Affected code:
  - `internacia_builder/trade_agreements.py`: role and parent derivation.
  - `internacia_builder/schemas.py`: three new columns and the view schema.
  - `internacia_builder/contract.py`: the `country_trade_agreements` SQL and the `role` enum.
  - `internacia_builder/validate/trade_agreement_rules.py`: role, parent and `wto_pta_ids` rules; the candidate exemption.
  - Tests.
- Affected exports:
  - `trade_agreements` gains `parent` and `wto_pta_ids`.
  - `trade_agreement_parties` and `country_trade_agreements` gain `role`.
  - `country_trade_agreements` gains about 2,800 rows: 2,575 beneficiary rows and 183 grantor rows (EU grantor rows expand to the 27 member states).
  - `memberships` shows `contributor` and `recipient` for the `GSP` and `SPARTECA` rosters.
- **Consumer note.** A query that counts trade links between countries from `country_trade_agreements` will count non-reciprocal preferences unless it filters on `role = 'party'` or `agreement_type <> 'preference_scheme'`. The changelog and the query examples say so.
- Versioning: MINOR (5.1.0). The changes are new optional fields, new columns, new records and new enum values.
