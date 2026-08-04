"""Smoke tests for SQL examples in docs/query-examples.zh.md."""

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
    connection.execute("SET memory_limit = '512MB'")
    yield connection
    connection.close()


@pytest.mark.parametrize(
    "sql,min_rows,expected_codes",
    [
        (
            """
            SELECT c.code
            FROM countries c, UNNEST(c.other_names) AS t(oname)
            WHERE oname.id = 'zh' AND oname.name = '中华人民共和国'
            """,
            1,
            {"CN"},
        ),
        (
            "SELECT code FROM countries WHERE code_status = 'official_iso3166_1'",
            249,
            {"CN", "TH", "LA"},
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
            WHERE i.id = 'NATO' AND m.type = 'country'
            """,
            30,
            {"DE", "FR", "US"},
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
            "SELECT code FROM countries WHERE un_member = true",
            190,
            {"CN", "US", "FR"},
        ),
        (
            "SELECT code FROM countries WHERE car_side = 'left'",
            74,
            {"JP", "GB", "AU"},
        ),
        (
            """
            SELECT c.code
            FROM countries c, UNNEST(c.writing_directions) AS t(d)
            WHERE d.id = 'rtl'
            """,
            28,
            {"EG", "SA"},
        ),
        (
            """
            SELECT c.code
            FROM countries c, UNNEST(c.writing_systems) AS t(s)
            WHERE s.id = 'cyrillic'
            """,
            12,
            {"RU", "UA"},
        ),
        (
            "SELECT code FROM countries WHERE dvd_region = 1",
            8,
            {"US", "CA"},
        ),
    ],
    ids=[
        "china_zh_official_name",
        "official_iso",
        "thailand_neighbors",
        "nato_members",
        "laos_org_memberships",
        "un_members",
        "car_side_left",
        "writing_direction_rtl",
        "writing_system_cyrillic",
        "dvd_region_1",
    ],
)
def test_documented_query_zh(con, sql, min_rows, expected_codes):
    rows = con.execute(sql).fetchall()
    codes = {row[0] for row in rows}
    assert len(rows) >= min_rows
    if expected_codes:
        assert expected_codes <= codes
