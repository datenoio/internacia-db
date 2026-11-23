# Change: `suspended` status for trade agreement negotiations on hold

## Why

`trade_agreements.status` cannot express negotiations that the parties launched and then put on
hold without ending them. Official sources use this state widely:

- **EFTA** labels its partner pages "Negotiations suspended" (Russia/Belarus/Kazakhstan: launched
  in January 2011, 11 rounds) or "Negotiations on hold" (Algeria: four rounds in 2007–2008;
  Honduras's accession to the EFTA-Central America FTA).
- **EU DG Trade** keeps a separate "on hold" table with 19 rows. Among them: EU-GCC "suspended since
  2008"; the Central Africa and Eastern and Southern Africa EPA negotiations with the states that
  did not sign, "paused until further notice in 2011"; and the Myanmar investment protection
  agreement.

Today such rows have to be recorded as `negotiating`, which states that talks are active, or as
`abandoned`, which states that they are no longer pursued. Both are wrong. The records `EFTATSOUZ`
and `EFTADZ` (datenoio/internacia-db#213) carry `negotiating` plus a note saying that the schema has
no better value. A consumer who filters `status = 'negotiating'` to find live talks gets talks that
have been frozen for more than 15 years.

## What Changes

- `status` gains the value `suspended`: negotiations were launched and then suspended, paused or
  put on hold by the parties, and have not been formally ended. If talks resume, the record goes
  back to `negotiating`. If they are formally ended or not pursued, it becomes `abandoned`.
- `suspended` covers negotiations only. An agreement in force whose application is suspended, in
  whole or for one party, keeps `in_force` and records the suspension in `notes`. Per-party pauses
  (one state's accession on hold) stay in `parties[].note`.
- Date rules: a `suspended` record needs no date and SHALL NOT have an `in_force` date, like
  `negotiating`. It is not an intblock candidate, because candidates are only `signed` or
  `in_force` records.
- Schema description, validator date rule, contract enums (`trade_agreements.status`,
  `country_trade_agreements.agreement_status`), `docs/data-contract.md` and tests are updated.
- Data: `EFTATSOUZ` and `EFTADZ` move to `suspended` and lose the "no status for that" sentence.
  Other candidates found in the official sources are recorded when those sources are walked, for
  example a new EU-GCC record.

## Alternatives considered

- **`on_hold`.** EFTA and the EU use "on hold", "paused" and "suspended" interchangeably.
  `suspended` was chosen because it is the term used where a source names the state as a status
  ("Negotiations suspended", "suspended since 2008").
- **A `suspended` date field.** It would record when talks stopped. Sources rarely give an exact
  date (the EU gives only a year), and a new column changes the table's `schema_hash`. The year
  goes in `notes` instead; a date field can be proposed later if the walks show enough data.
- **Keep `negotiating` plus a note.** This is the current workaround. It leaves the filter problem
  in place and hides the state from every export.

## Not in scope

- Suspension of agreements already in force (trade sanctions, suspended preferences under GSP or
  AGOA).
- Walking the EU and UK sources for further candidates. That is data work under the existing
  registry policy.

## Impact

- Affected specs: `trade-agreements` (requirement "Trade agreement source records"). That
  capability is still in the active change `add-trade-agreements-registry`, whose remaining open
  task is data work (7.5). Archive it before this change so that the MODIFIED requirement applies
  to the archived spec.
- Affected source: `data/schemas/trade_agreements.schema.json` (enum and description); two records
  in `data/trade_agreements/`.
- Affected code: `internacia_builder/validate/trade_agreement_rules.py` (the set of statuses that
  must not have `in_force`); `tests/test_trade_agreements.py`.
- Affected exports: `contract.json` enums for `trade_agreements.status` and
  `country_trade_agreements.agreement_status` gain one value. Both enums are open, so this is a
  MINOR change (contract 5.1); `schema_hash` does not change. The internacia SDK treats enums as
  open and needs no change.
- Affected documentation: `docs/data-contract.md` (status list), a `changelog.d/` fragment.
