"""PyArrow schemas for every exported dataset plus schema hashing."""

from __future__ import annotations

import hashlib
import json

import pyarrow as pa

# Version of the logical type grammar used by ``logical_type`` and ``schema_hash``;
# documented in docs/data-contract.md.
TYPE_GRAMMAR = "internacia-logical-types/1"

_SCALAR_TYPES = {
    pa.string(): "string",
    pa.bool_(): "boolean",
    pa.int32(): "int32",
    pa.int64(): "int64",
    pa.float64(): "float64",
}


def logical_type(data_type: pa.DataType) -> str:
    """Render an Arrow type in the canonical, library-independent type grammar."""
    if data_type in _SCALAR_TYPES:
        return _SCALAR_TYPES[data_type]
    if pa.types.is_map(data_type):
        return f"map<{logical_type(data_type.key_type)},{logical_type(data_type.item_type)}>"
    if pa.types.is_list(data_type):
        return f"list<{logical_type(data_type.value_type)}>"
    if pa.types.is_struct(data_type):
        fields = ",".join(f"{f.name}:{logical_type(f.type)}" for f in data_type)
        return f"struct<{fields}>"
    raise ValueError(f"No logical type for Arrow type {data_type}")


def schema_columns(schema: pa.Schema) -> list[list]:
    """Return ``[[name, logical_type, nullable], ...]`` in column order."""
    return [[f.name, logical_type(f.type), f.nullable] for f in schema]


