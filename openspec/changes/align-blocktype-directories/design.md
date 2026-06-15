## Context

Intblocks are stored under category directories intended to mirror primary blocktype. Organic growth left 16% of records misaligned and 27 blocktypes without dedicated directories.

## Goals / Non-Goals

- Goals: 1:1 directory↔primary blocktype alignment; remove orphan taxonomy entries; validator enforcement.
- Non-Goals: Creating 27 new directories in one PR; changing multi-blocktype semantics beyond primary-directory rule.

## Decisions

- **Primary blocktype**: First element of `blocktype` array is authoritative for directory placement.
- **Directory renames**: Mechanical renames first (`taxation`, `transportation`, `unregionalblocks`).
- **audit/**: Add `audit` blocktype to taxonomy and assign to 8 audit records (INTOSAI, EUROSAI, etc.) rather than merging into `intorg/`.
- **Batch remediation**: Phase A — report-listed exemplars; Phase B — remaining mismatches by blocktype group.
- **27 orphan blocktypes**: Records stay in thematic directories until dedicated dirs are justified; validator only enforces primary match, not directory existence for every blocktype.

## Risks / Trade-offs

- Large file-move PRs → batch by category with validation after each batch.
- Records legitimately multi-typed → reorder `blocktype` list or move file; document in CONTRIBUTING.

## Migration Plan

1. Taxonomy cleanup (remove `unregionalblocks`, add `audit` if chosen).
2. Directory renames with git mv.
3. Fix exemplar mismatches (WTO, ASEAN, G-20, CCASG, CEMAC, KIMBERLEY, EMU).
4. Batch-fix remaining 169 records.
5. Enable validator alignment check.

## Open Questions

- Whether to create top-priority missing directories (`mining/`, `trade/`) in this change or a follow-up.
