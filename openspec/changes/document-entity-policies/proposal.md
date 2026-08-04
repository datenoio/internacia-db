# Change: Document entity classification and CIS2 build-inclusion policies

## Why
The deep review found political classification choices (Taiwan as `dependent_territory`, Palestine vs Western Sahara entity types) are internally consistent but undocumented. CIS2 user-assigned entities (XA, XS, XT, XN) exist as complete YAML records but their presence in build exports is unstated policy debt.

## What Changes
- Add `docs/entity-classification-policy.md` explaining `entity_type`, `independent`, `un_member`, `un_status`, and `recognition_status` interactions for disputed and partially recognized entities.
- Extend `docs/country-code-policy.md` with explicit CIS2 build-inclusion statement (all four codes ship in Parquet/DuckDB/JSONL exports, or documented exclusion).
- Cross-link policies from README and `llms.txt`.

## Impact
- Affected specs: countries-entity-model, contributor-docs
- Affected code: `docs/` only (no schema change unless CIS2 exclusion requires build filter)
