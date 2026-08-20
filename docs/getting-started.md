# Getting started

Internacia is reference data for **countries** (256 records) and **international
organizations / groups** (“intblocks”, 1037 records; **78** blocktypes). It is part of
the [Dateno](https://dateno.io) open-source project. Data and documentation are licensed
[CC-BY-4.0](../DATA_LICENSE); code is MIT.

## Fastest path (spreadsheet)

1. Decompress [`data/datasets/countries-lite.csv.zst`](../data/datasets/countries-lite.csv.zst)
   (`zstd -d …`) or open [`countries-lite.parquet`](../data/datasets/countries-lite.parquet).
2. Filter `code_status` = `official_iso3166_1` for the 249 current ISO countries.
3. For organizations, use [`intblocks-lite.csv.zst`](../data/datasets/intblocks-lite.csv.zst)
   or join memberships via [`memberships.csv.zst`](../data/datasets/memberships.csv.zst)
   (`intblock_id` ↔ `country_code`). Full flattened tables are `countries.csv.zst` /
   `intblocks.csv.zst`.

See also the Frictionless index: [`datapackage.json`](../data/datasets/datapackage.json).

## Lookups (DuckDB / Python)

```bash
# One-liner membership check
duckdb data/datasets/internacia.duckdb \
  -c "SELECT country_code, status FROM memberships WHERE intblock_id='NATO' ORDER BY 1;"
```

```python
import duckdb
con = duckdb.connect("data/datasets/internacia.duckdb")
con.execute("SELECT code, name FROM countries WHERE code = 'XK'").fetchall()
```

## Lookups (internacia-python SDK)

This is the most convenient path for LLM-generated code: it handles database download/caching,
then exposes small Python methods for the common lookup/join patterns.

```bash
pip install internacia
```

```python
from internacia import InternaciaClient

client = InternaciaClient()

# Country lookup (ISO 3166-1 alpha-2)
country = client.countries.get_by_code("US")
print(country["name"])

# Organizations/blocks containing a country (membership roster)
blocks_for_us = client.intblocks.get_by_member("US")
for b in blocks_for_us[:5]:
    print(b["id"], b["name"])

# Fuzzy search across countries and blocks (multilingual)
results = client.search.fuzzy("United States", limit=5)
for r in results:
    print(r["type"], r["name"])
```

Prefer DuckDB/Parquet over parsing YAML under `data/countries/` or `data/intblocks/`.

## Citation

```
Internacia Datasets (Dateno). CC-BY-4.0.
DOI: https://doi.org/10.5281/zenodo.21452328
https://github.com/datenoio/internacia-db
```

Version: read `data/datasets/countries.manifest.json` or
`SELECT dataset, version, schema_hash FROM _meta;` in DuckDB.

## Next steps

| Goal | Doc |
|------|-----|
| Join keys & gotchas | [ai-consumers.md](ai-consumers.md) |
| Verified SQL recipes | [query-examples.md](query-examples.md) |
| Verified Polars recipes | [query-examples-polars.md](query-examples-polars.md) |
| Verified R / dplyr recipes | [query-examples-r.md](query-examples-r.md) |
| Observable / Plot recipes | [query-examples-observable.md](query-examples-observable.md) |
| Edit YAML | [CONTRIBUTING.md](../CONTRIBUTING.md), [agents/contribute.md](agents/contribute.md) |
| Field reference | [data-dictionary.md](data-dictionary.md) |
| Versioning / API posture | [versioning-policy.md](versioning-policy.md) |
| Country / entity policy | [country-code-policy.md](country-code-policy.md), [entity-classification-policy.md](entity-classification-policy.md) |
| Intblock inclusion | [intblock-inclusion-policy.md](intblock-inclusion-policy.md) |
