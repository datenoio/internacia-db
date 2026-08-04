# Change: Add CSV, lite, JSON, and Frictionless tabular exports

## Why
The deep review identified CSV as the single biggest barrier for non-technical users (researchers, educators, policy analysts). Plain JSONL and `memberships.csv` already ship, but there are still no flattened `countries.csv` / `intblocks.csv`, no token-efficient lite variants for LLM agents, no plain all-in-one JSON files, and no Frictionless `datapackage.json` descriptor.

## What Changes
- Add flattened `countries.csv` and `intblocks.csv` (scalar columns; struct fields flattened to `.value` or JSON strings where needed).
- Add `countries-lite.parquet`/`.csv` and `intblocks-lite.parquet`/`.csv` with identifier/name/classification fields only.
- Add plain `countries.json` and `intblocks.json` (single-file arrays) for simple API consumption.
- Optionally add Excel (`.xlsx`) exports of the lite tables.
- Generate Frictionless Data `datapackage.json` describing all dataset resources, schemas, and licenses.
- Extend artifact-consistency guard and README/`llms.txt` format tables.

## Impact
- Affected specs: dataset-release, contributor-docs
- Affected code: `internacia_builder/build.py`, `scripts/check_generated_artifacts.py`, `data/datasets/`, `README.md`, `docs/ai-consumers.md`, `llms.txt`, tests
