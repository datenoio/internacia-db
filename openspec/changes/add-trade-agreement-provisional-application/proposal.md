# Change: Record provisional application of trade agreements

## Why

Many trade agreements apply provisionally before, or instead of, their entry into force. The
UK's list of agreements in effect (https://www.gov.uk/guidance/uk-trade-agreements-in-effect)
marks each one as "Full ratification" or "Provisional application", and the cover page of each
UK Treaty Series publication gives the definitive date. The Norway, Iceland and Liechtenstein
agreement, for example, applied to Norway from 1 December 2021 and entered into force on
1 September 2022. EU agreements such as CETA have applied provisionally for years.

The registry has one `in_force` date. It cannot tell an agreement that applies provisionally
from one in force, and records hold whichever date the source gave. WTO RTA-IS and ADB ARIC do
not distinguish the two either.

## What Changes

- **New optional field `provisional_application`** (a date) on trade agreement records and on
  their parties: the date from which at least two parties, or that party, applied the agreement
  provisionally.
- **`in_force` means definitive entry into force.** A record applied only provisionally sets
  `provisional_application` and leaves out `in_force`. Its status stays `in_force`, which now
  reads "in force, or applied provisionally, for at least two parties".
- **Validation.** `status: in_force`, `terminated` or `superseded` needs `in_force` or
  `provisional_application`. `proposed`, `negotiating`, `signed` and `abandoned` records must
  not set `provisional_application`. `ended` must not be earlier than `provisional_application`.
  A linked record that sets `provisional_application` takes `in_force` only from itself, not
  from its intblock's start date.
- **Exports.** `trade_agreements`, `trade_agreement_parties` and the `country_trade_agreements`
  view gain a nullable `provisional_application` column, added after the existing columns.
  `trade_agreement_parties.joined` becomes the earlier of the party's provisional application
  and entry into force, else its signature.
- **Data.** UK records checked against the UK Treaty Series in the same pull request use the
  field where a UK source gives a provisional date. Catalogue records are not migrated: their
  `in_force` may still hold a provisional date.

## Impact

- Affected specs: `trade-agreements` (from `add-trade-agreements-registry`, not yet archived).
- Affected source: `data/schemas/trade_agreements.schema.json`, UK records in
  `data/trade_agreements/`.
- Affected code: `internacia_builder/trade_agreements.py`, `schemas.py`, `contract.py`,
  `validate/trade_agreement_rules.py`, `scripts/check_generated_artifacts.py`.
- Affected exports: one new nullable column in two tables and one view; `contract.json`
  `schema_hash` changes for the three.
- Affected documentation: `docs/data-contract.md`, `docs/ai-consumers.md`.
- Versioning: a new optional field and new columns are a MINOR change. Consumers who read
  `in_force` as "applies since" should use `coalesce(provisional_application, in_force)`.
