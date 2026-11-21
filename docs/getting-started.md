# Getting started

Internacia is reference data for **countries** (256 records) and **international
organizations / groups** (“intblocks”, 1324 records; **83** blocktypes). It is part of
the [Dateno](https://dateno.io) open-source project. Data and documentation are licensed
[CC-BY-4.0](../DATA_LICENSE); code is MIT.

## Fastest path (spreadsheet)

Exports are not committed: download them from the
[latest release](https://github.com/datenoio/internacia-db/releases/latest), or run
`python scripts/builder.py build` in a clone to create them under `data/datasets/`.

1. Decompress [`countries-lite.csv.zst`](https://github.com/datenoio/internacia-db/releases/latest/download/countries-lite.csv.zst)
   (`zstd -d …`) or open [`countries-lite.parquet`](https://github.com/datenoio/internacia-db/releases/latest/download/countries-lite.parquet).
2. Filter `code_status` = `official_iso3166_1` for the 249 current ISO countries.
3. For organizations, use [`intblocks-lite.csv.zst`](https://github.com/datenoio/internacia-db/releases/latest/download/intblocks-lite.csv.zst)
   or join memberships via [`memberships.csv.zst`](https://github.com/datenoio/internacia-db/releases/latest/download/memberships.csv.zst)
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

`internacia` 0.2.x (the current PyPI release) predates data v3: it cannot download
current releases, `search.fuzzy` fails, and `get_by_member` also returns former
memberships. See [SDK status](llm-scenarios.md#sdk-status) for the SQL equivalents;
SDK 0.3.0 with v3 support is in progress. With `internacia.duckdb` downloaded from a
[GitHub Release](https://github.com/datenoio/internacia-db/releases/latest), basic
lookups still work:

```bash
pip install internacia
```

```python
from pathlib import Path
from internacia import InternaciaClient

client = InternaciaClient(db_path=Path("internacia.duckdb"))

# Country lookup (ISO 3166-1 alpha-2)
country = client.countries.get_by_code("US")
print(country["name"])
```

Prefer DuckDB/Parquet over parsing YAML under `data/countries/` or `data/intblocks/`.

## Citation

```
Internacia Datasets (Dateno). CC-BY-4.0.
DOI: https://doi.org/10.5281/zenodo.20706176
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
| R / dplyr recipes | [query-examples-r.md](query-examples-r.md) |
| Observable / Plot recipes | [query-examples-observable.md](query-examples-observable.md) |
| Edit YAML | [CONTRIBUTING.md](../CONTRIBUTING.md), [agents/contribute.md](agents/contribute.md) |
| Find missing intblocks / improve records | [discovery.md](discovery.md), [agents/discover.md](agents/discover.md) |
| Field reference | [data-dictionary.md](data-dictionary.md) |
| Versioning / API posture | [versioning-policy.md](versioning-policy.md) |
| Country / entity policy | [country-code-policy.md](country-code-policy.md), [entity-classification-policy.md](entity-classification-policy.md) |
| Intblock inclusion | [intblock-inclusion-policy.md](intblock-inclusion-policy.md) |
| Intblock sources | [intblock-sources.md](intblock-sources.md) |
