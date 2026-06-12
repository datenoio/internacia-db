## 1. Package structure

- [ ] 1.1 Add `pyproject.toml` with package name and entry points
- [ ] 1.2 Create package layout: `internacia/builder.py`, `internacia/validate/countries.py`, `internacia/validate/intblocks.py`, `internacia/enrich/countries.py`, `internacia/cli.py`
- [ ] 1.3 Move shared utilities (paths, HTTP client, clean_data) into package modules

## 2. Migration

- [ ] 2.1 Replace subprocess validation in builder with direct imports
- [ ] 2.2 Add thin `scripts/*.py` shims delegating to package CLIs (backward compatibility)
- [ ] 2.3 Update CI and README to prefer package entry points

## 3. HTTP consolidation

- [ ] 3.1 Shared HTTP helper with retry/backoff and 0.1s rate limit default
- [ ] 3.2 Migrate `enrich_countries.py` from urllib to shared client

## 4. Tests and validation

- [ ] 4.1 Update pytest imports to use package modules
- [ ] 4.2 Run `openspec validate refactor-scripts-package --strict`
