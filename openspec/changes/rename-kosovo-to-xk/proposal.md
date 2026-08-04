# Change: Rename Kosovo country code from KV to XK

## Why
The deep review (dev/docs/DEEP_REVIEW_IMPLEMENTATION_PLAN.md) confirmed Kosovo is present as `KV`/`KSV` while virtually every external system (EU, IMF, SWIFT, Unicode CLDR, US State Dept, GeoNames) uses the de facto `XK`/`XKX` codes. Consumers searching for `XK.yaml` conclude Kosovo is missing. Renaming aligns the dataset with the dominant crosswalk standard.

## What Changes
- **BREAKING:** Rename `data/countries/KV.yaml` → `data/countries/XK.yaml`; set `code: XK`, `iso3code: XKX`.
- Add `data/datasets/countries_aliases.json` mapping `KV→XK` and `KSV→XKX` (mirroring `intblocks_aliases.json`).
- Update every intblock `includes[].id: KV` reference to `XK` across `data/intblocks/`.
- Regenerate all dataset artifacts; document migration in `CHANGELOG.md`, `docs/country-code-policy.md`, `llms.txt`, README.
- Update `countries-entity-model` spec requirement from KV to XK.

## Impact
- Affected specs: countries-entity-model, cross-dataset-integrity, dataset-release
- Affected code: `data/countries/XK.yaml`, `data/intblocks/**/*.yaml`, `internacia_builder/build.py`, alias generation, validation cross-rules, docs
