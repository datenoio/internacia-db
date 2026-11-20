# Change: Reorganize and retire the `intorg` blocktype

## Why

`intorg` (International Organization) is the broadest blocktype. 358 of 1275 intblocks
carry it: 147 records in `data/intblocks/intorg/` use it as the primary blocktype, and
211 records in other folders use it as a secondary tag. For 72 records it is the only
blocktype.

`intorg` does not work as a blocktype:

- **It describes the form of an entity, not its domain.** Every other blocktype says
  what an entity does (`fisheries`, `standards`, `bank`). `intorg` says what the entity
  is. The `scope_category` field already holds that information: 350 of the 358
  `intorg` records are `igo`.
- **It is an inconsistent IGO marker.** 362 of the 712 `igo` records do not carry it.
  Examples: `political` 50, `energy` 42, `military` 38, `bank` 35, `unagency` 34.
  `list_contains(blocktype, 'intorg')` returns about half of the IGOs, plus records
  that are not IGOs.
- **It hides the domain of 147 records.** Most of these records have a clear domain.
  Six of those domains are already in the taxonomy but have no folder: `fisheries`,
  `financial`, `development`, `tourism`, `labor`, `disaster`. Fisheries bodies are
  split: 17 are in `intorg/` and 17 are in `food/`.
- **It caused wrong `scope_category` values.** The legacy labeller
  `scripts/oneoff/label_scope_category.py` maps `intorg` to `igo`. About 70 `intorg`
  records labelled `igo` have a `legal_status` that contradicts `igo`: NGOs, industry
  associations, union federations, partnerships and trust funds. Task 6.2 of
  `complete-intblock-scope-taxonomy` asks for a follow-up audit of such `igo` labels.
  This change does that audit for the `intorg` subset.

## What Changes

- Define the rule: `blocktype` holds the domain or function only, and `scope_category`
  holds the entity form.
- Add two blocktypes: `governance` (public administration, federalism, elections,
  anti-corruption, transparency) and `commodity` (international commodity bodies and
  study groups). Design decision D3 describes the option without `commodity`.
- Create folders for six existing keys: `fisheries`, `financial`, `development`,
  `tourism`, `labor`, `disaster`.
- Add a required `description` (scope note) to every entry in
  `data/blocktypes/blocktypes.yaml`.
- Move the 147 records out of `data/intblocks/intorg/` to domain folders. Move 23
  records from other folders to the new folders. `intorg_mapping.yaml` lists each
  record and its target.
- Correct `scope_category` for 82 records that carry `intorg`, after an official-source
  check of each record. Defer 21 records that need a policy decision. Implement the
  "Non-state legal form is labeled IGO" scenario that `complete-intblock-scope-taxonomy`
  specified.
- Make the first `blocktype` value match the folder, as the existing requirement
  "Primary blocktype directory alignment" says. Today the validator only checks that
  the folder is somewhere in the list. 26 records in `space/` fail the stricter rule.
- Deprecate `intorg` in a MINOR release. List it under `deprecated` in `contract.json`
  and keep it on the 358 records, so existing queries return the same rows during the
  deprecation window.
- **BREAKING (next MAJOR, v5.0.0):** remove `intorg` from every record and from the
  taxonomy.

## Impact

- **Affected specs:** `intblocks-data-quality`, `intblocks-build`, `dataset-release`.
- **Affected source data:** `data/blocktypes/blocktypes.yaml`; 232 files under
  `data/intblocks/**` in the MINOR phase (moves, blocktype order, `scope_category`,
  provenance), and the 358 `intorg` records in the MAJOR phase.
- **Affected code:** `internacia_builder/contract.py` (deprecated blocktypes),
  `internacia_builder/validate/intblock_rules.py` and `validate/intblocks.py` (directory
  alignment, deprecated blocktype, non-state IGO rule),
  `internacia_builder/validate/cross_rules.py` (`ORG_PARENT_BLOCKTYPES`),
  `scripts/oneoff/label_scope_category.py`.
- **Affected docs:** `docs/intblock-inclusion-policy.md`, `docs/ai-consumers.md`,
  `docs/llm-scenarios.md`, `docs/query-examples.md`, `docs/agents/contribute.md`,
  `llms.txt` and the templates under `templates/`, `CHANGELOG.md`.
- **Affected tests:** `tests/test_documented_queries.py` and the fixtures that use
  `intorg` as a sample value.
- **Consumers:**
  - MINOR (4.x): new blocktype values; folder moves (record IDs do not change, so no
    alias is needed); a smaller set of `scope_category = 'igo'` records. Queries on
    `intorg` keep working.
  - MAJOR (5.0.0): `list_contains(blocktype, 'intorg')` returns no rows. The
    replacement is `scope_category = 'igo'` (712 records, not 358) or a domain
    blocktype.
