## 1. Country record rename
- [x] 1.1 Rename `data/countries/KV.yaml` → `XK.yaml`; set `code: XK`, `iso3code: XKX`; update `recognition_status.notes`
- [x] 1.2 Add provenance entry documenting the rename and source rationale

## 2. Alias artifact
- [x] 2.1 Create `data/datasets/countries_aliases.json` with `KV→XK`, `KSV→XKX`
- [x] 2.2 Emit alias artifact at build time; add Parquet sidecar if other alias tables have one
- [x] 2.3 Add validation that every `includes[].id` referencing a retired country code resolves via aliases

## 3. Intblock roster updates
- [x] 3.1 Replace `includes[].id: KV` with `XK` in all intblock YAML files (grep-driven)
- [x] 3.2 Run `validate_intblocks.py --json` — zero errors

## 4. Documentation and release
- [x] 4.1 Update `docs/country-code-policy.md`, `CHANGELOG.md` (breaking migration), `llms.txt`, README
- [x] 4.2 Rebuild datasets; run `check_generated_artifacts.py` and `pytest tests/`
