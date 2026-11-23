## 1. Schema and code

- [x] 1.1 Add `unts_registration` to the schema, the Arrow schema and the row builder
- [x] 1.2 Add the `DUPLICATE_UNTS_REGISTRATION` validator issue and tests
- [x] 1.3 Extend the `catalogue` verification description to the UN Treaty Series

## 2. Data

- [x] 2.1 Export the UNTC search for bilateral treaties with subject "Trade", filter titles and read the candidates' detail pages (`scripts/oneoff/parse_untc_details.py`)
- [x] 2.2 Walk the treaty databases of Australia, Canada, the Netherlands and Switzerland
- [x] 2.3 Import with the status policy (`scripts/oneoff/import_trade_relations.py`): official records from national databases, catalogue records for recent UNTS-only agreements, report candidates for the rest

## 3. Documentation and checks

- [x] 3.1 Document the walk in `docs/intblock-sources.md` and the coverage in `docs/ai-consumers.md` and `docs/data-contract.md`
- [x] 3.2 Add a `changelog.d` fragment
- [x] 3.3 Validate, rebuild with the pinned requirements, and run the tests
