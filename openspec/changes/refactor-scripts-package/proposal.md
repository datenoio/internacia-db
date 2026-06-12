# Change: Refactor scripts into installable package

## Why

Scripts are standalone Typer CLIs with duplicated logic; `builder.py` invokes `validate_countries.py` via subprocess. This hinders testability, shared HTTP clients, and consistent imports. Phase 4 architecture item from the improvement plan.

See [docs/improvement-plan.md](../../../docs/improvement-plan.md) §2.4.

## What Changes

- Introduce installable package (e.g. `internacia/` or `internacia_builder/`) with modules for build, validate, and enrich.
- Replace subprocess validation calls with direct imports in builder.
- Consolidate HTTP client usage (`requests` or `httpx`) with shared retry/rate-limit helper.
- Keep Typer CLI entry points (`internacia-build`, etc.) or thin wrappers in `scripts/` for backward compatibility.
- Add `pyproject.toml` package metadata (coordinate with `add-dev-tooling` and `add-dependency-governance`).

## Impact

- Affected specs: `countries-build`, `intblocks-build`, `dev-tooling` (modified)
- Affected code: new package directory, `scripts/` (deprecated or shim), `pyproject.toml`, tests
- Breaking: Possible CLI path changes unless shims retained
