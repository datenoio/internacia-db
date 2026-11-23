# Change: Add beneficiary history to preference schemes from WTO PTA Database versions

## Why

`add-preference-scheme-rosters` imported 45 preference schemes. Each lists the beneficiaries of the scheme's latest version in the WTO Preferential Trade Arrangements Database, with no dates. So the registry cannot answer the questions that matter most for non-reciprocal preferences: when a country graduated from a scheme, when it was suspended or reinstated, and who used to benefit. For example, the EU GSP fell from about 176 to about 90 beneficiaries in the 2014 reform, but the registry knows only the 2017 list.

The PTA Database keeps one version per notified change, such as 15 versions for AGOA since 2000 and 5 for the EU GSP. A probe on 2026-11-23 confirmed that the beneficiary page returns the list of any earlier version when its version id is posted: AGOA 2017-06-30 lists 38 beneficiaries, 27 of them with apparel benefits, and EU GSP 2014-01-01 lists 88, 10 of them GSP+. The first versions (AGOA 2000, EU GSP 1971) list no beneficiaries. The lists start with the first notification under the Transparency Mechanism for PTAs (WT/L/806, December 2010).

## What Changes

- **History walk.** `scripts/oneoff/import_wto_ptadb.py` gets a `history` step. It reads every version of each scheme and of each sub-scheme, and adds a `versions` list to the snapshot (version id, "As of" date, beneficiaries, sub-scheme beneficiaries).
- **Beneficiary dates.** Comparing consecutive versions that list beneficiaries gives each party:
  - `in_force`: the date of the version that first lists it. It is not set for a party already in the first such version, unless that version is the scheme's first version.
  - `left`: the date of the first version that no longer lists it.

  Countries that left before the latest version are added as former beneficiaries. Only the latest continuous spell is in the dates; earlier spells go in the party `note`.
- **Sub-scheme dates.** A sub-scheme's `in_force` becomes the date of the earliest version that lists it, instead of the latest one. The record still says that the sub-scheme was in force by then.
- **Validation.** New rule `TRADE_AGREEMENT_PARTY_DATE`: a party's `in_force` is not earlier than the agreement's `in_force`, `left` is not later than its `ended`, and `left` is later than the party's `in_force`.
- **Linked intblocks** (`AGOA`, `CBERA`, `CARIBCAN`, `SPARTECA`, `GSPPLUS`) keep their official rosters. The walk writes a review report of the `joined` and `left` dates it would suggest for them, for hand edits in later PRs.
- **No schema change.** `parties[].in_force`, `parties[].left` and the `former_party` export status already exist.

## Impact

- Affected specs: `trade-agreements`. This change adds requirements to it and depends on `add-preference-scheme-rosters` (PR 207) being merged and archived first.
- Affected source:
  - `data/trade_agreements/` preference-scheme records: party `in_force` and `left`, former beneficiaries, sub-scheme `in_force`, provenance and notes.
  - `scripts/oneoff/import_wto_ptadb.py`.
- Affected code: `internacia_builder/validate/trade_agreement_rules.py` (the party date rule), `internacia_builder/quality_report.py`, and tests.
- Affected exports:
  - `trade_agreement_parties` gains `former_party` rows and `in_force`, `joined` and `left` dates on preference schemes.
  - `trade_agreements.party_count` and `country_trade_agreements` do not change, because they count and list current parties only.
- Versioning: MINOR. There are new rows and values, and no new columns.
