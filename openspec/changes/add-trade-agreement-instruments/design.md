# Design: trade agreement instruments

## Context

`add-trade-agreements-registry` made the registry hold one record per legal instrument. It also said that upgrades and second protocols listed separately in ARIC become one record with a note. That kept the record count honest, but the history of an agreement ended up in prose.

The sources that list such instruments, as checked on 2026-11-23:

| Source | What it lists | Rows |
|---|---|---|
| WTO RTA-IS export, sheet `RTA Changes` | Notified changes: Joint Committee decisions, protocols, CEPA Supplements, supplementary agreements | 359. 127 amend 43 registry records; 232 are LAIA partial-scope agreements |
| China FTA Network (MOFCOM) | Upgrade, optimization and enhancement protocols, second phases, early harvest arrangements, often not yet notified to the WTO | 11 records in datenoio/internacia-db#211 |
| ADB ARIC | Upgrades as separate catalogue rows | Merged into one record each during the ARIC import |

Every WTO amendment row maps to a registry record through `wto_rta_id`; none is left unmapped. One WTO row can describe two instruments. The 2017 Mainland–Hong Kong and Mainland–Macao rows each notify both an Investment Agreement and an Agreement on Economic and Technical Cooperation.

## Goals and non-goals

Goals:

- every instrument that amends or adds to an agreement is a dated, typed and sourced item of that agreement's record;
- the instruments of every agreement can be queried in one table;
- no new record is created for an amendment.

Non-goals:

- tariff schedules, rules-of-origin annexes and the substance of a decision;
- negotiation rounds;
- treaty text;
- depth or coverage scores;
- per-party entry into force of an instrument (open question 1).

## Decisions

### 1. Field shape

`instruments` is an optional list on a registry record. An item has these fields; additional properties are rejected:

| Field | Required | Notes |
|---|---|---|
| `id` | yes | Unique within the record, pattern `^[a-z0-9][a-z0-9-]*$`. It is written by hand or by the import, such as `upgrade-2018`, `supplement-10` or `jc-2012-1`, and never changes once published |
| `kind` | yes | See decision 2 |
| `name` | yes | English name as used by the source |
| `other_names` | no | Same shape as on records (`lang`, `name`) |
| `status` | yes | `negotiating`, `signed`, `in_force`, `terminated`, `abandoned` |
| `signed`, `in_force`, `ended` | by status | ISO or partial dates, with the same rules as records: `signed` needs `signed`; `in_force` and `terminated` need `in_force`; `terminated` needs `ended`; `negotiating`, `signed` and `abandoned` have no `in_force` |
| `coverage` | no | Subset of `goods`, `services`, `investment`. The WTO column `Changes affect` gives the first two |
| `notes` | no | Legal facts, such as staggered entry into force or the fact that an instrument was replaced by a later one |
| `provenance` | yes | Same shape as record provenance, at least one entry |

`proposed` and `superseded` are left out. An upgrade under study has no legal existence yet. An instrument that a later one replaces is `terminated`, with a note.

### 2. Kinds

| Kind | Use for | Examples |
|---|---|---|
| `amending_protocol` | A protocol or agreement that amends the agreement, whatever the parties call it: upgrade, optimization, enhancement, second phase, supplement | `CNSG` 2018 Upgrade Protocol; `CNPE` Optimization Protocol; `CNMO` Supplements I–X; `CNPK` second-phase protocol |
| `supplementary_agreement` | A further agreement under the same agreement that covers a new area | `CNMO` Agreement on Trade in Services (2015); `CNHK` Investment Agreement (2017); `ACFTA` agreements on services and investment |
| `early_harvest` | An early harvest arrangement under the agreement | `CNNI` early harvest (2022) |
| `joint_committee_decision` | A decision of the agreement's joint body that amends it or its annexes | EFTA Joint Committee decisions |
| `exchange_of_letters` | An exchange of letters that launches or settles part of the agreement | `CNNZ` services negative-list negotiations (2024) |
| `other` | Anything else a source lists as a change | |

### 3. Instrument or separate record

- **Amends or adds to the agreement among its parties: instrument.** This holds even when the instrument enters into force for some parties first.
- **Replaces the agreement: separate record.** The new record gets `supersedes` and the old one gets `superseded_by`. An example is the modernized Canada–Ukraine FTA of 2023.
- **A new agreement concluded under an umbrella treaty, with its own parties: separate record.** The LAIA partial-scope agreements are the example. The 232 such WTO rows are left for a later change, which can decide how to link a record to its umbrella treaty.
- **Accession of a new party: party data.** It goes in `parties[].in_force` on a record, or in `includes[].joined` on a linked intblock, not in `instruments`.
- **Early harvest arrangements.**
  - An arrangement under an agreement that already has a record is an instrument (`CNNI`).
  - Where the arrangement is the only instrument signed so far, the record is the arrangement (`CNHN`, `CGCN`, `CNKE`).
  - Once the full agreement is signed, the record takes the agreement's name and dates. The arrangement then becomes an instrument with `kind: early_harvest`, and the record id stays the same.
