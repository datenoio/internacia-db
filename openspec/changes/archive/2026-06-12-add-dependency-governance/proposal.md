# Change: Add dependency governance

## Why

`requirements.txt` lists nine packages with no version pins. CI installs latest compatible versions on every run, causing silent reproducibility drift—especially across the pandas/pyarrow/duckdb compatibility matrix.

See [docs/improvement-plan.md](../../../docs/improvement-plan.md) §2.2.

## What Changes

- Pin all runtime dependencies in `requirements.txt` (or migrate to `pyproject.toml` with a lockfile).
- Add `.github/dependabot.yml` for pip and GitHub Actions updates.
- Add pip cache to `.github/workflows/validate.yml`.
- Document tested dependency versions in README or `docs/dependencies.md`.

## Impact

- Affected specs: `dependency-governance` (new), `dev-tooling` (modified)
- Affected code: `requirements.txt`, `.github/`, documentation
- Breaking: None (pin to currently working versions)
