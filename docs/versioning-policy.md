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

Enum-like fields (`status`, `scope_category`, `geographic_scope`, …) are **open**:
consumers must accept values they do not know, so a new value is MINOR. Removing or
renaming a value, or narrowing an enum, is MAJOR. A field or resource is first marked
`deprecated` in `contract.json` in a MINOR release and removed no earlier than the next
MAJOR; MAJOR changes are batched, at most once or twice a year. The machine-readable
form of these rules is [`contract.json`](data-contract.md).

`schema_hash` (manifests, sidecars, `_meta`, `contract.json`) is the SHA-256 of the
canonical column list of a table — name, logical type and nullability, in column order
— and does not depend on the pyarrow or DuckDB version; see
[data-contract.md](data-contract.md#schema_hash). Changing an exported field or nested
type changes the hash; changing YAML values or source-only JSON Schema constraints does
not. Read the migration report for
source and export contract changes, including constraints not represented by the
hash. An unchanged hash alone does not establish source-schema compatibility.

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
| `contract.json` | Tables, columns, types, keys, open enums, `contract_version`, `min_duckdb` |
| `SHA256SUMS` | Checksums of every release asset |
| `data/datasets/*.manifest.json` | `version`, `contract_version`, `schema_hash`, `row_count`, `git_commit`, per-file `sha256`/`bytes` |
| `migration.vX.Y.Z.json` (Release asset) | Recursive source JSON Schema and exported Arrow differences against the identified previous release, and (`data`) record ids added, removed and changed and membership edges added, removed and changed; generated on every release |
| Alias JSON / Parquet | Id remaps across releases |
| GitHub Release assets | Frozen Parquet/JSONL/DuckDB/CSV for that tag |

The record-level diff is the `data` section of `migration.vX.Y.Z.json`; the
CHANGELOG entry of each release summarizes it. Combine it with the alias maps to
follow renamed or merged ids.

Migration reports include nested fields, array items, required fields, enums,
and other constraints. `baseline.status` is `available`, `partial`, or
`unavailable`; a missing baseline yields `schema_changed: null`, not a claim of
compatibility. Review `baseline.missing_contracts` for partial comparisons.

## Discoverability

- **Zenodo** concept DOI [10.5281/zenodo.20706176](https://doi.org/10.5281/zenodo.20706176)
  always resolves to the latest deposited version. Cite it plus the manifest
  `version`.
- **Frictionless** resource index: `data/datasets/datapackage.json`.
- **Hugging Face Datasets** (`datenoio/internacia`) is an optional mirror, published
  only when `HF_TOKEN` is configured — see [release-distribution.md](release-distribution.md).
- **Croissant JSON-LD** is not published; use `datapackage.json`.

## Access posture (API)

[internacia-api](https://github.com/datenoio/internacia-api) is **experimental**
and self-host only: it is in development and has no installable release yet.
There is no hosted public Internacia HTTP endpoint and no MCP server in this
repository. Prefer:

1. `internacia.duckdb` from the GitHub Release assets (or a local build). The
   Release assets on tag `vX.Y.Z` are the **bundle of record** for that version;
   the repository commits only a few text descriptors (such as `contract.json`),
   so query a Release asset or a local `python scripts/builder.py build`
2. [internacia-python](https://github.com/datenoio/internacia-python) — `internacia`
   0.2.x on PyPI predates data v3 and cannot download current releases; see
   [SDK status](llm-scenarios.md#sdk-status)
3. Self-host internacia-api only for experiments until it has a release

## Git tags

PATCH and MINOR releases come from the [release train](release-train.md): a
monthly pull request that bumps the version and is tagged `vX.Y.Z` when merged.
`.github/workflows/release.yml` rebuilds exports and attaches them as Release
assets. The manifest `version` on a tagged build MUST match the git tag without
the `v` prefix.

For a release by hand (MAJOR), run `python scripts/prepare_release.py --apply`
or update the dated release entry in `CHANGELOG.md`, the version in
`pyproject.toml`, `internacia_builder/__init__.py`, `uv.lock` and `CITATION.cff`
(`version`, `date-released`) yourself, merge the `changelog.d/` fragments into that
entry and delete them, rebuild, commit the tracked descriptors and tag.
The release gate checks these versions against the tag and manifests.
