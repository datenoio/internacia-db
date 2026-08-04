## 1. Workflow extension
- [x] 1.1 After freshness check, run `enrich_countries.py` and `enrich_intblocks.py` when diffs would occur
- [x] 1.2 Open PR with label `enrichment` when changes are non-empty
- [x] 1.3 Upload report artifact regardless of PR outcome

## 2. Safety
- [x] 2.1 Limit workflow to `workflow_dispatch` + schedule; no push to default branch
- [x] 2.2 PR body summarizes provenance fields changed and record counts

## 3. Documentation
- [x] 3.1 Update `docs/enrichment.md` with monthly auto-PR behavior
- [x] 3.2 Note maintainer review expectations in CONTRIBUTING
