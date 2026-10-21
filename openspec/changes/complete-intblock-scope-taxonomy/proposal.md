# Change: Complete intblock scope taxonomy and reviewed backfill

## Why

The current four-value `scope_category` taxonomy covers independent IGOs, treaties, policy forums, and reference sets, but it does not accurately describe standing intergovernmental organs/funds or non-state international organizations. As a result, 114 formal intblock records still trigger `MISSING_SCOPE_CATEGORY`; assigning `igo` to all of them would silence validation while introducing known semantic errors.

The remaining backlog is not homogeneous. An initial audit identified 81 records that fit the existing taxonomy directly, 18 records requiring source-backed legal-status review, and 15 records exposing a model gap. Official-source review of all 18 found that 14 can be classified safely under the existing values; ACIL, RDR, GCCPO, and TAR must be deferred rather than forced into inaccurate categories. The existing directory-based label heuristic resolves none of the original 114 records and has already produced review candidates among existing `igo` labels, so completion requires explicit assignments and stronger safety controls.

## What Changes

This change keeps the four existing values stable and adds two narrow categories rather than broadening `igo` into a catch-all. It also defines a phased, auditable migration that separates obvious assignments from legal-status decisions and prevents partial or silent overwrites.

The implementation will make the following changes:

- Add `intergovernmental_body` for a standing intergovernmental organ, commission, fund, programme, office, or joint institution that is not an independent IGO.
- Add `non_state_organization` for an international NGO, professional or industry association, federation, or other non-state organization.
- Keep `igo` limited to standing intergovernmental organizations with independent institutional identity or legal personality.
- Backfill the first reviewed cohort of 81 formal records from an explicit ID-based manifest: 55 `igo`, 13 `treaty_body`, 7 `policy_forum`, and 6 `reference_enumeration`.
- Apply evidence-backed classifications to 14 of the 18 reviewed records, defer ACIL/RDR/GCCPO/TAR, and make explicit decisions for the 15 initial model-gap records plus the four deferrals.
- Replace directory-wide mutation with a dry-run-first, conflict-safe, idempotent backfill workflow.
- Promote missing `scope_category` on formal records from warning to error only after the formal backlog reaches zero.

The first 81-record manifest was applied after approval. A separate official-source manifest applied 14 assignments with field-level provenance. The reviewed `model_gap_15` manifest classified 12 dependent intergovernmental bodies and three non-state organizations; seven source rosters were corrected after source review. Four formal missing-category warnings temporarily remained: AFDF, CIF, TAR, and TELESUR. The final entity review resolved them and enabled the formal-record error gate; the current validators and quality analyzer report **zero** issues.

The final four approved decisions retain legally independent AFDF as `igo` with only its 29 documented State Participants; model CIF's two-fund partnership as `intergovernmental_body` with no country-member roster; keep `TAR` as the ESCAP cooperation platform (`policy_forum`) and add a separate 22-party `TARAGREEMENT`; and retire the commercial broadcaster `TELESUR` without aliasing it to an unrelated entity. CIF contributors and the 28 network-coverage countries are not organizational member-state rosters. The rebuilt intblock total is 1278 (one added, one retired), with 59,569 membership rows. Retirement of the public `TELESUR` ID and introduction of the distinct treaty ID are documented as consumer-visible migration steps.

## Impact

The enum expansion is additive in the source schema, but it is potentially breaking for downstream consumers that implement exhaustive four-value enums. The release must therefore include explicit migration notes and updated consumer examples before records use the new values.

The expected repository impact is:

- Affected specs: new `intblock-scope-taxonomy`; existing `intblocks-data-quality`.
- Affected source: `data/schemas/intblocks.schema.json`, `data/intblocks/**/*.yaml`, and the three explicit backfill manifests in `data/schemas/scope_category_*.yaml`.
- Affected code: `scripts/backfill_scope_category.py`, `scripts/label_scope_category.py`, validator and quality-analyzer scope rules.
- Affected documentation: `docs/intblock-inclusion-policy.md`, `docs/ai-consumers.md`, `llms.txt`, query examples, and `CHANGELOG.md`.
- Affected exports: all generated intblock formats after approved backfill; this final cohort removes a commercial broadcaster and adds a distinct treaty, so an unchanged net entity count does not imply unchanged IDs. It also removes false membership edges and requires explicit migration notes for `TELESUR` and the new Agreement ID.
- **Potentially breaking:** closed-enum consumers must accept `intergovernmental_body` and `non_state_organization` before those values ship.
