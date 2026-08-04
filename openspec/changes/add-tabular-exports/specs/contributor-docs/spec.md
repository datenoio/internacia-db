## ADDED Requirements

### Requirement: Tabular export documentation

README and `docs/ai-consumers.md` SHALL document CSV, lite, JSON array, and datapackage export paths with guidance on which format to choose by user type (spreadsheet, LLM lite, programmatic full).

#### Scenario: Non-programmer finds CSV path

- **WHEN** a reader opens `docs/getting-started.md` or README format table
- **THEN** they find instructions to download and open `countries.csv` without DuckDB or Parquet tooling
