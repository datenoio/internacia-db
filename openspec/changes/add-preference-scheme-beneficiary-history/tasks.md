# Tasks: beneficiary history from PTA Database versions

Prerequisite: `add-preference-scheme-rosters` (PR 207) is merged and archived.

## 1. History walk

- [ ] 1.1 Add a `history` step to `scripts/oneoff/import_wto_ptadb.py`.
  - For each scheme, reload the card until the version dropdown holds the scheme's latest version id, and take that dropdown as the scheme's version list.
  - Post each version id on `ptaBeneficiaries.aspx`, and read the beneficiaries and every sub-scheme list.
  - Check the scheme title on every page.
  - Save the `versions` list in the snapshot.
- [ ] 1.2 Report every version with no beneficiaries and every sub-scheme label that changes between versions. Also report a drop of more than half of the beneficiaries between two populated versions.
- [ ] 1.3 Run the walk and keep the snapshot outside the repository.

## 2. Dates

- [ ] 2.1 In `write`, derive the party `in_force` and `left` dates from consecutive populated versions (design decisions 1 and 2):
  - no `in_force` for baseline beneficiaries, unless the baseline is the scheme's first version;
  - the latest spell in the dates, and earlier spells in `note`.
- [ ] 2.2 Add former beneficiaries with `role: beneficiary` and `left`.
- [ ] 2.3 Give each sub-scheme `in_force` from its earliest populated version, unless its legal basis gives the date.
- [ ] 2.4 Update provenance (the range of versions) and notes (the baseline, "no later than" dates, the number of former beneficiaries).

## 3. Validation

- [ ] 3.1 Add `TRADE_AGREEMENT_PARTY_DATE` to `internacia_builder/validate/trade_agreement_rules.py` and `internacia_builder/quality_report.py`.
- [ ] 3.2 Run the rule over all records in a dry run. Fix the existing records it reports, or limit the rule to preference schemes, and write the result in design.md.
- [ ] 3.3 Write tests for the scenarios in `specs/trade-agreements/spec.md`.

## 4. Linked intblocks

- [ ] 4.1 Write the review report for `AGOA`, `CBERA`, `CARIBCAN`, `SPARTECA` and `GSPPLUS` (suggested dates, differences in membership). Do not edit their `includes`.
- [ ] 4.2 Open a separate issue or PR for each intblock whose report has differences.

## 5. Build, documentation and release

- [ ] 5.1 Build. Then run the validators, `pytest`, the quality report and the SDK contract suite.
- [ ] 5.2 In `docs/ai-consumers.md`, describe former beneficiaries and what "no later than" dates mean. Add a query for the beneficiaries a scheme lost.
- [ ] 5.3 Log the history walk in `docs/intblock-sources.md`.
- [ ] 5.4 Add a `changelog.d` fragment (MINOR).
- [ ] 5.5 Run `openspec validate add-preference-scheme-beneficiary-history --strict`.
