## 0. Pre-approval review artifacts

The following artifacts exist so reviewers can inspect the exact first cohort and exercise non-mutating behavior. They do not authorize schema or source-data changes, and the apply task remains blocked until approval.

- [x] 0.1 Add reviewed `data/schemas/scope_category_backfill.yaml` with exactly 81 explicit assignments
- [x] 0.2 Add dry-run-first `scripts/backfill_scope_category.py` with conflict blocking and JSON reports
- [x] 0.3 Add unit tests for manifest counts, surgical insertion, dry-run, conflicts, and idempotence
- [x] 0.4 Confirm repository dry run reports 81 pending, 0 conflicts, and 0 applied
- [x] 0.5 Obtain approval for `complete-intblock-scope-taxonomy` before running `--apply` or changing the schema/data

## 1. Taxonomy contract

This section implements the approved model before any record uses a new value. Documentation and schema must land together so downstream users never encounter an undocumented enum.

- [x] 1.1 Add `intergovernmental_body` and `non_state_organization` to `intblocks.schema.json`
- [x] 1.2 Update `docs/intblock-inclusion-policy.md` with positive criteria, exclusions, and boundary examples
- [x] 1.3 Update `docs/ai-consumers.md`, `llms.txt`, query examples, and `CHANGELOG.md`
- [x] 1.4 Add schema and validator tests for both new values and rejection of unknown values
- [x] 1.5 Document the additive-enum compatibility risk for closed-enum consumers

## 2. First cohort: 81 direct assignments

This cohort uses only the existing four categories and can be reviewed independently of the 15 model-gap decisions. The expected category totals and warning reduction are acceptance conditions.

- [x] 2.1 Reconcile the manifest against the approved review CSV and confirm 55/13/7/6 category totals
- [x] 2.2 Run the CLI dry run and review the complete JSON report
- [x] 2.3 Run `scripts/backfill_scope_category.py --apply` only after task 0.5 is approved
- [x] 2.4 Confirm exactly 81 source YAML files changed and no roster, hierarchy, name, or blocktype changed
- [x] 2.5 Run validators and confirm `MISSING_SCOPE_CATEGORY` decreases from 114 to 33
- [x] 2.6 Rebuild all generated datasets and verify artifact consistency

## 3. Source-backed cohort: review 18, apply 14

All 18 records were checked against official sources. Four do not fit the initially proposed categories: ACIL is an NGO, RDR is a standing council, GCCPO is a GCC department, and TAR mixes network coverage with treaty parties. Those four remain missing rather than acquiring misleading values. The other 14 now have field-level provenance; the observed warning target is 33 → 19.

- [x] 3.1 Verify all seven initial IGO candidates; reclassify CACM and TRACECA as treaty bodies; defer ACIL, RDR, and GCCPO
- [x] 3.2 Verify all five initial forum/process candidates; reclassify PETROCARIBE as a treaty body
- [x] 3.3 Verify four reference enumerations: CFACENTRAL, CFAWEST, ECCU, EUCU
- [x] 3.4 Verify ISS as treaty-body framework and defer TAR pending network/treaty roster reconciliation
- [x] 3.5 Add field-level provenance for each of the 14 applied `scope_category` decisions
- [x] 3.6 Confirm `MISSING_SCOPE_CATEGORY` decreases from 33 to 19, not 15

## 4. Remaining cohort: 19 → 4 records

Official-source review resolved 12 dependent public bodies and three non-state organizations (including ACIL, RDR and GCCPO). `scope_category_model_gap.yaml` applied all 15 assignments with field-level provenance. A separate reviewed roster cleanup removed 166 false country membership/territorial/consultative links across seven records, while retaining RDR's four actual country participants under `participant`. The intermediate four gaps (AFDF, CIF, TAR, TELESUR) were resolved in section 4A; the formal error gate is now enabled.

- [x] 4.1 Classify eight FAO subsidiary/advisory bodies under the approved policy
- [x] 4.2 Classify four funds/financing windows: ADF and AF remain dependent bodies, AFDF is an independent `igo` with 29 State Participants, CIF is a two-fund partnership without member states
- [x] 4.3 Classify MSF and CANTO as `non_state_organization` and remove false country membership
- [x] 4.4 Retire TELESUR as an out-of-scope commercial company without alias
- [x] 4.5 Add provenance for every retained model-gap assignment and repair removed-field provenance
- [x] 4.6 Resolve ACIL, RDR, and GCCPO under the expanded taxonomy without mistaking the parent body's members or an NGO's institutional members for country members
- [x] 4.7 Split TAR network (`policy_forum`, no country roster) from `TARAGREEMENT` (22 treaty parties)
- [x] 4.8 Confirm formal `MISSING_SCOPE_CATEGORY` decreases from 19 to 0
- [x] 4.9 Confirm intermediate 19 → 4 warning reduction and no schema/roster validation errors

## 4A. Approved final entity decisions: 4 → 0

- [x] 4A.1 AFDF: classify as `igo`, reconcile 29 dated ADF State Participants against 82 mixed country links, and correct legal prose/field provenance
- [x] 4A.2 CIF: classify the two-fund partnership as `intergovernmental_body`, remove its contributors from country membership, remove unsupported WB hierarchy, and document dated donor facts only as narrative
- [x] 4A.3 TAR: keep the network as a `policy_forum` with no invented country roster, add a separately identified 22-party Agreement from UNTC, and keep the network Q-id only on its own record
- [x] 4A.4 Retire TELESUR as an out-of-scope company: audit references, document the retired ID without an invalid alias, and remove seven false membership edges
- [x] 4A.5 Regenerate all outputs, update consumer-visible documentation and query snapshots, add per-record regression assertions, and verify formal warnings fall from four to zero without new quality errors

## 5. Regression gates

The strict gate is enabled only after the migration reaches zero. Validator and quality analyzer must remain behaviorally identical so local, CI, and generated quality reports cannot disagree.

- [x] 5.1 Promote missing `scope_category` on `status: formal` from warning to error
- [x] 5.2 Add parity tests for CLI validator and quality analyzer
- [x] 5.3 Make the legacy directory heuristic suggestion-only or retire its mutation path
- [x] 5.4 Keep deterministic `wbgroup` semantic rule; verify reviewed boundary exceptions with per-ID tests instead of unsafe directory-wide rules for mixed folders
- [x] 5.5 Run full pytest, Ruff, validators, quality analyzer, artifact consistency, and documented-query tests
- [x] 5.6 Run `openspec validate complete-intblock-scope-taxonomy --strict`

## 6. Follow-up boundary

Formal completeness does not resolve every taxonomy concern. The remaining work should be visible but separated from the acceptance criteria of this change unless reviewers explicitly expand scope.

- [ ] 6.1 Open a follow-up for the 72 still-unlabeled non-formal records (originally 78; six individually approved categories were applied with field-level provenance, but their country-link semantics were not changed)
- [ ] 6.2 Open a follow-up semantic audit for existing `igo` labels, starting with 93 marker-based review candidates
- [ ] 6.3 Decide whether a later change makes `scope_category` mandatory for every intblock record
