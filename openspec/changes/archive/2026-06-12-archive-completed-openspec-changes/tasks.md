## 1. Pre-archive validation

- [x] 1.1 Confirm all tasks marked `[x]` in each completed change's `tasks.md`
- [x] 1.2 Run `openspec validate add-countries-validation --strict` (and siblings) one final time

## 2. Archive and promote

- [x] 2.1 Run `openspec archive add-countries-validation --yes`
- [x] 2.2 Run `openspec archive fill-countries-core-fields --yes`
- [x] 2.3 Run `openspec archive add-countries-entity-status --yes`
- [x] 2.4 Run `openspec archive add-countries-release-governance --yes`
- [x] 2.5 Verify `openspec/specs/` contains promoted capabilities

## 3. Post-archive

- [x] 3.1 Run `openspec validate --strict`
- [x] 3.2 Update `openspec/project.md` testing strategy to reference canonical specs
- [x] 3.3 Mark this change complete and archive it
