# Maintainer release distribution

Tagged releases (`v*`) rebuild datasets and attach GitHub Release assets
(`.github/workflows/release.yml`). Optional mirrors:

| Channel | Secret / var | Behavior |
|---------|--------------|----------|
| Hugging Face Datasets | `HF_TOKEN`; optional `vars.HF_DATASET_REPO` (default `datenoio/internacia`) | Upload Parquet + manifests when token is set |
| Zenodo | `ZENODO_TOKEN`; optional `ZENODO_CONCEPT_DOI` (default `10.5281/zenodo.21452328`) | Logs deposit candidates; complete versioning under the concept DOI |
| Schema migration | (always) | Writes `data/datasets/migration.vX.Y.Z.json` comparing `data/datasets/schema_baseline/` to current schemas |

Without HF/Zenodo secrets, those steps no-op. GitHub Release assets still publish.
