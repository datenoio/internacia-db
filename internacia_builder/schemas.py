"""PyArrow schemas for every exported dataset plus schema hashing."""

from __future__ import annotations

import hashlib

import pyarrow as pa


def schema_hash(schema: pa.Schema) -> str:
    digest = hashlib.sha256(schema.serialize().to_pybytes()).hexdigest()
    return digest[:16]

def get_meta_schema() -> pa.Schema:
    """Schema for the embedded DuckDB ``_meta`` table."""
    return pa.schema(
        [
            ("dataset", pa.string()),
            ("version", pa.string()),
            ("build_date", pa.string()),
            ("git_commit", pa.string()),
            ("row_count", pa.int64()),
            ("schema_hash", pa.string()),
            ("data_license", pa.string()),
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
            ("code", pa.string()),
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
            ("id", pa.string()),
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
        ]
    )

def get_blocktypes_schema() -> pa.Schema:
    """Define explicit PyArrow schema for blocktypes."""
    return pa.schema(
        [
            ("id", pa.string()),
            ("name", pa.string()),
            ("other_names", pa.list_(pa.struct([("lang", pa.string()), ("name", pa.string())]))),
        ]
    )

def get_aliases_schema() -> pa.Schema:
    """Schema for the intblock identifier alias artifact."""
    return pa.schema(
        [
            ("alias", pa.string()),
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
            ("retired_id", pa.string()),
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
            ("intblock_id", pa.string()),
            ("country_code", pa.string()),
            ("include_type", pa.string()),
            ("status", pa.string()),
            ("joined", pa.string()),
            ("left", pa.string()),
        ]
    )
