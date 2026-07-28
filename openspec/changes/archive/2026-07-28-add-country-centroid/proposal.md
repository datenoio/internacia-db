# Change: Add country centroid coordinates

## Why

The Manus report (`dev/research/report_manus_20260615.md`) identifies country centroid coordinates as a **critical structural gap**: only 3 of 252 records have ad hoc `latitude`/`longitude` fields. A structured `centroid: {lat, lng}` field is required for map rendering, distance calculations, and spatial joins.

## What Changes

- Add `centroid` object (`lat`, `lng` floats) to countries JSON Schema and PyArrow export schema.
- Populate all 252 country/territory records from Natural Earth or World Bank geocoded sources.
- Add validation: required field with warn-then-error completeness gate.
- Document source and provenance per record.
- Remove or migrate ad hoc `latitude`/`longitude` on HK, IL, MO if present.

## Impact

- Affected specs: `countries-profile` (modified)
- Affected code: `data/schemas/countries.schema.json`, `data/countries/*.yaml`, `scripts/builder.py`, completeness config
- Breaking: **BREAKING** for consumers expecting no `centroid` field; additive with schema hash change documented in CHANGELOG
