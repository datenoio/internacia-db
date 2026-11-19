## 1. Labels (PATCH)
- [x] 1.1 Export `includes[].name` for `type: country` from the country `name` (`internacia_builder/export.py`)
- [x] 1.2 Make `name` optional for `type: country` includes in `intblocks.schema.json` (if/then)
- [x] 1.3 Normalize the 3,501 differing source names with a one-off script; verify only `name` changed
- [x] 1.4 `INCLUDE_NAME_MISMATCH`: exact comparison with the country `name`, validator warning, registry update
- [x] 1.5 Update tooling that writes includes to write the country `name` (the wbgroup roster sync writes it on every country entry)
- [x] 1.6 Tests: export label, optional name, rule severity

## 2. Associate statuses (MINOR)
- [ ] 2.1 Review the 27 records with `associate`/`associated` against their sources; recode and refresh `last_verified` (10 done; see design.md Result)
- [x] 2.2 Rewrite `includes_status.yaml` definitions; update `docs/ai-consumers.md` status table
- [x] 2.3 `contract.json` `deprecated[]` gains `enum_value` entries for `associate` and `associated_observer`
- [x] 2.4 `DEPRECATED_INCLUDE_STATUS` warning rule; tests

## 3. Removal (MAJOR, batched)
- [ ] 3.1 Remove `associate` and `associated_observer` from the schema enum, `includes_status.yaml` and contract enums
- [ ] 3.2 Migration notes in CHANGELOG and `docs/data-contract.md`
