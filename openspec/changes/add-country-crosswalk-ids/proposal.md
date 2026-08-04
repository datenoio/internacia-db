# Change: Add country crosswalk identifier fields

## Why
The deep review identified thin crosswalk coverage: no GeoNames, IOC, FIFA, or FIPS codes on country records. These identifiers are reference data (not socioeconomic profiles) and materially improve joins with sports, geospatial, and legacy US-government datasets.

## What Changes
- Add optional schema fields: `geonames_id`, `ioc_code`, `fifa_code`, `fips_code` to `data/schemas/countries.schema.json`.
- Backfill from authoritative sources via enrichment script or batch update.
- Document fields in `docs/ai-consumers.md` and data dictionary.
- Optional follow-up in same or sibling change: `bbox: {west, east, north, south}` from Wikidata/Natural Earth.

## Impact
- Affected specs: countries-profile, countries-data-quality
- Affected code: `data/schemas/countries.schema.json`, `data/countries/*.yaml`, enrichment scripts, docs
