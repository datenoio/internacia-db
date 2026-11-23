### Added

- Beneficiary history for the preference schemes imported from the WTO Preferential Trade
  Arrangements Database, read from every database version (walked 2026-11-23; OpenSpec
  `add-preference-scheme-beneficiary-history`).
  - A beneficiary that a later version first lists has `in_force`. A beneficiary that a
    version drops has `left`, and countries that graduated or were removed are now listed as
    former beneficiaries (`trade_agreement_parties.status = 'former_party'`): 439 rows in 30
    schemes, such as the beneficiaries that left `EU-GSP` in the 2014 reform.
  - These are no-later-than dates. Beneficiaries already in the earliest list (about 2011)
    have no `in_force`, and earlier spells are in the party `note`.
  - Older sub-scheme lists are dated only when their size matches the count in the
    database's dropdown label. Current lists are unchanged.
- Validation rule `TRADE_AGREEMENT_PARTY_DATE`: a party's `in_force` is not before the
  agreement's, its `left` is not after the agreement's `ended`, and `left` is after its own
  `in_force`.

### Fixed

- `EFTAES`: Austria and Sweden no longer have a `left` date of 1995-01-01. That is when they
  left EFTA, after this agreement had already ended in 1986.
- `CEFTA-1992`: `ended` is 2007-01-01, when Romania, Bulgaria and Croatia stopped being
  parties, not 2004-05-01.
