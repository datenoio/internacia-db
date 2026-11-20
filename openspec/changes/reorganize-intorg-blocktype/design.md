# Design: Reorganize and retire the `intorg` blocktype

## Context

The research note `dev/research/intorg_review_20261120.md` gives the full analysis.
The baseline is v4.0.0 (commit `88a0a27f`):

| Metric | Value |
|--------|-------|
| Records with `intorg` | 358 |
| Records in `data/intblocks/intorg/` | 147 |
| Records with `intorg` as a secondary tag | 211 |
| Records whose only blocktype is `intorg` | 72 |
| `intorg` records with `scope_category: igo` | 350 |
| `igo` records without `intorg` | 362 of 712 |
| Taxonomy keys with no folder | 22 (for example `fisheries` 4 uses, `financial` 11, `ocean` 35) |

`intorg_mapping.yaml` in this change directory is the proposed plan for each record.
A generator script checked these conditions:

- Each of the 147 `intorg/` records has exactly one target folder.
- Each record listed for a move from another folder exists in that folder.
- Each `scope_category` correction targets a record that carries `intorg` and does not
  already have the target value.

## Goals / Non-Goals

Goals:

- Give each of the 147 `intorg/` records a domain folder.
- Make `blocktype` mean domain or function only. Entity form stays in `scope_category`.
- Retire `intorg` without silently breaking consumer queries: deprecate it in a MINOR
  release and remove it in the next MAJOR release.
- Correct `scope_category` values that the `intorg` to `igo` heuristic produced, with
  source-backed provenance.
- Enforce primary-blocktype alignment, which the spec already requires.

Non-goals:

- No change to `includes`, beyond the roster check that the inclusion policy already
  requires for records that become `non_state_organization` (task 4.4).
- No new `scope_category` value. Section "Open questions" describes the gap.
- No reorganization of other broad folders (`political`, `economic`, `forum`). This
  change only uses `political` as the target for multipurpose regional organizations.
- No new records. Gaps that the new folders expose (for example ICO, ICCO, ICAC) go to
  the discovery backlog.
- No change to the 22 taxonomy keys without a folder beyond the six this change
  activates. The unused `unregionalgroup` key is out of scope.

## Decisions

### D1: `blocktype` is the domain; `scope_category` is the form

A blocktype answers "what does the entity do". `scope_category` answers "what kind of
entity is it". A blocktype SHALL NOT encode entity form. `intorg` is the only key that
breaks this rule.

Blocktypes such as `bank`, `fund`, `court` and `agreement` describe a function or an
instrument, and they stay. `unagency`, `wbgroup`, `unregionalblock` and
`parliamentary` describe a family of entities, and they stay too, because each has a
clear membership test.

### D2: Activate existing keys before adding new ones

The policy allows thin categories. Where a key already exists, the change creates its
folder and does not add a synonym. Six keys get folders: `fisheries` (34 records with
the 17 from `food/`), `financial` (14 with `BCBS`), `development` (12), `tourism` (4),
`labor` (4) and `disaster` (3 with `ADPC`).

### D3: Add `governance` and `commodity`

No existing key fits two groups of records:

- `governance`: public administration, federalism, elections, anti-corruption and
  transparency. Records: `CAPAM`, `EROPA`, `FORUMOFFEDERATIONS`, `IDEA`, `IACA`, `RAI`,
  `EITI`, and `CAFRAD` and `RESPA` from `education/`.
- `commodity`: intergovernmental commodity bodies and study groups. Records: `ICSG`,
  `ILZSG`, `INSG`, `OIV`, `CPOPC`, `ITTO`, and `IGC` and `COMMONFUND`. This is the class
  that the Common Fund for Commodities calls International Commodity Bodies.

Alternative to `commodity`: use the existing `mining` key for `ICSG`, `ILZSG`, `INSG`,
`EITI` and `IGF`. Put `OIV` and `CPOPC` in `agriculture`, and `ITTO` in `environment`.
This alternative adds one key fewer. The cost is that one class of body is split across
three folders, and later commodity bodies have no obvious home.
**Recommended: `commodity`.** The maintainer decides at approval (task 0.2).

### D4: Two-phase retirement with a ratchet

Removing a blocktype value that consumers filter on is a MAJOR change under
`docs/versioning-policy.md`. Because of that, the retirement has two phases:

