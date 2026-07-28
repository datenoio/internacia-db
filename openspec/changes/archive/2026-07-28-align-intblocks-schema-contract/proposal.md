# Change: Align the intblocks data contract across schema, export, and docs

## Why
The intblocks JSON Schema, the Arrow export schema, and the README describe three different field sets. `data/schemas/intblocks.schema.json` sets `additionalProperties: true`, so 12 keys used in source data are undeclared (`legal_status` alone appears in 282 records), while 3 declared keys (`abbrRU`, `listed`, `translations`) are never used. Separately, `data/intblocks/political/UFM.yaml` is tracked while its record `id` is `UfM` (invisible on case-insensitive filesystems, and no validator catches filename/id drift), and 22 records under `data/intblocks/space/` do not list `space` in their `blocktype`, producing all current validator warnings.

## What Changes
- Reconcile the canonical intblock field set across `data/schemas/intblocks.schema.json`, `get_intblocks_schema()` in `scripts/builder.py`, and the README schema table.
- Declare the canonical undeclared fields (`legal_status`, `official_documents`, `recognition_status`, `social_media`, `secretariat`), normalize one-off plural variants (`predecessors`, `successors`, `succeeded_by`) into the declared singular fields, and remove unused declared fields (`abbrRU`, `listed`, `translations`).
- Tighten top-level `additionalProperties` from `true` to `false` (or a documented narrow allowlist) after reconciliation. **BREAKING** for producers that rely on silent acceptance of unknown fields.
- Add a schema-parity test comparing JSON Schema properties to Arrow export field names with an explicit allowlist for source-only or export-normalized fields.
- Add filename-matches-id validation (case-sensitive) and rename `UFM.yaml` → `UfM.yaml`.
- Add `space` to the `blocktype` list of the 22 migrated `space/` records and escalate the category-directory-vs-primary-blocktype check from warn to error.

## Impact
- Affected specs: intblocks-data-quality, intblocks-build
- Affected code: `data/schemas/intblocks.schema.json`, `scripts/builder.py`, `internacia_builder/validate/intblocks.py`, `README.md`, `tests/test_validate_intblocks.py`, `data/intblocks/space/*.yaml`, `data/intblocks/political/UFM.yaml`
