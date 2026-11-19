# Data contract

Every build writes `contract.json` next to the other artifacts, and every GitHub Release
attaches it. It is the machine-readable statement of what a release contains and which
changes the [versioning policy](versioning-policy.md) treats as breaking. The SDK and the
API check it; other consumers (DuckDB, R, Polars) can read it directly.

`contract.json` is generated from `internacia_builder/schemas.py` (columns and types) and
`data/schemas/*.schema.json` (enum values). CI fails if the committed file differs from the
generated one.

## Fields

| Field | Meaning |
|-------|---------|
| `contract_version` | `MAJOR.MINOR` of the dataset version. PATCH releases never change the contract. Pin the MAJOR; treat a newer MINOR as compatible. |
| `dataset_version` | The dataset version the file was built for (equals the release tag). |
| `min_duckdb` | Oldest DuckDB version the release is tested with. |
| `duckdb_storage_compatibility_version` | DuckDB storage format used for `internacia.duckdb` (set explicitly by the builder). |
| `enum_policy` | Always `open`: see [Open enums](#open-enums). |
| `type_grammar` | Version of the logical type grammar below. |
| `tables[]` | One entry per table: `name`, `in_duckdb`, `primary_key`, `foreign_keys`, `schema_hash`, `columns[]` (`name`, `type`, `nullable`). |
| `enums[]` | Enum-like columns: `table`, `column` (nested paths use `field[].sub`), `values`, `open`. |
| `deprecated[]` | Columns, resources or enum values scheduled for removal in the next MAJOR release. An enum value entry is `{kind: "enum_value", table, column, value, replacements, removal}`; today `associate` and `associated_observer` on `memberships.status` and `intblocks.includes[].status`, from the `deprecated` markers in `data/schemas/includes_status.yaml`. |

Every entry in `tables[]` is present in `internacia.duckdb`; `kind` is `table` or `view`.
The alias and migration tables are also published as JSON and Parquet files. The `*-lite`
projections and CSV files are derived convenience exports and are not part of the contract.

Foreign keys with known exceptions carry a `note`: `memberships.country_code` can reference
historical codes such as `SU` that are not in `countries`.

```sql
-- Read the contract from DuckDB without Python
SELECT t.name, t.schema_hash
FROM read_json('contract.json') AS c, UNNEST(c.tables) AS u(t);
```

## Canonical views and reference tables

| Name | Kind | Contents |
|------|------|----------|
| `countries`, `intblocks`, `blocktypes`, `memberships` | table | The datasets |
| `_meta` | table | One row per dataset: version, build identity, `schema_hash`, `contract_version` |
| `intblocks_aliases`, `countries_aliases` | table | Retired or renamed IDs (`alias` → `target`, `reason`, `since`) |
| `attribute_intblock_migrations` | table | Retired attribute intblocks → country fields |
| `current_memberships` | view | Membership edges that are current: not `former_member`, no `left` date, and the intblock is neither `historical` nor dissolved. All participation statuses are kept; filter `status` for full members. |
| `country_currencies` | view | `country_code`, `currency_code`, `currency_name`, `currency_symbol` |
| `country_languages` | view | `country_code`, `language_code`, `language_name`, `official` |
| `country_timezones` | view | `country_code`, `timezone` |

Views carry their SQL in `contract.json` (`definition`), so consumers without DuckDB can
reproduce them. Countries with NULL `currencies`, `languages` or `timezones` have no rows in
the corresponding view. `reason = disambiguated` aliases must not be followed blindly: the
old ID now names a different entity.

## Identifier stability

Validation compares the record IDs with the latest release tag: an intblock ID or country
code that existed in that release must still exist or have an entry in
`data/intblocks_aliases.yaml` / `data/countries_aliases.yaml`.

## Logical types

`internacia-logical-types/1`:

| Type | Meaning |
|------|---------|
| `string`, `boolean`, `int32`, `int64`, `float64` | Scalars |
| `list<T>` | List of `T` |
| `struct<a:T,b:U>` | Struct; fields in declared order |
| `map<K,V>` | Map from `K` to `V` |

Example: `countries.native_names` is `map<string,struct<official:string,common:string>>`.

## `schema_hash`

`schema_hash` is the SHA-256 hex digest of the table's columns as a canonical JSON array of
`[name, logical_type, nullable]` in column order, serialized without spaces:

```python
import hashlib, json

columns = [[c["name"], c["type"], c["nullable"]] for c in table["columns"]]
schema_hash = hashlib.sha256(
    json.dumps(columns, separators=(",", ":"), ensure_ascii=False).encode()
).hexdigest()
```

It appears in `contract.json`, every `*.manifest.json` and `*.meta.json`, and DuckDB `_meta`.
It does not depend on the pyarrow or DuckDB version, so it only changes when a column is
added, removed, renamed, retyped, or changes nullability.

## Open enums

Every column listed in `enums[]` is open. Consumers must accept values they do not know
(map them to "other", pass them through, or ignore them), because adding a value is a MINOR
change. Removing or renaming a value is a MAJOR change. Each release's `contract.json` lists
the values that release uses.

## Checksums

- `SHA256SUMS` (`sha256sum` format) covers every other file in the bundle, including
  `migration.vX.Y.Z.json`. Verify a download with `sha256sum -c SHA256SUMS`.
- Each `*.manifest.json` lists `files[]` with `path`, `sha256` and `bytes` for its dataset's
  files, plus `contract_version`.
- `datapackage.json` resources carry `bytes`, `hash` (`sha256:<hex>`) and, for Parquet
  resources, a Frictionless Table Schema.
- DuckDB `_meta` carries `contract_version`. A file cannot contain its own checksum, so the
  checksum of `internacia.duckdb` is in `SHA256SUMS` and `datapackage.json`.

## Checking compatibility

1. Read `contract_version`; refuse a different MAJOR than the one you support.
2. Compare each table's `schema_hash` with the one you tested against. A different hash with
   the same MAJOR means additive changes: read `migration.vX.Y.Z.json` and the CHANGELOG.
3. Verify downloads with `SHA256SUMS`.
4. Remap stored IDs through the alias files before joining.
