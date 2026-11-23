# Tasks: beneficiary history from PTA Database versions

Prerequisite: `add-preference-scheme-rosters` (PR 207) is merged and archived.

## 1. History walk

- [x] 1.1 Add a `history` step to `scripts/oneoff/import_wto_ptadb.py`.
  - For each scheme, reload the card until the version dropdown holds the scheme's latest version id, and take that dropdown as the scheme's version list.
  - Post each version id on `ptaBeneficiaries.aspx`, and read the beneficiaries and every sub-scheme list.
  - Check the scheme title on every page.
  - Save the `versions` list in the snapshot.
- [x] 1.2 Report every version with no beneficiaries and every sub-scheme label that changes between versions. Also report a drop of more than half of the beneficiaries between two populated versions. The 2026-11-23 walk reported one drop, Türkiye (153 beneficiaries on 2018-06-29, 66 on 2019-09-16), and label changes for JP, NO, CBERA and GB-DCTS. It also found that the EU GSP version of 2017-06-29 lists China again, although China left the EU GSP in 2015; that is a database issue for the official review of `EU-GSP`.
- [x] 1.3 Run the walk and keep the snapshot outside the repository.

## 2. Dates

- [x] 2.1 In `write`, derive the party `in_force` and `left` dates from consecutive populated versions (design decisions 1 and 2):
  - no `in_force` for baseline beneficiaries, unless the baseline is the scheme's first version;
  - the latest spell in the dates, and earlier spells in `note`.
- [x] 2.2 Add former beneficiaries with `role: beneficiary` and `left`.
- [x] 2.3 Give each sub-scheme `in_force` from its earliest populated version, unless its legal basis gives the date.
- [x] 2.4 Update provenance (the range of versions) and notes (the baseline, "no later than" dates, the number of former beneficiaries).

## 3. Validation

- [x] 3.1 Add `TRADE_AGREEMENT_PARTY_DATE` to `internacia_builder/validate/trade_agreement_rules.py` and `internacia_builder/quality_report.py`.
- [x] 3.2 Run the rule over all records in a dry run. Fix the existing records it reports, or limit the rule to preference schemes, and write the result in design.md.
- [x] 3.3 Write tests for the scenarios in `specs/trade-agreements/spec.md`.

## 4. Linked intblocks

- [x] 4.1 Write the review report for `AGOA`, `CBERA`, `CARIBCAN`, `SPARTECA` and `GSPPLUS` (suggested dates, differences in membership). Do not edit their `includes`.
- [x] 4.2 Open a separate issue or PR for each intblock whose report has differences. The 2026-11-23 report lists them for AGOA (12 countries in the versions but not in `includes`, 1 current in one source only, 6 suggested dates), CBERA (Panama and Curaçao) and GSPPLUS (13 countries in the versions but not in `includes`, Uzbekistan, which joined after the 2017 version, and 5 suggested dates). Opened on 2026-11-23 as issues #232 (AGOA), #233 (CBERA) and #234 (GSPPLUS); the changes wait for the maintainer's decision there.

## 5. Build, documentation and release

- [x] 5.1 Build. Then run the validators, `pytest`, the quality report and the SDK contract suite.
- [x] 5.2 In `docs/ai-consumers.md`, describe former beneficiaries and what "no later than" dates mean. Add a query for the beneficiaries a scheme lost.
- [x] 5.3 Log the history walk in `docs/intblock-sources.md`.
- [x] 5.4 Add a `changelog.d` fragment (MINOR).
- [x] 5.5 Run `openspec validate add-preference-scheme-beneficiary-history --strict`.
