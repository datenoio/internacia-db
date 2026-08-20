# Dataset versioning policy

Internacia follows [Semantic Versioning](https://semver.org/) for tagged releases
(`vX.Y.Z`). The same version string is written into every manifest, Parquet
`.meta.json` sidecar, and the DuckDB `_meta` table.

This document defines what those numbers mean **for a reference dataset**, not
for a typical software library.

## What bumps which number

| Bump | When | Examples |
|------|------|----------|
| **MAJOR** (`X`) | Consumers must change queries, join keys, or parsers | Removed or renamed schema fields; identifier remaps (`KV`→`XK`); dropping an export format or a field from Parquet/DuckDB; retiring a class of records (attribute-partition intblocks) |
| **MINOR** (`Y`) | Additive, backward-compatible | New optional fields; new country or intblock records; new enum values; new export artifacts (`memberships.parquet`) |
| **PATCH** (`Z`) | Corrections that keep schema and identifiers stable | Roster fixes, description/provenance refresh, fill-rate improvements, documentation |

Row-count changes alone are **not** MAJOR. A new intblock is MINOR; correcting
NATO’s roster is PATCH.

`schema_hash` in the manifest changes when JSON Schema properties change. A
PATCH that only edits YAML values keeps the same `schema_hash`.

## Identifier stability

- **Country `code` and intblock `id` are the stable join keys.**
- Retired or renamed ids remain in `data/datasets/intblocks_aliases.json` and
  `data/datasets/countries_aliases.json` indefinitely (not dropped in the next
  MAJOR). `reason=disambiguated` means the old string now names a *different*
  entity.
- Attribute-partition retirements map through
  `data/datasets/attribute_intblock_migrations.json`.

## Release artifacts consumers should read

| Artifact | Answers |
|----------|---------|
| [CHANGELOG.md](../CHANGELOG.md) | Human-readable added/fixed/breaking notes and migration SQL |
| `data/datasets/*.manifest.json` | `version`, `schema_hash`, `row_count`, `git_commit` |
| `data/datasets/migration.vX.Y.Z.json` | Field-level JSON Schema add/remove/type-change (when `schema_hash` changes) |
| Alias JSON / Parquet | Id remaps across releases |
| GitHub Release assets | Frozen Parquet/JSONL/DuckDB/CSV for that tag |

There is **no** record-level `diff-vX.Y.Z.json` of added/removed ids yet. Until
that ships, combine CHANGELOG + alias maps + `row_count`. CI compares manifests
to `main` via `scripts/diff_countries_baseline.py` (internal; not a release
asset).

## Discoverability

- **Zenodo** concept DOI [10.5281/zenodo.21452328](https://doi.org/10.5281/zenodo.21452328)
  always resolves to the latest deposited version. Cite it plus the manifest
  `version`.
- **Frictionless** resource index: `data/datasets/datapackage.json`.
- **Hugging Face Datasets** (`datenoio/internacia`) is an optional mirror, published
  only when `HF_TOKEN` is configured — see [release-distribution.md](release-distribution.md).
- **Croissant JSON-LD** is not published; use `datapackage.json`.

## Access posture (API)

[internacia-api](https://github.com/datenoio/internacia-api) is a **self-host
reference implementation**. There is no hosted public Internacia HTTP endpoint
and no MCP server in this repository. Prefer:

1. Local `data/datasets/internacia.duckdb` (or GitHub Release assets)
2. [internacia-python](https://github.com/datenoio/internacia-python) (downloads/caches DuckDB)
3. Self-host internacia-api if you need HTTP in your own infrastructure

## Git tags

Maintainers tag `vX.Y.Z`. `.github/workflows/release.yml` rebuilds exports and
attaches them as Release assets. The manifest `version` on a tagged build MUST
match the git tag without the `v` prefix.
