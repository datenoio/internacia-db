# Change: Enrich country World Bank classification gaps

## Why

The Manus report (`dev/research/report_manus_20260615.md`) documents 33 records missing World Bank `region`, `incomeLevel`, and `lendingType` (and 107 missing `adminregion`) because WB does not classify high-income OECD members, overseas territories, and special entities. The schema should document this and source alternative classifications (UN M49, IMF) where applicable. Additionally, 82 countries lack recent `gini` data; older estimates should be backfilled where available.

Coordinate with `add-countries-enrichment-refresh` for gini threshold ratcheting and provenance freshness.

## What Changes

- Document WB classification gaps and expected absences in `docs/country-code-policy.md` or enrichment docs.
- Backfill `region`, `incomeLevel`, `lendingType`, and `adminregion` for the 33 non-WB-classified records from UN M49 or IMF where authoritative mappings exist.
- Backfill `gini` with older published estimates for countries lacking recent data (coordinate gini completeness tightening).
- Add validator documentation for structurally expected nulls vs data gaps.

## Impact

- Affected specs: `countries-profile` (modified)
- Affected code: `data/countries/*.yaml`, `scripts/enrich_countries.py`, docs, completeness config
- Breaking: None
