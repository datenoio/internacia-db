## 1. Schema and validation

- [x] 1.1 Archive `add-trade-agreements-registry` (or confirm it is archived) so that `openspec/specs/trade-agreements/spec.md` exists
  - [x] 1.1a Archived on main (b24c7b52), which also repointed the links and docstrings; this change fixes the one it missed (`scripts/oneoff/import_govuk_trade_agreements.py`) and folds `investment` (from `add-investment-agreements`, its task 1.5) into the MODIFIED block so that either change can be archived first
- [x] 1.2 Add `suspended` to the `status` enum in `data/schemas/trade_agreements.schema.json`, after `negotiating`; define it in the field description (negotiations launched and then suspended, paused or put on hold, not formally ended; not for agreements in force)
- [x] 1.3 Add `suspended` to the statuses that must not have an `in_force` date in `internacia_builder/validate/trade_agreement_rules.py`
- [x] 1.4 Tests in `tests/test_trade_agreements.py`: a `suspended` record without dates passes; a `suspended` record with `in_force` reports `TRADE_AGREEMENT_STATUS_DATE`; a `suspended` record with three or more parties is not an intblock candidate

## 2. Contract and documentation

- [x] 2.1 Rebuild; check that `contract.json` lists `suspended` for `trade_agreements.status` and `country_trade_agreements.agreement_status` and that no `schema_hash` changes
- [x] 2.2 Add `suspended` to the status list in `docs/data-contract.md`
- [x] 2.3 `changelog.d/` fragment under `### Added`, noting that the release is MINOR

## 3. Data

- [x] 3.1 After datenoio/internacia-db#213 merges, set `status: suspended` on `EFTATSOUZ` and `EFTADZ` and drop the sentence saying the schema has no status for suspended negotiations; refresh `last_verified` and the `status` provenance
- [x] 3.2 Validate (`--fail-on-warning`), build, `check_generated_artifacts.py`, pytest