def schema_hash(schema: pa.Schema) -> str:
    """SHA-256 of the canonical column list; independent of the pyarrow version."""
    canonical = json.dumps(schema_columns(schema), separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()

def get_meta_schema() -> pa.Schema:
    """Schema for the embedded DuckDB ``_meta`` table."""
    return pa.schema(
        [
            pa.field("dataset", pa.string(), nullable=False),
            ("version", pa.string()),
            ("build_date", pa.string()),
            ("git_commit", pa.string()),
            ("row_count", pa.int64()),
            ("schema_hash", pa.string()),
            ("data_license", pa.string()),
            ("contract_version", pa.string()),
        ]
    )

def _indicator_struct(value_type: pa.DataType) -> pa.DataType:
    return pa.struct(
        [
            ("value", value_type),
            ("year", pa.int64()),
            ("source", pa.string()),
            ("source_id", pa.string()),
        ]
    )

def get_countries_schema() -> pa.Schema:
    """Define explicit PyArrow schema for countries."""
    return pa.schema(
        [
            pa.field("code", pa.string(), nullable=False),
            ("name", pa.string()),
            ("iso3code", pa.string()),
            ("capital_city", pa.struct([("name", pa.string()), ("lng", pa.float64()), ("lat", pa.float64())])),
            ("region", pa.struct([("id", pa.string()), ("value", pa.string())])),
            ("adminregion", pa.struct([("id", pa.string()), ("value", pa.string())])),
            ("incomeLevel", pa.struct([("id", pa.string()), ("value", pa.string())])),
            ("lendingType", pa.struct([("id", pa.string()), ("value", pa.string())])),
            ("numeric_code", pa.string()),
            ("wikidata_id", pa.string()),
            ("geonames_id", pa.string()),
            ("ioc_code", pa.string()),
            ("fifa_code", pa.string()),
            ("fips_code", pa.string()),
            (
                "bbox",
                pa.struct(
                    [
                        ("west", pa.float64()),
                        ("east", pa.float64()),
                        ("north", pa.float64()),
                        ("south", pa.float64()),
                    ]
                ),
            ),
            ("official_name", pa.string()),
            (
                "languages",
                pa.list_(pa.struct([("code", pa.string()), ("name", pa.string()), ("official", pa.bool_())])),
            ),
            (
                "currencies",
                pa.list_(pa.struct([("code", pa.string()), ("name", pa.string()), ("symbol", pa.string())])),
            ),
            ("un_member", pa.bool_()),
            ("un_status", pa.string()),
            ("independent", pa.bool_()),
            ("entity_type", pa.string()),
            ("code_status", pa.string()),
            (
                "recognition_status",
                pa.struct(
                    [
                        ("status", pa.string()),
                        ("un_member", pa.bool_()),
                        ("notes", pa.string()),
                    ]
                ),
            ),
            (
                "parent_entity",
                pa.struct(
                    [
                        ("code", pa.string()),
                        ("name", pa.string()),
                    ]
                ),
            ),
            ("subregion", pa.string()),
            ("continents", pa.list_(pa.string())),
            ("borders", pa.list_(pa.string())),
            ("landlocked", pa.bool_()),
            ("tld", pa.string()),
            ("calling_codes", pa.list_(pa.string())),
            ("flag_emoji", pa.string()),
            ("car_side", pa.string()),
            (
                "writing_directions",
                pa.list_(pa.struct([("id", pa.string()), ("primary", pa.bool_())])),
            ),
            (
                "writing_systems",
                pa.list_(pa.struct([("id", pa.string()), ("primary", pa.bool_())])),
            ),
            ("dvd_region", pa.int32()),
            (
                "broadcast_systems",
                pa.list_(pa.struct([("id", pa.string())])),
            ),
            (
                "legal_systems",
                pa.list_(pa.struct([("id", pa.string())])),
            ),
            (
                "rail_gauges",
                pa.list_(
                    pa.struct(
                        [
                            ("id", pa.string()),
                            ("gauge_mm", pa.float64()),
                            ("primary", pa.bool_()),
                        ]
                    )
                ),
            ),
            ("start_of_week", pa.string()),
            ("demonyms", pa.struct([("female", pa.string()), ("male", pa.string())])),
            ("m49_code", pa.string()),
            ("population", _indicator_struct(pa.int64())),
            ("area", _indicator_struct(pa.float64())),
            ("gini", _indicator_struct(pa.float64())),
            ("centroid", pa.struct([("lat", pa.float64()), ("lng", pa.float64())])),
            ("timezones", pa.list_(pa.string())),
            ("timezone_status", pa.string()),
            ("native_names", pa.map_(pa.string(), pa.struct([("official", pa.string()), ("common", pa.string())]))),
            ("other_names", pa.list_(pa.struct([("id", pa.string()), ("name", pa.string())]))),
            ("common_names", pa.list_(pa.string())),
            (
                "provenance",
                pa.list_(
                    pa.struct(
                        [
                            ("field", pa.string()),
                            ("source", pa.string()),
                            ("url", pa.string()),
                            ("retrieved_at", pa.string()),
                            ("license", pa.string()),
                        ]
                    )
                ),
            ),
        ]
    )

def get_intblocks_schema() -> pa.Schema:
    """Define explicit PyArrow schema for intblocks."""
    return pa.schema(
        [
            pa.field("id", pa.string(), nullable=False),
            ("blocktype", pa.list_(pa.string())),
            ("status", pa.string()),
            ("name", pa.string()),
            ("languages", pa.list_(pa.string())),
            ("links", pa.list_(pa.struct([("url", pa.string()), ("type", pa.string())]))),
            ("founded", pa.string()),
            ("geographic_scope", pa.string()),
            ("scope_category", pa.string()),
            ("regions", pa.list_(pa.string())),
            (
                "includes",
                pa.list_(
                    pa.struct(
                        [
                            ("id", pa.string()),
                            ("name", pa.string()),
                            ("type", pa.string()),
                            ("status", pa.string()),
                            ("joined", pa.string()),
                            ("left", pa.string()),
                            ("role", pa.string()),
                            ("note", pa.string()),
                        ]
                    )
                ),
            ),
            ("membership_count", pa.int64()),
            ("membership_count_type", pa.string()),
            ("wikidata_id", pa.string()),
            ("legal_status", pa.string()),
            ("description", pa.string()),
            ("tags", pa.list_(pa.string())),
            ("topics", pa.list_(pa.struct([("key", pa.string()), ("name", pa.string())]))),
            (
                "headquarters",
                pa.struct(
                    [
                        ("city", pa.string()),
                        ("country", pa.string()),
                        ("coordinates", pa.struct([("lat", pa.float64()), ("lng", pa.float64())])),
                    ]
                ),
            ),
            ("acronyms", pa.list_(pa.struct([("lang", pa.string()), ("value", pa.string())]))),
            ("partof", pa.list_(pa.string())),  # Normalized to list of strings
            ("dissolved", pa.string()),
            ("predecessor", pa.string()),
            ("successor", pa.string()),
            ("active_period", pa.struct([("start", pa.string()), ("end", pa.string())])),
            ("last_verified", pa.string()),
            ("other_names", pa.list_(pa.struct([("id", pa.string()), ("name", pa.string())]))),
            (
                "provenance",
                pa.list_(
                    pa.struct(
                        [
                            ("field", pa.string()),
                            ("source", pa.string()),
                            ("url", pa.string()),
                            ("retrieved_at", pa.string()),
                            ("license", pa.string()),
                        ]
                    )
                ),
            ),
            # Appended last so existing column positions do not move (MINOR, additive).
            (
                "institutional_design",
                pa.struct(
                    [
                        ("mandate", pa.string()),
                        ("decision_rule", pa.string()),
                        ("decision_force", pa.string()),
                        ("independent_organs", pa.list_(pa.string())),
                        ("enforcement", pa.list_(pa.string())),
                        ("mutual_defence", pa.bool_()),
                        ("veto_holders", pa.list_(pa.string())),
                    ]
                ),
            ),
        ]
    )

def get_blocktypes_schema() -> pa.Schema:
    """Define explicit PyArrow schema for blocktypes."""
    return pa.schema(
        [
            pa.field("id", pa.string(), nullable=False),
            ("name", pa.string()),
            ("description", pa.string()),
            (
                "deprecated",
                pa.struct(
                    [
                        ("replacements", pa.list_(pa.string())),
                        ("removal", pa.string()),
                        ("note", pa.string()),
                    ]
                ),
            ),
            ("other_names", pa.list_(pa.struct([("lang", pa.string()), ("name", pa.string())]))),
        ]
    )

def get_aliases_schema() -> pa.Schema:
    """Schema for the intblock identifier alias artifact."""
    return pa.schema(
        [
            pa.field("alias", pa.string(), nullable=False),
            ("target", pa.string()),
            ("reason", pa.string()),
            ("since", pa.string()),
            ("note", pa.string()),
        ]
    )

def get_attribute_migration_schema() -> pa.Schema:
    """Schema for attribute-intblock → country-field migration artifact."""
    return pa.schema(
        [
            pa.field("retired_id", pa.string(), nullable=False),
            ("country_field", pa.string()),
            ("country_value", pa.string()),
            ("country_value_id", pa.string()),
            ("disposition", pa.string()),
            ("vocab", pa.string()),
            ("vocab_id", pa.string()),
            ("since", pa.string()),
            ("note", pa.string()),
        ]
    )

def get_memberships_schema() -> pa.Schema:
    """Define explicit PyArrow schema for the flattened membership edge table."""
    return pa.schema(
        [
            pa.field("intblock_id", pa.string(), nullable=False),
            pa.field("country_code", pa.string(), nullable=False),
            ("include_type", pa.string()),
            ("status", pa.string()),
            ("joined", pa.string()),
            ("left", pa.string()),
        ]
    )

def get_country_currencies_schema() -> pa.Schema:
    """Schema for the ``country_currencies`` view (one row per country and currency)."""
    return pa.schema(
        [
            pa.field("country_code", pa.string(), nullable=False),
            pa.field("currency_code", pa.string(), nullable=False),
            ("currency_name", pa.string()),
            ("currency_symbol", pa.string()),
        ]
    )

def get_country_languages_schema() -> pa.Schema:
    """Schema for the ``country_languages`` view (one row per country and language)."""
    return pa.schema(
        [
            pa.field("country_code", pa.string(), nullable=False),
            pa.field("language_code", pa.string(), nullable=False),
            ("language_name", pa.string()),
            ("official", pa.bool_()),
        ]
    )

def get_country_timezones_schema() -> pa.Schema:
    """Schema for the ``country_timezones`` view (one row per country and IANA zone)."""
    return pa.schema(
        [
            pa.field("country_code", pa.string(), nullable=False),
            pa.field("timezone", pa.string(), nullable=False),
        ]
    )
