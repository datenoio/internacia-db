## 1. Pin dependencies

- [x] 1.1 Record currently working versions from CI/local environment
- [x] 1.2 Pin all packages in `requirements.txt` with compatible version specifiers
- [x] 1.3 Optionally add `requirements-dev.txt` pins for pytest/ruff (coordinate with other changes)

## 2. Automation

- [x] 2.1 Added `.github/dependabot.yml` for pip and github-actions (monthly, grouped)
- [x] 2.2 Added pip cache to `.github/workflows/validate.yml` via `setup-python` cache option

## 3. Documentation

- [x] 3.1 Documented tested Python version (3.11) in README installation section
- [x] 3.2 Run `openspec validate add-dependency-governance --strict`
