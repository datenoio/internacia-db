## 1. Schema and code

- [x] 1.1 Add `unctad_iia_id` to the schema, the Arrow schema and the row builder
- [x] 1.2 Add `unctad_iia_id` to the catalogue identifiers checked for duplicates (`DUPLICATE_IDENTIFIER`) and a test
- [x] 1.3 Extend the `catalogue` verification description to the UNCTAD IIA Navigator

## 2. Data

- [x] 2.2 Parse the latest Wayback capture of every IIA Navigator economy page and import the BIT rows (`scripts/oneoff/import_unctad_bits.py`)
- [x] 2.3 Map the U.S. and Canadian BITs to their UNCTAD ids and note date and status differences

## 3. Documentation and checks

- [x] 3.1 Document the walk in `docs/intblock-sources.md` and the coverage in `docs/ai-consumers.md` and `docs/data-contract.md`
- [x] 3.2 Add a `changelog.d` fragment
- [x] 3.3 Validate, rebuild with the pinned requirements, and run the tests
