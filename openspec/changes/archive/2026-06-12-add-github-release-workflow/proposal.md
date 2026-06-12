# Change: Add GitHub release workflow for dataset artifacts

## Why

Generated binaries (`.duckdb`, `.parquet`, `.zst`) are committed to git, inflating repository size without a formal release process. Consumers lack versioned download URLs tied to semver tags.

See [docs/improvement-plan.md](../../../docs/improvement-plan.md) §3.4.

## What Changes

- Add `.github/workflows/release.yml` triggered on `v*` tags.
- Run full `scripts/builder.py build` and attach `data/datasets/*` artifacts to GitHub Release.
- Document hybrid consumption model: YAML sources + manifests in git; large binaries via Releases.
- Optionally gate release on validation + link check (coordinate with `add-scheduled-link-validation`).
- Update README with release download instructions.

## Impact

- Affected specs: `dataset-release` (modified)
- Affected code: `.github/workflows/release.yml`, `README.md`, `CHANGELOG.md`
- Breaking: None (additive; git-tracked artifacts may remain during transition)
