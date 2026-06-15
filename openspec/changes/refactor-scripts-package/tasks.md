## 1. Package structure

- [x] 1.1 Add `pyproject.toml` with package name and entry points
- [x] 1.2 Create package layout: `internacia_builder/validate/countries.py`, `internacia_builder/validate/intblocks.py`, `internacia_builder/cli.py`
- [x] 1.3 Move shared utilities (paths, HTTP client, clean_data) into package modules

## 2. Migration

- [x] 2.1 Replace subprocess validation in builder with direct imports
- [x] 2.2 Add thin `scripts/*.py` shims delegating to package CLIs (backward compatibility)
- [x] 2.3 Update CI and README to prefer package entry points

## 3. HTTP consolidation

- [x] 3.1 Shared HTTP helper with retry/backoff and 0.1s rate limit default
- [ ] 3.2 Migrate `enrich_countries.py` from urllib to shared client

## 4. Tests and validation

- [x] 4.1 Update pytest imports to use package modules
- [x] 4.2 Run `openspec validate refactor-scripts-package --strict`
