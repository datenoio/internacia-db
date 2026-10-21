# Design: Complete intblock scope taxonomy

## Context

Internacia historically exported four `scope_category` values: `igo`, `treaty_body`, `policy_forum`, and `reference_enumeration`. Before backfill, coverage was 1086 of 1278 records overall and 992 of 1106 formal records. After the first 81 assignments and 14 source-backed assignments, 19 formal records lacked a category. A 15-record cohort reduced that backlog to four (AFDF, CIF, TAR, TELESUR); the final entity decisions have now reduced formal missing-category findings to zero. Another 78 non-formal records remain unlabeled but do not trigger the formal error gate.

A record-by-record audit initially divided the formal backlog into 81 direct assignments, 18 official-source checks, and 15 model-gap cases. All 18 source checks were completed: 14 received evidence-backed assignments, while ACIL (NGO, not an IGO), RDR (standing council without independent IGO status), GCCPO (GCC Secretariat department), and TAR (network roster mixed with treaty parties) were deferred. In parallel, 93 existing `igo` records have legal-status text matching broad non-governmental/private/association markers; these are review candidates rather than confirmed errors, but they show why directory inference must not be extended.

## Goals / Non-Goals

The change is designed to finish formal-record classification without weakening the meaning of `igo`. It also makes the first migration cohort reproducible and safe to review before any source data is edited.

The goals are:

- Define precise categories for intergovernmental bodies and non-state organizations.
- Backfill 81 reviewed records without touching membership, names, hierarchy, or blocktypes.
- Make backfill dry-run-first, conflict-safe, idempotent, and machine-reportable.
- Reduce formal `MISSING_SCOPE_CATEGORY` warnings in controlled stages: 114 → 33 → 19 → 4 → 0; the final four require separate entity/roster decisions.
- Add a regression gate only after the migration reaches zero.

The non-goals are:

- Automatically classifying all records from their directory or blocktype.
- Resolving the 18 source-review records without official evidence.
- Reclassifying all 93 existing `igo` review candidates in the first migration PR.
- Requiring `scope_category` for all 78 currently unlabeled non-formal records in this change.
- Changing country reference data or hierarchy in the first 81-record mechanical backfill. The final evidence-backed entity review may remove incorrect `partof` links (hosting and trusteeship are not organizational hierarchy) and invalid `includes`/`membership_count` assertions.

## Decisions

The decisions below preserve current consumer semantics where possible. New values are intentionally specific, and migration automation operates from an explicit reviewed manifest rather than inferred rules.

### Decision 1: Keep `igo` narrow

`igo` continues to mean a standing intergovernmental organization with an independent institutional identity or legal personality. Being state-created, treaty-based, or hosted by an IGO is not sufficient by itself.

This prevents commissions, financing windows, NGOs, federations, and companies from being grouped with entities such as the UN, NATO, OECD, or IOM solely because governments participate in them.

### Decision 2: Add two categories

The enum gains two values with non-overlapping purposes:

| Value | Meaning | Initial examples |
|---|---|---|
| `intergovernmental_body` | Standing intergovernmental organ, commission, fund, programme, office, or joint multilateral fund partnership without independent IGO status | FAO Article VI and dependent Article XIV commissions, CODEX, ADF, AF, RDR, GCCPO, CIF's CTF+SCF architecture; **not** AFDF or teleSUR |
| `non_state_organization` | International NGO, professional or industry association, federation, or other organization not constituted by states as an IGO | MSF, CANTO, ACIL |

No generic `other` value is added. If a record cannot be assigned after evidence review, it remains unresolved or is reconsidered under the inclusion policy rather than hidden in a catch-all category.

### Decision 3: Use an explicit first-cohort manifest

The first cohort is stored in `data/schemas/scope_category_backfill.yaml`. It contains exactly 81 reviewed IDs grouped by the four existing categories: 55 `igo`, 13 `treaty_body`, 7 `policy_forum`, and 6 `reference_enumeration`.

The manifest is intentionally ID-based. It is not a permanent claim that every record in the same directory has the same category, and it cannot assign an unknown enum, duplicate an ID, or silently absorb a newly added record.

### Decision 4: Backfill CLI is non-mutating by default

`scripts/backfill_scope_category.py` performs a dry run unless `--apply` is passed. It validates the complete manifest and repository inventory before writing any file.

The CLI follows these safety rules:

- Existing matching values are treated as idempotent success.
- Existing different values are conflicts and are never overwritten.
- Any conflict blocks the entire apply operation, preventing partial migration.
- Missing IDs, duplicate IDs, unexpected statuses, malformed YAML, and manifest-count mismatches are fatal.
- Edits are surgical text insertions after `status`, not YAML reserialization.
- `--check` exits non-zero while pending assignments remain.
- `--report-json` writes the complete plan or result for review and CI.

The initial 81-record cohort was applied after approval and is now idempotent. A separate `source_review_14` manifest requires one official-source provenance entry per assignment; its apply run changed 14 records. The `model_gap_15` manifest likewise applied 12 `intergovernmental_body` and three `non_state_organization` values with field-level provenance. The six-category schema is in place; the formal error gate has not changed.

### Decision 5: Stage the warning reduction

The first cohort reduced warnings from 114 to 33; 14 source-backed cases reduced them to 19. The new two-value taxonomy and 15 reviewed assignments (including ACIL, RDR and GCCPO from the earlier deferrals) reduced them from 19 to **4**. AFDF, CIF, TAR and TELESUR were then resolved as different entity/roster problems, bringing the formal omission count to **zero** before enabling the error gate.

