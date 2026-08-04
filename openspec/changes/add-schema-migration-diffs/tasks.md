## 1. Migration diff generator
- [x] 1.1 Compare current JSON Schema to previous release schema (or stored baseline)
- [x] 1.2 Emit `migration.vX.Y.Z.json` with field-level changes per dataset

## 2. Release integration
- [x] 2.1 Attach migration file to GitHub Release assets when schema_hash changes
- [x] 2.2 Skip or emit empty migration when schema_hash unchanged

## 3. Documentation
- [x] 3.1 Document migration file format in `docs/ai-consumers.md`
- [x] 3.2 Add example consumer snippet (Python SDK / DuckDB column check)

## 4. Tests
- [x] 4.1 Test migration diff generation against a fixture schema pair
