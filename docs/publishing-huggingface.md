# Publishing Internacia datasets on Hugging Face

Guide for maintainers: how the `datenoio/internacia` dataset repo on
Hugging Face is created, populated, and kept in sync with GitHub releases.

Target repo: [datenoio/internacia](https://huggingface.co/datasets/datenoio/internacia)
(override via the `HF_DATASET_REPO` variable — see below).

## What gets published

The release workflow prepares a validated Parquet mirror from its final
`.release-datasets/` build. The manual path uses a full local `data/datasets/`
build. Both use `prepare_huggingface_bundle` to produce:

| Repo path | Why it is uploaded |
|-----------|--------------------|
| `countries/countries.parquet` | 256 country records |
| `intblocks/intblocks.parquet` | 1317 organizations / groups |
| `blocktypes/blocktypes.parquet` | 80 taxonomy keys |
| `memberships/memberships.parquet` | Flattened country↔intblock edges |
| `datapackage.json` | Parquet-only Frictionless index with paths matching the per-table folders |
| `{countries,intblocks,blocktypes,memberships}.manifest.json` | All four tables' version, `schema_hash`, and build identity |
| `{countries,intblocks,blocktypes,memberships}.meta.json` | All four tables' metadata sidecars |
| `README.md` | Dataset card (YAML front matter: `license: cc-by-4.0`, tags, `size_categories`) |

**Layout matters: one folder per table.** Each parquet file is uploaded
into a folder named after its table because Hugging Face derives one
*config* per folder. Uploaded flat at the repo root, all four tables are
treated as a single `default`/`train` split; the datasets viewer then
tries to merge incompatible schemas and fails with a `CastError`
("column names don't match"), and `load_dataset("datenoio/internacia")`
breaks the same way. With the folder layout, users get working configs:

```python
from datasets import load_dataset
countries = load_dataset("datenoio/internacia", "countries")
```

Not uploaded: source YAML, compressed `.zst` variants, `internacia.duckdb`,
and migration diffs. GitHub Release assets remain the
full-fidelity channel; Hugging Face is the convenient query/loading channel.

Note: the HF Data Studio viewer renders nested cells (structs, lists,
maps — e.g. `capital_city`, `region`, `languages`) as JSON text in the
grid. That is display-only; the underlying parquet columns are natively
typed, and the viewer's *Features* panel shows the real struct/list types.

## Prerequisites (one-time setup)

1. **Hugging Face account + organization.** Create the `datenoio`
   organization (or use a personal account) at [https://huggingface.co](https://huggingface.co).
2. **Access token.** Settings → Access Tokens → *New token* with **write**
   scope, restricted to the datasets repos you will publish to.
3. **GitHub repo configuration** (for the automated path):
   - Secret `HF_TOKEN` — the token from step 2
     (`Settings → Secrets and variables → Actions → Secrets`).
   - Variable `HF_DATASET_REPO` (optional) — e.g. `datenoio/internacia`;
     defaults to `datenoio/internacia` when unset.

No local Python setup is required for the automated path; CI installs the pinned
`huggingface_hub` from `requirements-publish.txt` itself.

## Automated publishing (recommended)

Every tagged release (`v*`) runs `.github/workflows/release.yml`, which:

1. Runs lint and checks committed artifact freshness before rebuilding all formats
   into `.release-datasets`.
2. Tests that final build, checks artifact content and descriptor paths, enforces
   the quality gate and tag-version consistency, and emits the migration report.
3. Creates the GitHub Release, then, if `HF_TOKEN` is set, runs
   `scripts/push_huggingface.py`. It creates the HF dataset repo if missing and pushes the
   files listed above in **one commit** — parquet files into their per-table folders, card
   and manifests at the root — deleting any legacy flat `*.parquet` files at the repo root
   in the same commit, and tags that commit with the release tag. If the token is absent,
   the step logs `HF_TOKEN not set; skipping Hugging Face upload` and exits 0 — the rest of
   the release is unaffected. The step runs in the `publish` job, which installs only
   `requirements-publish.txt` and checks every file against the `build` job's digest first.

Before tagging, align the dated release entry in `CHANGELOG.md`, `pyproject.toml`,
and `internacia_builder/__init__.py` with the intended version. Run a full build,
commit the source and generated artifacts, and verify the bundle version. For
example, after preparing version `2.2.0`:

```bash
git tag v2.2.0
git push origin v2.2.0
```

Then watch the *Release datasets* workflow run; the step is named
**Push to Hugging Face (optional)**.

The commit replaces files on the `main` revision of the HF repo, so the HF `main`
always mirrors the latest tagged release, and never a mix of two. Each release is also an
HF tag, so it stays reachable after the next one: `load_dataset("datenoio/internacia",
revision="vX.Y.Z")`. Releases before this workflow change have no HF tag; use the commit
history for them.

## Manual publishing (one-off / recovery)

Use this to bootstrap the repo, re-push after a failed CI step, or publish
from a local build:

```bash
pip install -r requirements-publish.txt
export HF_TOKEN=hf_...  # use a write token for the target dataset repo

python scripts/builder.py build
python scripts/check_generated_artifacts.py
python scripts/check_release_bundle.py data/datasets

# Prepare and validate the same descriptor, Parquet files, and metadata as CI.
rm -rf .hf-release
python -c "from pathlib import Path; from internacia_builder.distribution import prepare_huggingface_bundle; prepare_huggingface_bundle(Path('data/datasets'), Path('.hf-release'))"
python scripts/push_huggingface.py .hf-release --message "Release vX.Y.Z" --tag vX.Y.Z
```

Run this from the repository root with the development dependencies installed
and `HF_TOKEN` set. `--repo` (or `HF_DATASET_REPO`) selects another dataset repository;
omit `--tag` for a push that is not a release.

## Dataset card

`data/datasets/README.md` doubles as the HF dataset card. Its YAML front
matter controls HF metadata:

- `license: cc-by-4.0` — must stay in sync with `ATTRIBUTION.md`.
- `tags` — improve discoverability (`countries`, `geography`,
  `tabular-data`, …).
- `size_categories: 1K<n<10K` — the current generated card metadata. Read each
  table's manifest for its row count; membership edges are a separate, larger table.

When adding a new published table, update the builder's card/config generation,
`prepare_huggingface_bundle`, and the workflow/manual cleanup lists. Give the
table its own folder so it becomes its own HF config.

## Verifying a publish

1. Open the repo page and confirm the *Files and versions* tab shows the
   per-table folders plus the new `*.manifest.json` with the expected
   `version` and `schema_hash`.
2. Confirm the viewer works: open the *Data Studio* tab (or a parquet
   file's preview) — each config should render as its own table with no
   cast error. The API check:

   ```bash
   curl -s "https://datasets-server.huggingface.co/valid?dataset=datenoio/internacia"
   ```

   should list `countries`, `intblocks`, `blocktypes`, and `memberships`
   as valid configs.
3. Cross-check against the local build:

   ```bash
   cat data/datasets/countries.manifest.json
   ```

4. Smoke-test loading:

   ```python
   import pandas as pd
   base = "hf://datasets/datenoio/internacia/"
   countries = pd.read_parquet(base + "countries/countries.parquet")
   print(len(countries))  # 256
   ```

   or with DuckDB:

   ```sql
   SELECT count(*) FROM 'hf://datasets/datenoio/internacia/countries/countries.parquet';
   ```

   (Requires `duckdb >= 0.10` with the `httpfs` extension and `HF_TOKEN` in
   the environment for private repos; public repos read anonymously.)

   or via the `datasets` library:

   ```python
   from datasets import load_dataset
   countries = load_dataset("datenoio/internacia", "countries")
   ```

## Versioning and reproducibility

- HF `main` tracks the latest release; the authoritative version identifier
  is inside each `*.manifest.json` (`version`, `schema_hash`, `git_commit`).
- Consumers needing a pinned version should either read the manifest first
  or use a specific HF revision (`revision="<commit-sha>"` in
  `hf_hub_download` / `pd.read_parquet(..., storage_options=...)`).
- The folder layout means file URLs include the table folder
  (`.../resolve/main/countries/countries.parquet`). Publishing removes legacy flat
  files (`.../resolve/main/countries.parquet`); pin an older revision if you need
  that layout.
- Long-term archival with a DOI goes through Zenodo (concept DOI
  `10.5281/zenodo.20706176`), not Hugging Face — see
  [release-distribution.md](release-distribution.md).
- Follow [versioning-policy.md](versioning-policy.md): schema-breaking
  changes bump the dataset version, and the generated
  `migration.vX.Y.Z.json` documents the diff (kept on GitHub, not uploaded
  to HF).

## Troubleshooting

| Symptom | Likely cause / fix |
|---------|--------------------|
| CI logs `HF_TOKEN not set; skipping` | Secret missing or misnamed — re-check step 3 of prerequisites. This is a no-op, not a failure. |
| `403 Forbidden` on upload | Token lacks write scope or is not authorized for the `datenoio` org. Re-issue the token. |
| `403 ... rights to create a dataset under the namespace "datenoio"` | The `datenoio` organization does not exist on Hugging Face yet (check `https://huggingface.co/api/organizations/datenoio`). Create it at https://huggingface.co/organizations/new, or point `HF_DATASET_REPO` at a namespace the token owner controls. |
| `RepositoryNotFoundError` | Rare with `exist_ok=True`; usually a typo in `HF_DATASET_REPO`. |
| Card renders without license/tags | Front matter broken — validate the YAML header of `data/datasets/README.md`. |
| Files uploaded but stale content | Workflow ran before `builder.py build` finished; re-run the workflow or use the manual path. |
| Data Studio shows a `CastError` / "column names don't match" | Parquet files were uploaded flat at the repo root (legacy layout). Re-run the upload — it moves files into per-table folders and deletes the legacy root copies. |
| Viewer cells look like JSON strings | Display-only rendering of struct/list columns; the parquet columns themselves are natively typed. Check the *Features* panel for real types. |