1. **MINOR (4.x).**
   - Records move to domain folders. `intorg` stays as a trailing secondary tag on all
     358 records, so `list_contains(blocktype, 'intorg')` returns the same rows.
   - `blocktypes.yaml` marks `intorg` with
     `deprecated: {replacements: [], removal: next MAJOR, note: ...}`.
     `contract.json` lists it under `deprecated` with `column: blocktype`.
   - The validator rejects `intorg` as a primary blocktype. It also enforces a ratchet:
     the set of records that carry `intorg` must equal the 358 baseline IDs, except IDs
     that the alias file marks as merged or retired. The set may not grow, and it may not
     shrink before the MAJOR release.
2. **MAJOR (5.0.0).**
   - Remove `intorg` from all records, the taxonomy, and the `deprecated` list.
   - Delete the empty folder.
   - Add migration SQL to `CHANGELOG.md`.

The `includes_status.yaml` deprecation markers use the same mechanism:
`internacia_builder/contract.py::_deprecated` reads markers from one file. This change
extends it to read `data/blocktypes/blocktypes.yaml` as well.

### D5: Primary blocktype equals the folder

`intblocks-data-quality` requires the first `blocktype` value to equal the folder.
`intblocks-build` requires only that the folder is in the list, and the validator
implements the weaker rule. This change aligns `intblocks-build` with the stricter
rule. It also reorders the 26 `space/` records that fail the stricter rule, for example
`intorg|space` becomes `space|intorg`.

### D6: Source-backed `scope_category` corrections

`intorg_mapping.yaml` derives the corrections from `legal_status` text. This method
shows where to look, but it is not evidence. The approach of
`complete-intblock-scope-taxonomy` applies here too:

- Each correction needs an official source (statutes, host agreement, registry entry)
  and a field-level provenance entry before it is applied.
- A correction that the source does not confirm stays as it is and moves to
  `scope_category_deferred`.
- The corrections use a dry-run-first, ID-based manifest, with no directory inference.

The corrections are value changes (PATCH under the versioning policy). They ship in
the same MINOR release as the folder moves. The release notes must give the change in
the `scope_category = 'igo'` row count.

### D7: Blocktype scope notes

Most mis-filed records come from keys that overlap. Each taxonomy entry gets a
one-sentence English `description` that says what is included and what is not. The
following overlaps need an explicit boundary:

- `maritime` (shipping, navigation, ports), `ocean` (marine environment and science)
  and `fisheries` (fisheries management).
- `research` (research institutes and programmes) and `scientific` (scientific unions
  and councils).
- `bank`, `fund` and `financial` (regulators, standard setters, anti-money-laundering
  bodies).
- `political` (multipurpose political and regional organizations) and `forum`
  (standing processes).
- `legal` and `court`.

## Risks / Trade-offs

- **Consumers who read `intorg` as "all IGOs".** They already get about half of the
  IGOs. The CHANGELOG and `docs/ai-consumers.md` explain that `scope_category = 'igo'`
  is the correct filter.
- **Wrong reclassification of borderline entities.** Mitigated by the source check in
  D6 and by the deferred list.
- **Many file moves in one PR.** Record IDs do not change, so the requirement
  "Intblock file path stability on category move" needs no aliases. Reviewers see a rename-only diff
  when moves and content edits are in separate commits.
- **The `commodity` key adds one more thin category.** Accepted. It has 8 records at
  once, and the discovery backlog has more candidates.

## Migration Plan

1. Approve the proposal and decide D3 and the open questions.
2. MINOR release with taxonomy, moves, scope corrections, deprecation and validator
   gates.
3. At least one MINOR release passes with `intorg` deprecated.
4. MAJOR release v5.0.0: strip `intorg` and delete the key.

Rollback before the MAJOR release: revert the moves. Record IDs do not change and
`intorg` stays on all records, so no consumer-visible identifier changes.

## Open Questions

1. **Transgovernmental networks and public-private partnerships.** The six
   `scope_category` values have no clear place for:
   - networks of agencies, not states: IOSCO, IAIS, ISSA, INTOSAI and its regional
     bodies, tax-administration associations;
   - hybrid partnerships: GAVI, Global Fund, CEPI, EITI.

   They stay in `scope_category_deferred`. Options:
   - (a) a written rule that maps them to existing values, for example networks with
     legal personality become `igo` and the others become `policy_forum`;
   - (b) a new open-enum value (MINOR) in a separate change.
2. **ICRC and the CGIAR centres.** They have international legal personality but are
   not constituted by states. Decide between `igo` and `non_state_organization`.
3. **D3.** Choose `commodity` or `mining`.
