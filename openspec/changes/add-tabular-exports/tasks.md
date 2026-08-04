## 1. CSV exports
- [x] 1.1 Implement flattened `countries.csv` and `intblocks.csv` writers in `internacia_builder/build.py`
- [x] 1.2 Define flattening rules for struct fields (`population.value`, `area.value`, etc.) and document in `docs/ai-consumers.md`
- [x] 1.3 Add manifests/sidecars for new CSV artifacts

## 2. Lite exports
- [x] 2.1 Define lite column sets for countries (~10 fields) and intblocks (~8 fields)
- [x] 2.2 Emit `countries-lite.parquet`, `countries-lite.csv`, `intblocks-lite.parquet`, `intblocks-lite.csv`
- [x] 2.3 Document token savings and use cases in `llms.txt` and `docs/ai-consumers.md`

## 3. Plain JSON and optional Excel
- [x] 3.1 Emit `countries.json` and `intblocks.json` as JSON arrays
- [x] 3.2 (Optional) Emit Excel workbooks for lite tables if dependency cost is acceptable

## 4. Frictionless datapackage
- [x] 4.1 Generate `data/datasets/datapackage.json` listing resources, paths, formats, and licenses
- [x] 4.2 Link datapackage from README

## 5. Verification
- [x] 5.1 Extend `check_generated_artifacts.py` for new formats
- [x] 5.2 Add tests for CSV/lite row counts matching Parquet primary keys
- [x] 5.3 Full build + `pytest tests/` green
