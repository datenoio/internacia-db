## 1. Build descriptors out of git
- [x] 1.1 Stop tracking `*.manifest.json` and `datapackage.json` (`.gitignore`, `internacia_builder/snapshot.py`)
- [x] 1.2 `scripts/diff_countries_baseline.py` reads the build directory and the baseline sources and `contract.json`
- [x] 1.3 Tests for the snapshot patterns

## 2. Rounded intblock count
- [x] 2.1 `scripts/check_doc_counts.py` reads the built manifests and checks the rounded intblock count
- [x] 2.2 Update the 10 documentation files and `docs/publishing-huggingface.md`
- [x] 2.3 The dataset card renders the rounded count

## 3. Changelog fragments
- [x] 3.1 `changelog.d/README.md` and a fragment format check
- [x] 3.2 `release.apply_version` merges and deletes fragments; the release train commits `changelog.d/`
- [x] 3.3 Tests

## 4. Guidance
- [x] 4.1 Contributor and agent guides: no descriptor commits, fragments, no running totals
