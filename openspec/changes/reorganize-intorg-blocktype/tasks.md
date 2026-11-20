## 0. Pre-approval review

- [x] 0.1 Add the research note `dev/research/intorg_review_20261120.md` and the generated review artifact `intorg_mapping.yaml`. Check that the mapping covers each of the 147 `intorg/` records exactly once.
- [x] 0.2 Maintainer decides D3 (`commodity` or `mining`) and open questions 1–2 in `design.md`. Decided at approval (2026-11-20): `commodity`; the records in open questions 1–2 keep `igo` and stay on the reviewed allowlist.
- [x] 0.3 Approve `reorganize-intorg-blocktype` before any source data, schema or validator change.

## 1. Taxonomy contract (MINOR)

- [x] 1.1 Add `governance` and `commodity` to `data/blocktypes/blocktypes.yaml`, with translations (ar, zh, en, fr, ru, es).
- [x] 1.2 Add a one-sentence `description` to every blocktype entry, including the boundary notes in design D7.
- [x] 1.3 Mark `intorg` with `deprecated: {replacements: [], removal: next MAJOR, note: "use scope_category = 'igo' for entity form; use a domain blocktype for the domain"}`.
- [x] 1.4 Extend `internacia_builder/contract.py::_deprecated` to emit `{kind: enum_value, table: intblocks, column: blocktype, value: intorg, ...}` from `blocktypes.yaml`. Export `description` and `deprecated` as new nullable columns of the blocktypes artifacts (additive, MINOR).
- [x] 1.5 Update `docs/intblock-inclusion-policy.md` ("Directory vs blocktype" and a new section on blocktype semantics), `docs/ai-consumers.md`, `docs/agents/contribute.md`, `llms.txt` and `templates/`. Run `python scripts/generate_agent_shims.py`.

## 2. Validator gates

- [x] 2.1 Enforce that the first `blocktype` value equals the folder (`check_intblock_directory_alignment`). Reorder the 26 `space/` records that fail this rule.
- [x] 2.2 Report an error when a deprecated blocktype is the primary blocktype.
- [x] 2.3 Add a ratchet for deprecated blocktypes. The set of records that carry `intorg` must equal the 358 baseline IDs, except IDs that `intblocks_aliases.yaml` marks as merged or retired. Store the baseline ID list next to the manifest from task 4.1.
- [x] 2.4 Report an error when a blocktype entry has no `description`.
- [x] 2.5 Implement the scenario "Non-state legal form is labeled IGO" from `complete-intblock-scope-taxonomy` (`SCOPE_CATEGORY_SEMANTIC_MISMATCH`), with a reviewed exception allowlist for the deferred records.
- [x] 2.6 Remove `intorg` from `ORG_DIRS` and from the blocktype set in `scripts/oneoff/label_scope_category.py`. Update `tests/test_label_scope_category.py`.
- [x] 2.7 Keep the CLI validator and the quality analyzer in parity for the new rules (`share-quality-rule-registry`).

## 3. Record moves (MINOR)

- [x] 3.1 Create folders `fisheries`, `financial`, `development`, `tourism`, `labor`, `disaster`, `governance`, `commodity`.
- [x] 3.2 Move the 147 `intorg/` records with `git mv`, as `moves_from_intorg` lists them. Put the target folder first in `blocktype`. Keep the other domain tags and keep `intorg` as the last value.
- [x] 3.3 Move the 23 records in `moves_from_other_folders` in the same way.
- [x] 3.4 Put moves and content edits in separate commits, so reviewers see a rename-only diff.
- [x] 3.5 Remove the empty `data/intblocks/intorg/` folder.
- [x] 3.6 Check that no `partof`, `includes`, alias or documented-query reference breaks. Record IDs do not change, so no alias is needed.

## 4. `scope_category` corrections

- [x] 4.1 Turn `scope_category_corrections` into an ID-based manifest under `data/schemas/` for the existing dry-run-first backfill script.
- [x] 4.2 For each of the 82 records, check an official source. Apply only confirmed values, each with field-level provenance. Move each unconfirmed record to the deferred list. Result: 76 applied (`data/schemas/scope_category_intorg_review.yaml`; D8TTEN and JDTJUBA became `intergovernmental_body`, not `policy_forum`); SOPAC stays `igo` (1990 treaty with legal personality); CAPAM, CREDAF, EROPA, COMMONWEALTHINSTITUTE and WMA deferred to the allowlist.
- [x] 4.3 Run the dry run, review the JSON report, then apply.
- [x] 4.4 (Maintainer decision 2026-11-20: remove the rosters. Done for 24 records whose members are companies, unions, universities or other organizations, 1,800 membership edges; records with one national member body per country keep their rosters.) For each record that becomes `non_state_organization`, review `includes` against the inclusion policy (for example `BIMCO`, `IATA`, `ISO`). Remove countries that are only locations of member organizations, or set `membership_applicability: not_applicable` and `membership_count_type`.
- [x] 4.5 Record the change in the `scope_category = 'igo'` count in `CHANGELOG.md`.

## 5. MINOR release checks

- [x] 5.1 Update `docs/llm-scenarios.md` section 11 and `docs/query-examples.md` (`PICES` expected output) together with `tests/test_documented_queries.py`.
- [x] 5.2 Replace `intorg` in the test fixtures where it stands for "a valid blocktype" (`test_builder_export`, `test_cross_dataset`, `test_clean_data`, `test_check_artifacts`, `test_quality_rules`, `test_partof_hierarchy`, `test_validate_intblocks`).
- [x] 5.3 Run `python scripts/validate_intblocks.py --json`, `python scripts/validate_countries.py --json`, `pytest tests/`, Ruff and `python scripts/builder.py build`. Check artifact consistency.
- [x] 5.4 Add a CHANGELOG entry with the deprecation notice and the before/after query.
- [x] 5.5 Run `openspec validate reorganize-intorg-blocktype --strict`.

## 6. Removal (MAJOR, v5.0.0)

- [ ] 6.1 After at least one MINOR release with `intorg` deprecated, remove `intorg` from every record and from `blocktypes.yaml`. Remove the deprecation entry and the ratchet.
- [ ] 6.2 Remove `intorg` from `ORG_PARENT_BLOCKTYPES` in `internacia_builder/validate/cross_rules.py`. Prefer a test on the target's `scope_category` (`igo`, `intergovernmental_body`, `policy_forum`, `non_state_organization`) over a blocktype list. Known case: today `intorg` stops `EPPO` `partof: IPPC` from being reported, because `IPPC` is a `treaty_body`. Decide that link before the MAJOR release.
- [ ] 6.3 Add migration SQL to `CHANGELOG.md` and to the migration artifact.
- [ ] 6.4 Rebuild and run the full test and validation suite.
