"""Consumer contract (``contract.json``) and bundle checksums (``SHA256SUMS``).

See docs/data-contract.md for the format and the versioning rules it encodes.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import pyarrow as pa

from internacia_builder.paths import project_root
from internacia_builder.schemas import (
    TYPE_GRAMMAR,
    get_aliases_schema,
    get_attribute_migration_schema,
    get_blocktypes_schema,
    get_border_status_schema,
    get_countries_schema,
    get_country_aliases_schema,
    get_country_borders_schema,
    get_country_currencies_schema,
    get_country_languages_schema,
    get_country_timezones_schema,
    get_country_trade_agreements_schema,
    get_intblocks_schema,
    get_memberships_schema,
    get_meta_schema,
    get_trade_agreement_parties_schema,
    get_trade_agreements_schema,
    schema_columns,
    schema_hash,
)
from internacia_builder.trade_agreements import PARTY_STATUSES, PARTY_TYPES
from internacia_builder.yaml_io import safe_load

CONTRACT_FILE = "contract.json"
CHECKSUMS_FILE = "SHA256SUMS"

# Oldest DuckDB the release is tested with: the builder pin and the SDK's lower bound.
MIN_DUCKDB = "1.5.4"
# Set explicitly so that raising the builder's DuckDB pin cannot silently raise the
# oldest DuckDB able to open internacia.duckdb.
DUCKDB_STORAGE_COMPATIBILITY = "v1.0.0"

# Alias ``reason`` values accepted by the validator (internacia_builder/validate/cross_rules.py).
ALIAS_REASONS = ["renamed", "merged", "disambiguated", "retired", "moved"]
ALIAS_TARGET_DATASETS = ["intblocks", "trade_agreements"]

# name, schema, in internacia.duckdb, primary key, foreign keys, JSON Schema with enum sources
TABLES: list[dict[str, Any]] = [
    {
        "name": "countries",
        "schema": get_countries_schema,
        "in_duckdb": True,
        "primary_key": ["code"],
        "foreign_keys": [],
        "enum_source": "countries.schema.json",
    },
    {
        "name": "intblocks",
        "schema": get_intblocks_schema,
        "in_duckdb": True,
        "primary_key": ["id"],
        "foreign_keys": [
            {"columns": ["blocktype[]"], "references": {"table": "blocktypes", "columns": ["id"]}},
        ],
        "enum_source": "intblocks.schema.json",
    },
    {
        "name": "blocktypes",
        "schema": get_blocktypes_schema,
        "in_duckdb": True,
        "primary_key": ["id"],
        "foreign_keys": [],
    },
    {
        "name": "memberships",
        "schema": get_memberships_schema,
        "in_duckdb": True,
        "primary_key": ["intblock_id", "country_code"],
        "foreign_keys": [
            {"columns": ["intblock_id"], "references": {"table": "intblocks", "columns": ["id"]}},
            {
                "columns": ["country_code"],
                "references": {"table": "countries", "columns": ["code"]},
                "note": "Rows with include_type 'historical-country' may reference codes that are not in countries (e.g. SU).",
            },
        ],
    },
    {
        "name": "_meta",
        "schema": get_meta_schema,
        "in_duckdb": True,
        "primary_key": ["dataset"],
        "foreign_keys": [],
    },
    {
        "name": "intblocks_aliases",
        "schema": get_aliases_schema,
        "in_duckdb": True,
        "primary_key": ["alias"],
        "foreign_keys": [],
    },
    {
        "name": "countries_aliases",
        "schema": get_country_aliases_schema,
        "in_duckdb": True,
        "primary_key": ["alias"],
        "foreign_keys": [],
    },
    {
        "name": "attribute_intblock_migrations",
        "schema": get_attribute_migration_schema,
        "in_duckdb": True,
        "primary_key": ["retired_id"],
        "foreign_keys": [],
    },
    {
        "name": "border_status",
        "schema": get_border_status_schema,
        "in_duckdb": True,
        # One entry per border; a later closure replaces an ended one.
        "primary_key": ["country_a", "country_b"],
        "foreign_keys": [
            {"columns": ["country_a"], "references": {"table": "countries", "columns": ["iso3code"]}},
            {"columns": ["country_b"], "references": {"table": "countries", "columns": ["iso3code"]}},
        ],
        "enum_source": "border_status.schema.json",
        # The source file wraps rows in an `entries` list; enums are read below that prefix.
        "enum_prefix": "entries[].",
    },
    {
        "name": "trade_agreements",
        "schema": get_trade_agreements_schema,
        "in_duckdb": True,
        "primary_key": ["id"],
        "foreign_keys": [
            {"columns": ["intblock_id"], "references": {"table": "intblocks", "columns": ["id"]}},
        ],
        "enum_source": "trade_agreements.schema.json",
    },
    {
        "name": "trade_agreement_parties",
        "schema": get_trade_agreement_parties_schema,
        "in_duckdb": True,
        "primary_key": ["agreement_id", "party_id"],
        "foreign_keys": [
            {"columns": ["agreement_id"], "references": {"table": "trade_agreements", "columns": ["id"]}},
            {
                "columns": ["party_id"],
                "references": {"table": "countries", "columns": ["code"]},
                "note": "Rows with party_type 'intblock' reference intblocks.id instead; 'historical-country' rows may use codes not in countries.",
            },
        ],
    },
]

# Canonical views inside internacia.duckdb. Their semantics are part of the contract, so
# DuckDB, R and Polars users get the same answers as the SDK.
VIEWS: list[dict[str, Any]] = [
    {
        "name": "current_memberships",
        "schema": get_memberships_schema,
        "primary_key": ["intblock_id", "country_code"],
        "description": (
            "Membership edges that are current: not former_member, no left date, and the "
            "intblock is neither historical nor dissolved. Every participation status is kept."
        ),
        "sql": (
            "SELECT m.* FROM memberships m JOIN intblocks i ON i.id = m.intblock_id "
            "WHERE m.status IS DISTINCT FROM 'former_member' AND m.\"left\" IS NULL "
            "AND i.status IS DISTINCT FROM 'historical' AND i.dissolved IS NULL "
            "ORDER BY m.intblock_id, m.country_code"
        ),
    },
    {
        "name": "country_currencies",
        "schema": get_country_currencies_schema,
        "primary_key": ["country_code", "currency_code"],
        "description": "One row per country and currency; countries without currencies have no rows.",
        "sql": (
            "SELECT c.code AS country_code, u.cur.code AS currency_code, "
            "u.cur.name AS currency_name, u.cur.symbol AS currency_symbol "
            "FROM countries c, UNNEST(c.currencies) AS u(cur) "
            "ORDER BY country_code, currency_code"
        ),
    },
    {
        "name": "country_languages",
        "schema": get_country_languages_schema,
        "primary_key": ["country_code", "language_code"],
        "description": "One row per country and language; countries without languages have no rows.",
        "sql": (
            "SELECT c.code AS country_code, u.lang.code AS language_code, "
            "u.lang.name AS language_name, u.lang.official AS official "
            "FROM countries c, UNNEST(c.languages) AS u(lang) "
            "ORDER BY country_code, language_code"
        ),
    },
    {
        "name": "country_borders",
        "schema": get_country_borders_schema,
        "primary_key": ["country_code", "neighbor_iso3"],
        "description": (
            "One row per country and land neighbour (countries.borders), with the pair's current "
            "border_status (closed or restricted), or NULL when no closure is recorded."
        ),
        # Unnest in a subquery: DuckDB before 2.0 (MIN_DUCKDB included) rejects a LEFT JOIN
        # whose condition reads columns of a lateral UNNEST ("Non-inner join on correlated
        # columns not supported").
        "sql": (
            "SELECT b.country_code, b.iso3code, b.neighbor_iso3, s.status AS current_status "
            "FROM (SELECT c.code AS country_code, c.iso3code, UNNEST(c.borders) AS neighbor_iso3 "
            "FROM countries c) b "
            "LEFT JOIN border_status s ON s.\"until\" IS NULL "
            "AND ((s.country_a = b.iso3code AND s.country_b = b.neighbor_iso3) "
            "OR (s.country_b = b.iso3code AND s.country_a = b.neighbor_iso3)) "
            "ORDER BY country_code, neighbor_iso3"
        ),
    },
    {
        "name": "country_trade_agreements",
        "schema": get_country_trade_agreements_schema,
        "primary_key": ["country_code", "agreement_id"],
        "description": (
            "One row per country and trade agreement it is a current party to. Country parties map "
            "directly (via NULL); a bloc party (the EU) is expanded to its current members from "
            "current_memberships, with via set to the bloc id. Coverage is current, not historical."
        ),
        "sql": (
            "WITH p AS (SELECT tp.party_id, tp.party_type, tp.agreement_id, tp.in_force AS party_in_force, "
            "a.agreement_type, a.status AS agreement_status, a.in_force AS agreement_in_force "
            "FROM trade_agreement_parties tp JOIN trade_agreements a ON a.id = tp.agreement_id "
            "WHERE tp.status = 'party'), "
            "r AS (SELECT party_id AS country_code, agreement_id, CAST(NULL AS VARCHAR) AS via, agreement_type, "
            "agreement_status, coalesce(party_in_force, agreement_in_force) AS in_force "
            "FROM p WHERE party_type IN ('country', 'territory') "
            "UNION ALL "
            "SELECT m.country_code, p.agreement_id, p.party_id AS via, p.agreement_type, p.agreement_status, "
            "p.agreement_in_force AS in_force "
            "FROM p JOIN current_memberships m ON m.intblock_id = p.party_id "
            "WHERE p.party_type = 'intblock' AND m.include_type IN ('country', 'territory') "
            "AND m.status IN ('member', 'founding_member', 'participant', 'associate', 'associate_member', 'associated')) "
            "SELECT country_code, agreement_id, via, agreement_type, agreement_status, in_force FROM r "
            "QUALIFY row_number() OVER (PARTITION BY country_code, agreement_id ORDER BY via NULLS FIRST) = 1 "
            "ORDER BY country_code, agreement_id"
        ),
    },
    {
        "name": "country_timezones",
        "schema": get_country_timezones_schema,
        "primary_key": ["country_code", "timezone"],
        "description": "One row per country and IANA time zone.",
        "sql": (
            "SELECT c.code AS country_code, u.tz AS timezone "
            "FROM countries c, UNNEST(c.timezones) AS u(tz) "
            "ORDER BY country_code, timezone"
        ),
    },
]

# Enum-like export columns that are derived from another table's enum.
DERIVED_ENUMS = [
    ("memberships", "include_type", "intblocks", "includes[].type"),
    ("memberships", "status", "intblocks", "includes[].status"),
    ("current_memberships", "include_type", "intblocks", "includes[].type"),
    ("current_memberships", "status", "intblocks", "includes[].status"),
    ("memberships", "role", "intblocks", "includes[].role"),
    ("current_memberships", "role", "intblocks", "includes[].role"),
    ("country_borders", "current_status", "border_status", "status"),
    ("country_trade_agreements", "agreement_type", "trade_agreements", "agreement_type"),
    ("country_trade_agreements", "agreement_status", "trade_agreements", "status"),
]


def contract_version(dataset_version: str) -> str:
    """``MAJOR.MINOR`` of the dataset version; PATCH releases never change the contract."""
    parts = dataset_version.split(".")
    return ".".join(parts[:2]) if len(parts) >= 2 and all(p.isdigit() for p in parts[:2]) else dataset_version


def _schema_enums(node: Any, path: str = "") -> list[tuple[str, list[str]]]:
    """Collect ``(column path, values)`` for every ``enum`` in a JSON Schema."""
    found: list[tuple[str, list[str]]] = []
    if isinstance(node, dict):
        if "enum" in node and path:
            found.append((path, [str(v) for v in node["enum"]]))
        for key, value in node.items():
            if key == "properties" and isinstance(value, dict):
                for name, sub in value.items():
                    found.extend(_schema_enums(sub, f"{path}.{name}" if path else name))
            elif key == "items":
                found.extend(_schema_enums(value, f"{path}[]"))
            elif key in ("oneOf", "anyOf", "allOf") and isinstance(value, list):
                for sub in value:
                    found.extend(_schema_enums(sub, path))
    return found


def _enums(schemas_dir: Path) -> list[dict[str, Any]]:
    enums: list[dict[str, Any]] = []
    by_column: dict[tuple[str, str], list[str]] = {}
    for table in TABLES:
        source = table.get("enum_source")
        if not source:
            continue
        columns = set(table["schema"]().names)
        json_schema = json.loads((schemas_dir / source).read_text(encoding="utf-8"))
        prefix = table.get("enum_prefix", "")
        for path, values in _schema_enums(json_schema):
            if prefix:
                if not path.startswith(prefix):
                    continue
                path = path[len(prefix):]
            if path.split("[]")[0].split(".")[0] not in columns:
                continue
            by_column[(table["name"], path)] = values
            enums.append({"table": table["name"], "column": path, "values": values, "open": True})
    for table, column, source_table, source_column in DERIVED_ENUMS:
        values = by_column[(source_table, source_column)]
        enums.append({"table": table, "column": column, "values": values, "open": True})
    for table in ("intblocks_aliases", "countries_aliases"):
        enums.append({"table": table, "column": "reason", "values": ALIAS_REASONS, "open": True})
    enums.append({"table": "intblocks_aliases", "column": "target_dataset", "values": ALIAS_TARGET_DATASETS, "open": True})
    enums.append({"table": "trade_agreement_parties", "column": "party_type", "values": PARTY_TYPES, "open": True})
    enums.append({"table": "trade_agreement_parties", "column": "status", "values": PARTY_STATUSES, "open": True})
    enums.append({"table": "trade_agreement_parties", "column": "source", "values": ["intblock", "record"], "open": True})
    return sorted(enums, key=lambda e: (e["table"], e["column"]))


# Columns that carry includes[].status values.
STATUS_COLUMNS = (("memberships", "status"), ("intblocks", "includes[].status"))


def _deprecated(schemas_dir: Path) -> list[dict[str, Any]]:
    """Enum values scheduled for removal, from the ``deprecated`` markers in includes_status.yaml."""
    path = schemas_dir / "includes_status.yaml"
    statuses = ((safe_load(path.read_text(encoding="utf-8")) or {}).get("statuses") or {}) if path.exists() else {}
    entries = []
    for value, spec in sorted(statuses.items()):
        marker = (spec or {}).get("deprecated")
        if not marker:
            continue
        for table, column in STATUS_COLUMNS:
            entries.append({
                "kind": "enum_value",
                "table": table,
                "column": column,
                "value": value,
                "replacements": list(marker.get("replacements") or []),
                "removal": str(marker.get("removal") or "next MAJOR"),
            })
    return entries


def _deprecated_blocktypes(path: Path) -> list[dict[str, Any]]:
    """Blocktype values scheduled for removal, from the ``deprecated`` markers in blocktypes.yaml."""
    entries = []
    blocktypes = (safe_load(path.read_text(encoding="utf-8")) or []) if path.exists() else []
    for spec in sorted((b for b in blocktypes if isinstance(b, dict)), key=lambda b: str(b.get("id"))):
        marker = spec.get("deprecated")
        if not marker:
            continue
        entry = {
            "kind": "enum_value",
            "table": "intblocks",
            "column": "blocktype",
            "value": str(spec["id"]),
            "replacements": list(marker.get("replacements") or []),
            "removal": str(marker.get("removal") or "next MAJOR"),
        }
        if marker.get("note"):
            entry["note"] = str(marker["note"])
        entries.append(entry)
    return entries


def build_contract(dataset_version: str, root: Path | None = None) -> dict[str, Any]:
    """Build the contract document for ``dataset_version`` from the export schemas."""
    root = root or project_root()
    tables = []
    for table in TABLES:
        schema: pa.Schema = table["schema"]()
        tables.append(
            {
                "name": table["name"],
                "kind": "table",
                "in_duckdb": table["in_duckdb"],
                "primary_key": table["primary_key"],
                "foreign_keys": table["foreign_keys"],
                "schema_hash": schema_hash(schema),
                "columns": [
                    {"name": name, "type": type_, "nullable": nullable}
                    for name, type_, nullable in schema_columns(schema)
                ],
            }
        )
    for view in VIEWS:
        schema = view["schema"]()
        tables.append(
            {
                "name": view["name"],
                "kind": "view",
                "in_duckdb": True,
                "primary_key": view["primary_key"],
                "foreign_keys": [],
                "schema_hash": schema_hash(schema),
                "columns": [
                    {"name": name, "type": type_, "nullable": nullable}
                    for name, type_, nullable in schema_columns(schema)
                ],
                "description": view["description"],
                "definition": view["sql"],
            }
        )
    return {
        "contract_version": contract_version(dataset_version),
        "dataset_version": dataset_version,
        "min_duckdb": MIN_DUCKDB,
        "duckdb_storage_compatibility_version": DUCKDB_STORAGE_COMPATIBILITY,
        "enum_policy": "open",
        "type_grammar": TYPE_GRAMMAR,
        "tables": tables,
        "enums": _enums(root / "data" / "schemas"),
        "deprecated": _deprecated(root / "data" / "schemas")
        + _deprecated_blocktypes(root / "data" / "blocktypes" / "blocktypes.yaml"),
    }


def render_contract(dataset_version: str, root: Path | None = None) -> str:
    return json.dumps(build_contract(dataset_version, root), ensure_ascii=False, indent=2) + "\n"


def write_contract(output_dir: Path, dataset_version: str) -> Path:
    path = output_dir / CONTRACT_FILE
    path.write_text(render_contract(dataset_version), encoding="utf-8")
    return path


def file_digest(path: Path) -> dict[str, Any]:
    """``{"sha256": hex, "bytes": size}`` for one file."""
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1 << 20), b""):
            digest.update(chunk)
    return {"sha256": digest.hexdigest(), "bytes": path.stat().st_size}


def write_checksums(directory: Path) -> Path:
    """Write ``SHA256SUMS`` (``sha256sum`` format) for every other file in ``directory``."""
    lines = [
        f"{file_digest(path)['sha256']}  {path.name}"
        for path in sorted(directory.iterdir(), key=lambda p: p.name)
        if path.is_file() and path.name != CHECKSUMS_FILE
    ]
    out = directory / CHECKSUMS_FILE
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return out


def verify_checksums(directory: Path) -> list[str]:
    """Return problems: missing ``SHA256SUMS``, unlisted files, or digest mismatches."""
    path = directory / CHECKSUMS_FILE
    if not path.is_file():
        return [f"{CHECKSUMS_FILE}: missing"]
    problems: list[str] = []
    listed: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        digest, _, name = line.partition("  ")
        if not name or len(digest) != 64:
            problems.append(f"{CHECKSUMS_FILE}: malformed line {line!r}")
            continue
        listed[name] = digest
    present = {p.name for p in directory.iterdir() if p.is_file() and p.name != CHECKSUMS_FILE}
    for name in sorted(present - listed.keys()):
        problems.append(f"{CHECKSUMS_FILE}: {name} is not listed")
    for name in sorted(listed.keys() - present):
        problems.append(f"{CHECKSUMS_FILE}: {name} is listed but missing")
    for name in sorted(present & listed.keys()):
        if file_digest(directory / name)["sha256"] != listed[name]:
            problems.append(f"{CHECKSUMS_FILE}: {name} does not match its checksum")
    return problems
