## 0. Approval gate

- [x] 0.1 Obtain maintainer approval for `add-artificial-intelligence-blocktype` (the work below was done on 2026-11-21 at the maintainer's direct request, before this proposal; approved on 2026-11-21)
- [ ] 0.2 Resolve the open questions in `design.md`

## 1. Taxonomy

- [x] 1.1 Add `artificial_intelligence` to `data/blocktypes/blocktypes.yaml` with a scope note and an English name
- [x] 1.2 Point AI bodies to the new key in the `digital` scope note

## 2. Records

- [x] 2.1 Add `artificial_intelligence` to `WAICO`, `PAXSILICA`, `CHIP4` and `GPAI`, keeping each primary blocktype and keeping `intorg` last on `WAICO`
- [x] 2.2 Add `NAAIMES`, `HAIPFRIENDS`, `OECDAIPRINCIPLES`, `MILITARYAIDECLARATION` and `COEAICONVENTION` with official-source rosters, `last_verified` and provenance
- [x] 2.3 Add Wikidata exclusions for `NAAIMES` and `HAIPFRIENDS`
- [x] 2.4 Record the deferral of the UN Group of Friends for International Cooperation on AI Capacity-building in `CHANGELOG.md`
- [x] 2.5 Check the `COEAICONVENTION` roster against the Council of Europe Treaty Office chart in a browser (matches the chart as of 2026-11-21)

## 3. Documentation

- [x] 3.1 Update current counts (83 blocktypes, 1303 intblocks) and regenerate agent shims
- [x] 3.2 Update the `human_rights` topic recipe in `docs/query-examples.md` and `tests/test_documented_queries.py`
- [x] 3.3 Add a MINOR entry to `CHANGELOG.md`

## 4. Verification

- [x] 4.1 Rebuild with the pinned requirements and run the committed-snapshot, artifact, doc-count and Markdown-link checks
- [x] 4.2 Run both validators, `ruff` and `pytest tests/`
