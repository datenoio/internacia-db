# Change: Align intblock directories with blocktype taxonomy

## Why

The Manus report (`dev/research/report_manus_20260615.md`) documents structural misalignment between `data/intblocks/<category>/` directories and blocktype values: 4 directories with no matching blocktype, 27 blocktypes without directories, 169 records (16%) with primary blocktype–directory mismatch, and an orphaned `unregionalblocks` blocktype never used in data.

## What Changes

- Rename misaligned directories: `taxation/` → `tax/`, `transportation/` → `transport/`, `unregionalblocks/` → `unregionalblock/`.
- Resolve `audit/` directory (add `audit` blocktype or merge into `intorg/` per report §3.3).
- Remove orphaned `unregionalblocks` blocktype from blocktypes taxonomy.
- Document and enforce **primary blocktype** rule: first value in `blocktype` list determines expected directory.
- Reclassify or relocate the 169 mismatch records in batches (high-profile examples first: WTO, ASEAN, G-20, CCASG).
- Add validator check (warn → error) for primary blocktype–directory alignment.
- Coordinate with `add-blocktypes-source` for taxonomy file path.

## Impact

- Affected specs: `intblocks-data-quality` (modified), `cross-dataset-integrity` (modified)
- Affected code: `data/intblocks/`, `data/blocktypes/` or `data/datasets/blocktypes.yaml`, `scripts/validate_intblocks.py`
- Breaking: File path changes for intblock YAML; consumers using directory paths need CHANGELOG note
