# Getting started

Internacia is reference data for **countries** (256 records) and **international
organizations / groups** (“intblocks”, 1037 records; **78** blocktypes). Data is licensed
[CC-BY-4.0](../ATTRIBUTION.md); code is MIT.

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

Prefer DuckDB/Parquet over parsing YAML under `data/countries/` or `data/intblocks/`.

## Citation

```
Internacia Datasets (Dateno / CommonData). CC-BY-4.0.
https://github.com/datenoio/internacia-db
```

Version: read `data/datasets/countries.manifest.json` or
`SELECT dataset, version, schema_hash FROM _meta;` in DuckDB.

## Next steps

| Goal | Doc |
|------|-----|
| Join keys & gotchas | [ai-consumers.md](ai-consumers.md) |
| Verified SQL recipes | [query-examples.md](query-examples.md) |
| Edit YAML | [CONTRIBUTING.md](../CONTRIBUTING.md), [agents/contribute.md](agents/contribute.md) |
| Field reference | [data-dictionary.md](data-dictionary.md) |
| Country / entity policy | [country-code-policy.md](country-code-policy.md), [entity-classification-policy.md](entity-classification-policy.md) |
| Intblock inclusion | [intblock-inclusion-policy.md](intblock-inclusion-policy.md) |
