"""Smoke tests for Polars examples documented in docs/query-examples-polars.md."""

from pathlib import Path

import pytest

DATASETS = Path(__file__).resolve().parents[1] / "data" / "datasets"
COUNTRIES_PARQUET = DATASETS / "countries.parquet"
INTBLOCKS_PARQUET = DATASETS / "intblocks.parquet"
MEMBERSHIPS_PARQUET = DATASETS / "memberships.parquet"

pytestmark = [
    pytest.mark.skipif(not COUNTRIES_PARQUET.is_file(), reason="countries.parquet not built"),
    pytest.mark.skipif(not INTBLOCKS_PARQUET.is_file(), reason="intblocks.parquet not built"),
    pytest.mark.skipif(not MEMBERSHIPS_PARQUET.is_file(), reason="memberships.parquet not built"),
]


@pytest.fixture(scope="module")
def pl():
    return pytest.importorskip("polars")


@pytest.fixture(scope="module")
def countries(pl):
    return pl.read_parquet(COUNTRIES_PARQUET)


@pytest.fixture(scope="module")
def intblocks(pl):
    return pl.read_parquet(INTBLOCKS_PARQUET)


@pytest.fixture(scope="module")
def memberships(pl):
    return pl.read_parquet(MEMBERSHIPS_PARQUET)


def country_memberships(pl, intblocks):
    return (
        intblocks.select(
            pl.col("id").alias("intblock_id"),
            pl.col("name").alias("intblock_name"),
            "includes",
        )
        .explode("includes", empty_as_null=True)
        .drop_nulls("includes")
        .unnest("includes")
        .filter(pl.col("type") == "country")
    )


def test_un_members(pl, countries):
    rows = countries.filter(pl.col("un_member")).select("code")
    assert rows.height == 193
    assert {"US", "FR", "TH", "GW"} <= set(rows["code"].to_list())


def test_official_iso(pl, countries):
    rows = countries.filter(pl.col("code_status") == "official_iso3166_1")
    assert rows.height == 249


def test_struct_population(pl, countries):
    pop = countries.select(pl.col("population").struct.field("value").alias("pop"))
    assert pop.filter(pl.col("pop").is_not_null()).height > 200


def test_thailand_neighbors(pl, countries):
    neighbors = (
        countries.filter(pl.col("code") == "TH")
        .select("borders")
        .explode("borders", empty_as_null=True)
        .join(countries, left_on="borders", right_on="iso3code")
        .select("code")
    )
    assert set(neighbors["code"].to_list()) == {"KH", "LA", "MM", "MY"}


def test_laos_reverse_borders(pl, countries):
    rows = countries.filter(pl.col("borders").list.contains("LAO"))
    assert rows.height == 5
    assert {"CN", "TH", "VN"} <= set(rows["code"].to_list())


def test_attribute_filters(pl, countries):
    assert countries.filter(pl.col("car_side") == "left").height == 74
    assert countries.filter(pl.col("dvd_region") == 1).height == 8
    rtl = (
        countries.explode("writing_directions", empty_as_null=True)
        .drop_nulls("writing_directions")
        .filter(pl.col("writing_directions").struct.field("id") == "rtl")
    )
    assert rtl.height == 28
    cyr = (
        countries.explode("writing_systems", empty_as_null=True)
        .drop_nulls("writing_systems")
        .filter(pl.col("writing_systems").struct.field("id") == "cyrillic")
    )
    assert cyr.height == 12
    assert countries.filter(
        (pl.col("region").struct.field("id") == "ECS")
        & (pl.col("code_status") == "official_iso3166_1")
    ).height == 61


def test_nato_eu_memberships(pl, memberships):
    nato = memberships.filter(
        (pl.col("intblock_id") == "NATO") & (pl.col("status") == "member")
    )
    eu = memberships.filter(pl.col("intblock_id") == "EU")
    assert nato.height == 32
    assert eu.height == 27
    overlap = nato.select("country_code").join(eu.select("country_code"), on="country_code")
    assert overlap.height == 23
    assert {"DE", "FR", "IT"} <= set(overlap["country_code"].to_list())


def test_asean_and_laos(pl, memberships):
    assert memberships.filter(pl.col("intblock_id") == "ASEAN").height == 11
    assert memberships.filter(pl.col("country_code") == "LA").height >= 100


def test_ru_former_and_march_2022(pl, intblocks):
    members = country_memberships(pl, intblocks)
    ru = members.filter((pl.col("id") == "RU") & (pl.col("status") == "former_member"))
    assert set(ru["intblock_id"].to_list()) == {
        "BEACST",
        "DANUBECOM",
        "EASTERNBLOC",
        "ECHR",
        "EUA",
        "GRECO",
        "ICES",
        "JCPOA",
        "NSS",
        "OPENSKY",
        "RAMSAR",
    }
    march = members.filter(
        (pl.col("id") == "RU")
        & (pl.col("status") == "former_member")
        & (
            pl.col("left").str.starts_with("2022-03")
            | pl.col("note").str.contains("(?i)March 2022")
        )
    )
    assert set(march["intblock_id"].to_list()) == {"ECHR", "EUA", "ICES"}


def test_jaccard_nato_eu(pl, memberships):
    nato = set(memberships.filter(pl.col("intblock_id") == "NATO")["country_code"].to_list())
    eu = set(memberships.filter(pl.col("intblock_id") == "EU")["country_code"].to_list())
    assert round(len(nato & eu) / len(nato | eu), 2) == 0.64


def test_intblock_aliases_parquet(pl):
    aliases = pl.read_parquet(DATASETS / "intblocks_aliases.parquet")
    assert {"alias", "target"} <= set(aliases.columns)
    assert aliases.height > 0
