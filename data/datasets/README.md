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
configs:
  - config_name: countries
    data_files: countries/countries.parquet
  - config_name: intblocks
    data_files: intblocks/intblocks.parquet
  - config_name: blocktypes
    data_files: blocktypes/blocktypes.parquet
  - config_name: memberships
    data_files: memberships/memberships.parquet
---

# Internacia Datasets

Reference data for **countries** (256) and **international organizations / groups**
(“intblocks”, 1289), plus **82** blocktypes. Licensed **CC-BY-4.0**.

Source repository: [datenoio/internacia-db](https://github.com/datenoio/internacia-db)

## Loading

Each table is a separate config:

```python
from datasets import load_dataset

countries = load_dataset("datenoio/internacia", "countries")
intblocks = load_dataset("datenoio/internacia", "intblocks")
```

or directly from the parquet files:

```python
import pandas as pd
countries = pd.read_parquet("hf://datasets/datenoio/internacia/countries/countries.parquet")
```

Nested fields (`capital_city`, `region`, `incomeLevel`, `languages`,
`borders`, `native_names`, …) are natively typed parquet structs, lists,
and maps. The Data Studio grid renders them as JSON text — that is
display-only; the *Features* panel shows the real types.

## Files

| Path | Description |
|------|-------------|
| `countries/countries.parquet` | Country reference records |
| `intblocks/intblocks.parquet` | Organizations / groups |
| `blocktypes/blocktypes.parquet` | Taxonomy keys |
| `memberships/memberships.parquet` | Flattened country↔intblock edges |
| `datapackage.json` | Frictionless resource index |
| `*.manifest.json` | Version, schema_hash, build identity |

## Join keys

- Countries: `code` (alpha-2), `iso3code`, `wikidata_id`
- Intblocks: `id`; membership via `memberships.country_code` ↔ `countries.code`
- Borders use **alpha-3** — join on `iso3code`

## Citation

See Zenodo concept DOI [10.5281/zenodo.20706176](https://doi.org/10.5281/zenodo.20706176)
and the repository [`ATTRIBUTION.md`](https://github.com/datenoio/internacia-db/blob/main/ATTRIBUTION.md).