This ordering keeps each review comprehensible and makes unexpected warning-count changes a failing acceptance condition rather than an unnoticed side effect.

### Decision 6: Tighten validation after migration

While the migration is active, missing category on a formal record remains a warning. Once the formal backlog reaches zero, the same condition becomes an error in both the CLI validator and quality analyzer.

The field remains optional in JSON Schema during this change because non-formal records still have an acknowledged backlog. A later change may require it globally after the remaining 78 records and existing semantic review candidates are resolved.

### Decision 7: Resolve the four entity boundaries before enforcing the gate

AFDF has full juridical personality under Articles 31 and 42 of its constituent agreement. Its `igo` roster contains only the 29 State Participants in the dated ADF voting statement; the Bank itself is a non-country participant. CIF denotes the partnership of two separate funds, CTF and SCF, with their own committees. Treat CIF as a standing `intergovernmental_body` without a third country-member roster; its 15 contributors are not members, and World Bank hosting/trusteeship does not establish `partof: WB`.

The TAR Network is the existing ID's cooperation platform, not the Intergovernmental Agreement's 22-party roster. Interpret `policy_forum` to include a continuing intergovernmental implementation/cooperation platform without independent legal personality. The platform has no verifiable country *membership* roster in this model, so keep the 28-country coverage in prose, remove its `includes`/count and set `membership_applicability: not_applicable`. Add one distinct `treaty_body` for the Agreement with 22 parties from UNTC; do not copy the network's Wikidata ID to the treaty. An optional third reference-set record for network coverage is outside this migration.

TELESUR is a registered Venezuelan commercial company, not an intblock under any of the six entity-kind values. Remove its source record and seven false country memberships after checking references, document retirement without an alias pointing to a non-existent record, and regenerate exports. The remaining formal set must have zero missing categories *before* severity is increased. Stale per-field provenance on removed roster fields must be removed or replaced with provenance of retained notes.

## Risks / Trade-offs

The main risk is not the mechanical insertion of a field but the downstream meaning of the expanded enum. The migration therefore separates schema, data, and validation gates and gives consumers time to accept new values.

| Risk | Mitigation |
|---|---|
| Closed-enum downstream clients reject new values | Document as a schema migration; update SDK/API examples before new values ship |
| `intergovernmental_body` becomes a new catch-all | Define positive criteria; prohibit generic `other`; require evidence for ambiguous cases |
| Existing incorrect `igo` labels remain | Track the 93 marker-based candidates in a follow-up semantic audit |
| Directory heuristics misclassify mixed folders | Use explicit reviewed IDs; keep automatic inference suggestion-only |
| Partial apply leaves an inconsistent cohort | Validate every assignment first; abort all writes on any conflict |
| Surgical text edit damages YAML | Parse before and after insertion; cover formatting and idempotence with tests |
| Warning count changes unexpectedly | Assert observed targets 33, 19 and 4, then require evidence for the final 4 → 0 stage |

## Migration Plan

The migration begins only after the proposal is approved. The prepared script and manifest are review artifacts; they do not authorize source-data mutation by themselves.

The approved sequence is:

1. Add the two enum values, policy definitions, consumer documentation, and compatibility notes.
2. Run the 81-record CLI in dry-run mode and review its JSON report against the manifest.
3. Run `--apply`, validate that exactly 81 files change, rebuild exports, and confirm warnings fall from 114 to 33.
4. Complete official-source review for all 18 records, apply 14 assignments with provenance, and reduce warnings from 33 to 19. Preserve four deferrals explicitly.
5. Apply reviewed taxonomy decisions to 12 dependent bodies and three non-state organizations, including ACIL, RDR, and GCCPO; remove false country-member assertions and reduce warnings from 19 to 4. In this cohort 166 `includes` relationships were removed: 163 from six entities with no country-level roster and three subnational/consultative proxies from RDR, whose four state entries are now `participant` rather than `member`.
6. Apply the four evidence-backed decisions above, check the 29-country AFDF roster against the latest available official statement, add a separate 22-party treaty, and retire teleSUR. Rebuild all formats and require four to zero missing formal categories without false country-member edges.
7. Promote missing formal `scope_category` to an error and add regression tests.
8. Release with enum-migration notes; then start a separate audit of 78 non-formal gaps and existing `igo` review candidates.

Rollback is data-only and deterministic: revert the YAML insertions, regenerate datasets, and restore warning severity. The manifest and dry-run report identify every file in the first cohort.

## Open Questions

These questions require explicit reviewer decisions before the final taxonomy cohort is applied. They do not block review of the first 81 assignments, but they do block completion of the change.

1. Resolved for this change: teleSUR is removed from intblocks. Corporate shareholder relations belong in a separate future dataset, not a fake `scope_category`.
2. Resolved: AFDF retains only 29 State Participants using the latest verified official voting statement. Regional bank members and other donors/beneficiaries are excluded.
3. Should `scope_category` become mandatory for all statuses in a later change, or remain required only for formal records?
4. Should the 93 existing `igo` review candidates be audited inside this change or in a dedicated follow-up after formal completeness reaches 100%?
5. Resolved for this change: CIF remains an umbrella institution without membership rows; if a contributor-country join is later required, create a separate dated reference set with a different ID.
6. Resolved: TAR remains the network/platform without an invented country-member roster, and the Agreement becomes a separate treaty record. A separate 28-country geographic reference set remains a possible future change.
