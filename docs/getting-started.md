# Getting started

Internacia is reference data for **countries** (256 records) and **international
organizations / groups** (“intblocks”, 1700+ records; **83** blocktypes). It is part of
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

See also the Frictionless index `datapackage.json`, which the build writes next to the
exports and every [GitHub Release](https://github.com/datenoio/internacia-db/releases/latest) ships.

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

# Trade agreements in force for Chile (trade agreements registry)
con.execute("""
    SELECT agreement_id, agreement_type, via
    FROM country_trade_agreements
    WHERE country_code = 'CL' AND agreement_status = 'in_force'
""").fetchall()
```

Trade and investment agreements are not intblocks: they are in `trade_agreements`,
`trade_agreement_parties` and `trade_agreement_instruments` (also as Parquet and JSONL).
See the [AI consumer guide](ai-consumers.md#trade-agreements-registry).

## Lookups (internacia-python SDK)

`internacia` 0.5.0 (the current PyPI release) reads data contracts 3.x and 4.x, not the
current 5.x: without `db_path` it downloads the newest 4.x release, and it refuses a 5.x
database with `ContractError`. SDK 0.6.0 with contract 5 support is not yet on PyPI. See
[SDK status](llm-scenarios.md#sdk-status) for the SQL equivalents. With `internacia.duckdb`
downloaded from a [GitHub Release](https://github.com/datenoio/internacia-db/releases/latest)
and the contract check turned off, basic lookups work:

```bash
pip install internacia
```

```python
from pathlib import Path
from internacia import InternaciaClient

client = InternaciaClient(db_path=Path("internacia.duckdb"), check_contract=False)

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
| Trade agreements registry | [ai-consumers.md](ai-consumers.md#trade-agreements-registry), [data-contract.md](data-contract.md#canonical-views-and-reference-tables) |
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
