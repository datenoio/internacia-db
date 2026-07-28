## 1. Taxonomy cleanup (Critical / Medium)

- [x] 1.1 Remove orphaned `unregionalblocks` blocktype from blocktypes taxonomy (never used in records)
- [x] 1.2 Add `audit` blocktype to taxonomy and assign to 8 records in `audit/` (INTOSAI, EUROSAI, ASOSAI, etc.)
- [x] 1.3 Coordinate blocktypes source path with `add-blocktypes-source` if merged first

## 2. Directory renames (Critical)

- [x] 2.1 Rename `data/intblocks/taxation/` → `data/intblocks/tax/`
- [x] 2.2 Rename `data/intblocks/transportation/` → `data/intblocks/transport/`
- [x] 2.3 Rename `data/intblocks/unregionalblocks/` → `data/intblocks/unregionalblock/`
- [x] 2.4 Update any hardcoded directory references in scripts and docs

## 3. Exemplar record fixes (High)

- [x] 3.1 Move or reorder `WTO` (`unagency/` → `trade/`, remove misleading `unagency` blocktype)
- [x] 3.2 Fix `ASEAN` primary blocktype vs `political/` directory
- [x] 3.3 Extend `G-20` blocktypes (`economic`, `forum`) and topics (`economy`, `finance`)
- [x] 3.4 Fix `CCASG` primary blocktype vs `economic/` directory
- [x] 3.5 Fix `CEMAC`/`UEMOA` (`customs/` vs `cuscurr` primary), `KIMBERLEY`, `EMU`, ICSG/ILZSG/INSG mining records

## 4. Batch remediation (High)

- [x] 4.1 Generate mismatch report: primary blocktype vs directory for all 169 records
- [x] 4.2 Remediate mismatches in batches by blocktype group (move file or reorder `blocktype` list)
- [x] 4.3 Document primary blocktype rule in CONTRIBUTING

## 5. Validation

- [x] 5.1 Add `validate_intblocks.py` check: primary blocktype must match parent directory name (warn, then error)
- [x] 5.2 Run full validation and dataset rebuild
- [x] 5.3 Run `openspec validate align-blocktype-directories --strict`
