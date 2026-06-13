## 1. Policy and source

- [x] 1.1 Document the identifier stability policy (README "Versioning and identifier stability")
- [x] 1.2 Create `data/intblocks_aliases.yaml` source seeded from v1.3.0 acronym disambiguations (`ASF`→`FSA`, `CAF`→`CAFBANK`). Note: the 8 v1.3.0 duplicate merges kept the same id, so they need no alias.

## 2. Build artifact

- [x] 2.1 Update `scripts/builder.py` to read the alias source and export `data/datasets/intblocks_aliases.json` and `.parquet`
- [x] 2.2 Add the alias artifact to the release assets in `.github/workflows/release.yml`

## 3. Validation

- [x] 3.1 In `scripts/validate_intblocks.py`, assert every alias `target` resolves to an existing intblock id
- [x] 3.2 Assert alias/current-id collisions are allowed only when `reason: disambiguated`
- [x] 3.3 Add tests for alias export and validation

## 4. Documentation

- [x] 4.1 README: document the alias artifact and how consumers remap retired ids
- [x] 4.2 CHANGELOG entry under Added
- [x] 4.3 Run `openspec validate add-id-stability-aliases --strict`
