## 1. Reconcile field set
- [x] 1.1 Inventory intblock keys in source data vs JSON Schema vs Arrow export schema
- [x] 1.2 Declare canonical fields in `intblocks.schema.json`: `legal_status`, `official_documents`, `recognition_status`, `social_media`, `secretariat`
- [x] 1.3 Normalize plural one-offs (`predecessors`/`successors`/`succeeded_by`) into declared singular fields in source and schema
- [x] 1.4 Remove unused declared fields `abbrRU`, `listed`, `translations`
- [x] 1.5 Update `get_intblocks_schema()` and the README schema table to match

## 2. Tighten schema and add parity check
- [x] 2.1 Set top-level `additionalProperties: false` (or documented narrow allowlist) in `intblocks.schema.json`
- [x] 2.2 Add a schema-parity test comparing JSON Schema properties to Arrow export field names with an explicit allowlist
- [x] 2.3 Document the change under `[Unreleased]` in `CHANGELOG.md` as a producer-facing breaking change

## 3. Filename and id integrity
- [x] 3.1 Add filename-matches-id validation (case-sensitive) to `internacia_builder/validate/intblocks.py`
- [x] 3.2 Rename `data/intblocks/political/UFM.yaml` to `UfM.yaml` via two-step `git mv`
- [x] 3.3 Add a test asserting a filename/id mismatch fails validation

## 4. Blocktype directory alignment
- [x] 4.1 Add `space` to the `blocktype` list of the 22 `space/` records missing it
- [x] 4.2 Escalate the category-directory-vs-primary-blocktype check from warn to error
- [x] 4.3 Run `validate_intblocks.py` to confirm 0 warnings and 0 errors

## 5. Rebuild and validate
- [x] 5.1 Rebuild datasets and confirm the artifact-consistency checker passes
- [x] 5.2 Run `pytest tests/` and `openspec validate align-intblocks-schema-contract --strict`
