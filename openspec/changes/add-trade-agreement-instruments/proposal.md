# Change: Add instruments to trade agreement records

## Why

The registry keeps one record per legal instrument (`add-trade-agreements-registry`, design decision 7). It has no place for the instruments that amend an agreement or add to it after signature: upgrade protocols, supplements, supplementary agreements, early harvest arrangements and joint committee decisions. Today these facts are free text in `notes`, so they cannot be queried or dated. Examples are the China–Singapore 2018 Upgrade Protocol and 2023 further upgrading protocol, the ASEAN–China version 2.0 and 3.0 protocols, and the ten Supplements to the Mainland–Macao CEPA.

Two sources already hold this data:

- **China FTA Network (MOFCOM).** datenoio/internacia-db#211 wrote upgrade and early harvest facts into the `notes` of 11 records: `ACFTA`, `CHCN`, `CLCN`, `CNGE`, `CNKR`, `CNNI`, `CNNZ`, `CNPE`, `CNPK`, `CNSG` and `SACUCN`.
- **WTO RTA-IS.** The `RTA Changes` sheet of the full export has 359 rows. 127 of them are amendments to 43 agreements the registry already holds, each with the signature and entry-into-force dates of the change. The other 232 rows are partial-scope agreements concluded under the LAIA (ALADI) treaty. Those are agreements with their own parties, not amendments.

A structured list keeps one record per agreement and makes the history of each agreement queryable. It also lets a consumer tell an agreement that has been upgraded from one that has not, without parsing prose.

## What Changes

- **New optional field `instruments`** on `data/trade_agreements/<ID>.yaml` records. It holds the instruments that amend or add to the agreement among its parties. Each item has:
  - `id`: unique within the record;
  - `kind`: `amending_protocol`, `supplementary_agreement`, `early_harvest`, `joint_committee_decision`, `exchange_of_letters` or `other`;
  - `name`, and optional `other_names`;
  - `status`: `negotiating`, `signed`, `in_force`, `terminated` or `abandoned`;
  - `signed`, `in_force` and `ended` dates;
  - an optional `coverage` list (`goods`, `services`, `investment`);
  - optional `notes`, and a required `provenance` list.

  The item shape has no numeric trade fields.
- **Boundary rules.** An agreement that replaces another is a separate record with `supersedes`. An agreement concluded under an umbrella treaty with its own parties (ALADI partial-scope agreements) is a separate record. An accession is party data, not an instrument. An early harvest arrangement that precedes the agreement is an instrument of the agreement's record.
- **The agreement's own fields do not change.** `status`, `signed` and `in_force` stay those of the agreement itself. An upgrade in force does not change them.
- **Validation.** JSON Schema covers the item shape. Validator rules check:
  - instrument ids are unique within a record;
  - status and dates agree, with the same rules as records;
  - `ended` is not earlier than `signed` or `in_force`.

  The quality report lists instruments signed before the agreement they belong to, except early harvest arrangements, and the validator does not fail on them.
- **Export.** A new `trade_agreement_instruments` table, with primary key `agreement_id` and `instrument_id` and a foreign key to `trade_agreements.id`. It is exported as Parquet, JSONL and DuckDB and listed in `contract.json` and `datapackage.json`. `kind`, `status` and `coverage` are open enums. Adding the table is a MINOR change.
- **Backfill.**
  1. Move the MOFCOM facts from `notes` into `instruments` on the 11 records and delete the repeated sentences.
  2. Import the 127 WTO amendment rows with a one-off script, mapped by `wto_rta_id`.
- **Not in scope.**
  - Tariff schedules, rules-of-origin annexes, the content of decisions, negotiation rounds and treaty text.
  - Per-party entry-into-force dates of an instrument (see `design.md`).
  - The 232 ALADI partial-scope agreements, which need their own records in a later change.

## Impact

- Affected specs: `trade-agreements`, which gains requirements. That capability is still defined only in the active change `add-trade-agreements-registry`, so this change adds requirements to it and modifies none.
- Affected source: `data/schemas/trade_agreements.schema.json` and `data/trade_agreements/*.yaml` (51 records gain `instruments`: 43 from WTO and 11 from MOFCOM, with `ACFTA`, `CLCN` and `CNPK` in both).
- Affected code:
  - `internacia_builder/trade_agreements.py` (rows);
  - `schemas.py` (`get_trade_agreement_instruments_schema`), `export.py`, `contract.py`, `build.py`;
  - `internacia_builder/validate/trade_agreement_rules.py` and `registry.py`;
  - `scripts/check_generated_artifacts.py`;
  - a one-off `scripts/oneoff/import_trade_agreement_instruments.py`.
- Affected exports: one new resource. Existing tables and columns are unchanged.
- Affected documentation: `docs/data-contract.md`, `docs/ai-consumers.md`, `docs/query-examples.md`, the agent shims, and a changelog fragment.
- Versioning: MINOR (contract 5.1).
- Depends on datenoio/internacia-db#211 for the MOFCOM notes to move. The schema and export work does not depend on it.
