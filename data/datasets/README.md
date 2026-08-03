---
license: cc-by-4.0
pretty_name: Internacia Datasets
tags:
  - countries
  - international-organizations
  - reference-data
  - geography
  - tabular-data
size_categories:
  - 1K<n<10K
---

# Internacia Datasets

Reference data for **countries** (256) and **international organizations / groups**
(“intblocks”, 1037), plus **78** blocktypes. Licensed **CC-BY-4.0**.

Source repository: [datenoio/internacia-db](https://github.com/datenoio/internacia-db)

## Files

| File | Description |
|------|-------------|
| `countries.parquet` | Country reference records |
| `intblocks.parquet` | Organizations / groups |
| `blocktypes.parquet` | Taxonomy keys |
| `memberships.parquet` | Flattened country↔intblock edges |
| `datapackage.json` | Frictionless resource index |
| `*.manifest.json` | Version, schema_hash, build identity |

## Join keys

- Countries: `code` (alpha-2), `iso3code`, `wikidata_id`
- Intblocks: `id`; membership via `memberships.country_code` ↔ `countries.code`
- Borders use **alpha-3** — join on `iso3code`

## Citation

See Zenodo concept DOI [10.5281/zenodo.21452328](https://doi.org/10.5281/zenodo.21452328)
and the repository [`ATTRIBUTION.md`](https://github.com/datenoio/internacia-db/blob/main/ATTRIBUTION.md).
