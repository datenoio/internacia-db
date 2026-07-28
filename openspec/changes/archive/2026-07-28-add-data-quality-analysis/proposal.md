# Change: Add data quality analysis command

## Why

There is no consolidated command in this repository that aggregates and reports all data quality metrics and issues across both the countries and international blocks datasets in a structured way (with reports grouped by country, priority, and rule), unlike the `dataportals-registry` repository. Adding this capability will make it much easier to audit, triage, and fix data inconsistencies.

## What Changes

- Add `analyze-quality` command to `scripts/builder.py`.
- Implement checker functions for countries and intblocks.
- Generate text and JSONL reports grouped under `dataquality/` by country, priority, and rule.
- Allow configuring the output directory with `--output` / `-o`.

## Impact

- Affected specs: `data-quality-analysis` (new spec)
- Affected code: `scripts/builder.py`
