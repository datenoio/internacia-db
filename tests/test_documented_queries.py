"""Smoke tests for SQL examples documented in docs/query-examples.md."""

from pathlib import Path

import duckdb
import pytest

DUCKDB_PATH = Path(__file__).resolve().parents[1] / "data" / "datasets" / "internacia.duckdb"

pytestmark = pytest.mark.skipif(
    not DUCKDB_PATH.is_file(),
    reason="internacia.duckdb not built",
)


@pytest.fixture(scope="module")
def con():
    connection = duckdb.connect(str(DUCKDB_PATH), read_only=True)
    yield connection
    connection.close()


@pytest.mark.parametrize(
    "sql,min_rows,expected_codes",
    [
        (
            "SELECT code FROM countries WHERE un_member = true",
            190,
            {"US", "FR", "TH"},
        ),
        (
            "SELECT code FROM countries WHERE code_status = 'official_iso3166_1'",
            249,
            {"US", "TH", "LA"},
        ),
        (
            """
            SELECT n.code
            FROM countries th,
                 UNNEST(th.borders) AS b(neighbor_iso3)
            JOIN countries n ON n.iso3code = b.neighbor_iso3
            WHERE th.code = 'TH'
            """,
            4,
            {"KH", "LA", "MM", "MY"},
        ),
        (
            """
            SELECT m.id AS code
            FROM intblocks i, UNNEST(i.includes) AS t(m)
            WHERE i.id = 'ASEAN' AND m.type = 'country'
            """,
            10,
            {"LA", "TH", "SG"},
        ),
        (
            """
            SELECT m.id AS code
            FROM intblocks i, UNNEST(i.includes) AS t(m)
            WHERE m.id = 'LA' AND m.type = 'country'
            """,
            100,
            set(),
        ),
        (
            "SELECT code FROM countries WHERE list_contains(borders, 'LAO')",
            5,
            {"CN", "TH", "VN"},
        ),
        (
            """
            SELECT c.code
            FROM countries c
            JOIN (
              SELECT m.id
              FROM intblocks i, UNNEST(i.includes) AS t(m)
              WHERE i.id = 'NATO' AND m.type = 'country'
            ) nato ON c.code = nato.id
            JOIN (
              SELECT m.id
              FROM intblocks i, UNNEST(i.includes) AS t(m)
              WHERE i.id = 'EU' AND m.type = 'country'
            ) eu ON c.code = eu.id
            """,
            20,
            {"DE", "FR", "IT"},
        ),
        (
            "SELECT dataset FROM _meta",
            3,
            {"countries", "intblocks", "blocktypes"},
        ),
    ],
    ids=[
        "un_members",
        "official_iso",
        "thailand_neighbors",
        "asean_members",
        "laos_org_memberships",
        "laos_reverse_borders",
        "nato_and_eu_overlap",
        "meta_tables",
    ],
)
def test_documented_query(con, sql, min_rows, expected_codes):
    rows = con.execute(sql).fetchall()
    codes = {row[0] for row in rows}
    assert len(rows) >= min_rows
    if expected_codes:
        assert expected_codes <= codes