- **Upgrade negotiations: a `negotiating` instrument.** They are recorded once launched, with no dates. Rounds are not recorded.

### 4. The agreement's own fields

`status`, `signed`, `in_force` and `ended` describe the agreement itself. An instrument in force does not change them. `CNPE` keeps `in_force: 2010-05-01` after its Optimization Protocol entered into force on 2026-11-01. Consumers who want the latest change read `max(in_force)` from `trade_agreement_instruments`.

### 5. Export

`trade_agreement_instruments` has one row per record and instrument. Its columns:

- `agreement_id` and `instrument_id`, both not null; together they are the primary key;
- `kind`, `name`, `status`, `signed`, `in_force`, `ended`;
- `coverage` (`list<string>`), `other_names`, `notes`, `provenance`.

`agreement_id` references `trade_agreements.id`. The enum columns are open, as in the other registry tables. A linked record's instruments come from the registry record, not from the intblock.

The table is exported as Parquet, JSONL and DuckDB, and listed in `contract.json`, `datapackage.json` and the manifests. A new resource is additive, so the release is MINOR (contract 5.1).

### 6. Validation

- **JSON Schema.** It checks the item shape, the enums, the `id` pattern, the dates and the absence of extra properties. A numeric trade field on an instrument is rejected, as on a record.
- **Validator errors:**
  - a duplicate instrument `id` within a record (`DUPLICATE_TRADE_AGREEMENT_INSTRUMENT`);
  - a status–date conflict (`TRADE_AGREEMENT_INSTRUMENT_DATE`);
  - `ended` earlier than `signed` or `in_force`, compared at shared precision as on records.
- **Quality report only** (`TRADE_AGREEMENT_INSTRUMENT_BEFORE_AGREEMENT`): an instrument other than an early harvest arrangement that is signed before its record's `signed` date.

  This is not an error. On a linked record the agreement dates can come from the intblock. `ACFTA` reads `founded: 2004-11-29`, the signature of the Agreement on Trade in Goods, while the Framework Agreement dates from 2002.

### 7. Backfill

1. **MOFCOM.** Move the upgrade and early harvest sentences that datenoio/internacia-db#211 wrote into `notes` on 11 records into `instruments`, and delete the repeated sentences.

   `ACFTA` 2.0 is `in_force` from 2019-10-22, the date for all parties. A note records that it applied to China and Viet Nam first, from 2016-07-01.

   `CNKR` second phase, `CHCN` before signature, and the `CNNZ` services negotiations become `negotiating` items. `CHCN` is now `signed`: the protocol was signed on 2026-10-30.
2. **WTO `RTA Changes`.** A one-off script, `scripts/oneoff/import_wto_rta_changes.py`, imports the 127 amendment rows:
   - each row maps to a record through `wto_rta_id`;
   - `kind` is read from the remarks (Decision, Protocol, Supplement, Agreement) and checked by hand;
   - `coverage` comes from `Changes affect`;
   - dates are converted from Excel serial dates;
   - provenance cites the RTA ID card.

   The row with no dates is reported and left for hand review. A row that lists two instruments becomes two items.
3. **Overlap.** `ACFTA`, `CLCN` and `CNPK` appear in both sources. When MOFCOM and the WTO describe the same instrument, it becomes one item with both provenance rows. An official text or party government wins on dates. A conflict between them is recorded in the item's `notes`.

   Two examples:
   - The WTO gives 2019-03-01 for the entry into force of the China–Chile protocol, which MOFCOM's #211 notes do not date.
   - For the `ACFTA` 2.0 protocol, the WTO gives signature on 2015-11-21 and entry into force on 2016-07-01, the first parties' date. MOFCOM gives signature on 2015-11-22 and entry into force for all parties on 2019-10-22. The item keeps the MOFCOM dates and notes the WTO dates.

## Risks

- **Over-recording technical decisions.** Many EFTA Joint Committee decisions only transpose HS nomenclature. The default is to record every notified change, because filtering would be a judgment the sources do not make. `kind` lets consumers filter them out.
- **Instrument ids chosen by hand.** If an id is renamed, it breaks the primary key consumers join on. The pattern and the rule that ids never change once published cover this, and so does a test that keeps the id set of published instruments stable.
- **Partial adoption.** Most records will have no instruments for a long time. The documentation says that an empty list means "none recorded", not "none exist".

## Open questions

1. Per-party entry into force of an instrument, such as `ACFTA` 2.0 entering into force for China and Viet Nam first. The default is one date (the date it applied to all parties, or the first date where that is all the source gives) plus a note. A per-party list can follow if a source needs it.
2. Should `trade_agreements` gain a derived `instrument_count` or `last_instrument_in_force` column? The default is no; the consumer joins the new table.
3. Should the import skip Joint Committee decisions that only transpose HS nomenclature? The default is no (see Risks).
