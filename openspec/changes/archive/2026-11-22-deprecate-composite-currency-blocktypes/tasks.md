## 0. Approval

- [x] 0.1 Maintainer approves the review findings and the migration (2026-11-22, in the review session).

## 1. Taxonomy contract (MINOR)

- [x] 1.1 Mark `eccurr` deprecated (`replacements: [economic, currency]`) and `cuscurr` deprecated (`replacements: [customs, currency]`) in `data/blocktypes/blocktypes.yaml`, with `removal: next MAJOR` and a note.
- [x] 1.2 Update the scope notes of `currency`, `customs`, `eccurr` and `cuscurr` (design D3).
- [x] 1.3 Add `eccurr` (`OECS`) and `cuscurr` (`CEMAC`, `UEMOA`) to `data/schemas/deprecated_blocktypes_baseline.yaml`.

## 2. Baseline records (MINOR)

- [x] 2.1 Move `OECS` to `data/intblocks/economic/` with `git mv`; set `blocktype: [economic, political, currency, eccurr]`.
- [x] 2.2 Set `CEMAC` and `UEMOA` to `blocktype: [customs, currency, cuscurr]`.

## 3. Currency and customs gaps (MINOR)

- [x] 3.1 Add `data/intblocks/currency/EUROAREA.yaml` (21 members from the ECB roster, `partof: EU`, `wikidata_id: Q8268`), and add `Q8268` to `references.wikidata_duplicate_allowlist`.
- [x] 3.2 Add Bulgaria (joined 2026-01-01) to `wbgroup/EMU` and update `membership_count` and provenance.
- [x] 3.3 Move `SCHENGENAREA` to `data/intblocks/travel/` with `git mv`; set `blocktype: [travel]`.
- [x] 3.4 Remove `customs` from `UNASUR`.

## 4. Docs and checks

- [x] 4.1 Update `docs/intblock-inclusion-policy.md`, `docs/data-contract.md`, `docs/ai-consumers.md` and `docs/agents/contribute.md`; run `python scripts/generate_agent_shims.py`.
- [x] 4.2 Update `tests/test_include_labels_and_statuses.py` for the new contract entries and any cookbook count the new record changes.
- [x] 4.3 Add a `changelog.d/` fragment with the deprecation notice and the replacement queries.
- [x] 4.4 Run `python scripts/validate_intblocks.py --fail-on-warning`, `python scripts/builder.py build`, `python scripts/check_generated_artifacts.py`, `pytest tests/` and Ruff.
- [x] 4.5 Run `openspec validate deprecate-composite-currency-blocktypes --strict`.

## 5. Removal (MAJOR, v5.0.0)

Moved to `reorganize-intorg-blocktype` tasks 6.1, 6.3 and 6.4 when this change was archived, so the MAJOR release removes `intorg`, `eccurr` and `cuscurr` from one checklist.

- [ ] 5.1 After at least one MINOR release with both values deprecated, remove `eccurr` and `cuscurr` from `OECS`, `CEMAC`, `UEMOA` and from `blocktypes.yaml`, together with `intorg` (`reorganize-intorg-blocktype` task 6.1). Remove their baseline entries.
- [ ] 5.2 Add the migration SQL from design.md to `CHANGELOG.md`.
- [ ] 5.3 Rebuild and run the full test and validation suite.
