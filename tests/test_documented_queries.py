"""Smoke tests for SQL examples documented in docs/query-examples.md."""

import re

import duckdb
import pytest

from internacia_builder.paths import datasets_dir, project_root

DUCKDB_PATH = datasets_dir() / "internacia.duckdb"

pytestmark = pytest.mark.skipif(
    not DUCKDB_PATH.is_file(),
    reason="internacia.duckdb not built",
)


@pytest.fixture(scope="module")
def con():
    connection = duckdb.connect(str(DUCKDB_PATH), read_only=True)
    # Documented recipes must run within a bounded memory budget; a recipe
    # that exceeds this limit fails loudly instead of exhausting host memory.
    connection.execute("SET memory_limit = '512MB'")
    yield connection
    connection.close()


@pytest.mark.parametrize(
    "sql,min_rows,expected_codes",
    [
        (
            "SELECT code FROM countries WHERE un_member = true",
            193,
            {"US", "FR", "TH", "GW"},
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
            4,
            {"countries", "intblocks", "blocktypes", "memberships"},
        ),
        (
            "SELECT code FROM countries WHERE car_side = 'left'",
            74,
            {"GB", "JP", "AU", "IN"},
        ),
        (
            "SELECT code FROM countries WHERE dvd_region = 1",
            8,
            {"US", "CA"},
        ),
        (
            """
            SELECT c.code
            FROM countries c, UNNEST(c.writing_directions) AS t(d)
            WHERE d.id = 'rtl'
            """,
            28,
            {"EG", "SA", "IL"},
        ),
        (
            """
            SELECT c.code
            FROM countries c, UNNEST(c.writing_systems) AS t(s)
            WHERE s.id = 'cyrillic'
            """,
            12,
            {"RU", "UA", "BG"},
        ),
        (
            """
            SELECT c.code
            FROM countries c, UNNEST(c.broadcast_systems) AS t(b)
            WHERE b.id = 'ntsc'
            """,
            48,
            {"US", "JP", "CA"},
        ),
        (
            """
            SELECT c.code
            FROM countries c, UNNEST(c.legal_systems) AS t(l)
            WHERE l.id = 'common_law'
            """,
            54,
            {"US", "GB", "AU"},
        ),
        (
            """
            SELECT c.code
            FROM countries c, UNNEST(c.rail_gauges) AS t(g)
            WHERE g.id = 'russian' AND g."primary" = true
            """,
            18,
            {"RU", "UA", "FI"},
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
        "car_side_left",
        "dvd_region_1",
        "writing_direction_rtl",
        "writing_system_cyrillic",
        "broadcast_ntsc",
        "legal_common_law",
        "rail_gauge_russian",
    ],
)
def test_documented_query(con, sql, min_rows, expected_codes):
    rows = con.execute(sql).fetchall()
    codes = {row[0] for row in rows}
    assert len(rows) >= min_rows
    if expected_codes:
        assert expected_codes <= codes


def test_dependent_body_without_country_roster_recipe(con):
    ids = {row[0] for row in con.execute("""
        SELECT id, name, scope_category
        FROM intblocks
        WHERE scope_category = 'intergovernmental_body'
          AND COALESCE(len(includes), 0) = 0
        ORDER BY id
    """).fetchall()}
    assert {"ADF", "AF", "GCCPO"} <= ids
    for record_id in ("ADF", "AF", "GCCPO", "MSF", "CANTO", "ACIL"):
        assert con.execute(
            "SELECT COUNT(*) FROM memberships WHERE intblock_id = ?", [record_id]
        ).fetchone()[0] == 0


def test_ru_former_member_march_2022(con):
    rows = con.execute(
        """
        SELECT i.id
        FROM intblocks i, UNNEST(i.includes) AS t(m)
        WHERE m.id = 'RU'
          AND m.type = 'country'
          AND m.status = 'former_member'
          AND (
            m.left LIKE '2022-03%'
            OR m.note ILIKE '%March 2022%'
          )
        ORDER BY i.id
        """
    ).fetchall()
    assert [row[0] for row in rows] == ["COE", "ECHR", "ESCREVISED", "ICES"]


def test_ru_former_members_only(con):
    rows = con.execute(
        """
        SELECT i.id
        FROM intblocks i, UNNEST(i.includes) AS t(m)
        WHERE m.id = 'RU'
          AND m.type = 'country'
          AND m.status = 'former_member'
        ORDER BY i.id
        """
    ).fetchall()
    assert len(rows) == 17
    assert {row[0] for row in rows} == {
        "BEACST",
        "CBSS",
        "COE",
        "CTBT",
        "DANUBECOM",
        "EASTERNBLOC",
        "ECHR",
        "ECPT",
        "ESCREVISED",
        "FCNM",
        "GRECO",
        "ICES",
        "ISTC",
        "JCPOA",
        "NSS",
        "OPENSKY",
        "RAMSAR",
    }


MAJORITY_UN_MISSING_MAJOR_SQL = """
WITH un AS (
  SELECT code FROM countries WHERE un_member = true
),
un_count AS (
  SELECT COUNT(*)::DOUBLE AS n FROM un
),
block_rosters AS (
  SELECT
    i.id,
    COUNT(DISTINCT m.id) FILTER (
      WHERE m.id IN (SELECT code FROM un)
        AND COALESCE(m.status, 'member') != 'former_member'
    ) AS un_members_in_roster,
    bool_or(m.id = 'CN' AND COALESCE(m.status, 'member') != 'former_member') AS has_china,
    bool_or(m.id = 'US' AND COALESCE(m.status, 'member') != 'former_member') AS has_usa
  FROM intblocks i, UNNEST(i.includes) AS t(m)
  WHERE m.type = 'country'
  GROUP BY i.id
)
SELECT b.id
FROM block_rosters b
CROSS JOIN un_count u
WHERE b.un_members_in_roster > u.n * 0.5
  AND {condition}
ORDER BY b.id
"""


@pytest.mark.parametrize(
    "condition,expected_count,expected_ids",
    [
        (
            "(NOT b.has_china OR NOT b.has_usa)",
            78,
            {"CBD", "NAM", "EGMONTGROUP", "APMINEBANCONVENTION"},
        ),
        (
            "NOT b.has_china AND b.has_usa",
            13,
            {"EGMONTGROUP", "FLORENCE", "PTBT", "PSI", "HCOC"},
        ),
        (
            "b.has_china AND NOT b.has_usa",
            45,
            {"CBD", "UNCLOS", "BASEL"},
        ),
        (
            "NOT b.has_china AND NOT b.has_usa",
            20,
            {"NAM", "ICW", "APMINEBANCONVENTION", "EGDDS", "CTBT"},
        ),
    ],
    ids=[
        "missing_cn_or_us",
        "missing_china_only",
        "missing_usa_only",
        "missing_both",
    ],
)
def test_majority_un_missing_major_powers(con, condition, expected_count, expected_ids):
    rows = con.execute(MAJORITY_UN_MISSING_MAJOR_SQL.format(condition=condition)).fetchall()
    ids = {row[0] for row in rows}
    assert len(rows) == expected_count
    assert expected_ids <= ids


ADDITIONAL_RECIPES = [
    (
        """
        SELECT c.code FROM countries c
        WHERE c.code IN (SELECT m.id FROM intblocks i, UNNEST(i.includes) t(m) WHERE i.id='NATO' AND m.type='country')
          AND c.code NOT IN (SELECT m.id FROM intblocks i, UNNEST(i.includes) t(m) WHERE i.id='EU' AND m.type='country')
        ORDER BY c.code
        """,
        9,
        {"US", "GB", "TR", "CA"},
    ),
    (
        """
        SELECT c.code FROM countries c
        WHERE c.code IN (SELECT m.id FROM intblocks i, UNNEST(i.includes) t(m) WHERE i.id='EU' AND m.type='country')
          AND c.code NOT IN (SELECT m.id FROM intblocks i, UNNEST(i.includes) t(m) WHERE i.id='EUROAREA' AND m.type='country')
        ORDER BY c.code
        """,
        6,
        {"SE", "PL", "DK"},
    ),
    (
        """
        SELECT c.code FROM countries c
        WHERE c.code IN (SELECT m.id FROM intblocks i, UNNEST(i.includes) t(m) WHERE i.id='EU' AND m.type='country')
          AND c.code IN (SELECT m.id FROM intblocks i, UNNEST(i.includes) t(m) WHERE i.id='BSEC' AND m.type='country' AND m.status='observer')
        ORDER BY c.code
        """,
        9,
        {"DE", "FR", "IT"},
    ),
    (
        """
        SELECT c.code FROM intblocks i CROSS JOIN UNNEST(i.includes) t(m)
        JOIN countries c ON c.code = m.id AND m.type = 'country'
        WHERE c.un_member GROUP BY c.code ORDER BY COUNT(DISTINCT i.id) DESC LIMIT 1
        """,
        1,
        {"FR"},
    ),
    (
        """
        SELECT c.code FROM intblocks i CROSS JOIN UNNEST(i.includes) t(m)
        JOIN countries c ON c.code = m.id AND m.type = 'country'
        WHERE c.un_member GROUP BY c.code ORDER BY COUNT(DISTINCT i.id) ASC LIMIT 1
        """,
        1,
        {"FM"},
    ),
    (
        """
        SELECT COUNT(*) FROM (
          SELECT m.id, COUNT(DISTINCT i.id) org_count FROM intblocks i, UNNEST(i.includes) t(m)
          WHERE m.type='country' GROUP BY 1 HAVING org_count >= 100
        ) d JOIN countries c ON c.code=d.id
        WHERE c.un_member AND c.code NOT IN (SELECT m.id FROM intblocks i, UNNEST(i.includes) t(m) WHERE i.id='OECD')
        """,
        155,
        set(),
    ),
    (
        """
        SELECT c.code FROM intblocks i CROSS JOIN UNNEST(i.includes) t(m)
        JOIN countries c ON c.code = m.id AND m.type = 'country'
        WHERE m.status='observer' GROUP BY c.code HAVING COUNT(*) >= 5 ORDER BY c.code
        """,
        47,
        {"CA", "IN", "TH", "UA"},
    ),
    (
        """
        SELECT c.code FROM countries c
        WHERE c.landlocked AND c.un_member
          AND c.code NOT IN (
            SELECT m.id FROM intblocks i, UNNEST(i.includes) t(m)
            WHERE list_contains(i.blocktype,'trade') AND m.type='country'
              AND COALESCE(m.status,'member') != 'former_member'
          ) ORDER BY c.code
        """,
        0,
        set(),
    ),
    (
        """
        SELECT c.code FROM countries c WHERE c.landlocked AND len(c.borders)=1 ORDER BY c.code
        """,
        3,
        {"LS", "SM", "VA"},
    ),
    (
        """
        SELECT COUNT(*) FROM countries c
        WHERE c.incomeLevel.value IS NOT NULL AND len(c.borders) >= 2
          AND NOT EXISTS (
            SELECT 1 FROM UNNEST(c.borders) b(iso3) JOIN countries n ON n.iso3code=b.iso3
            WHERE n.incomeLevel.value IS DISTINCT FROM c.incomeLevel.value)
        """,
        22,
        set(),
    ),
    (
        """
        SELECT c.code FROM countries c
        WHERE len(c.borders) > 0 AND NOT EXISTS (
          SELECT 1 FROM UNNEST(c.borders) b(iso3) JOIN countries n ON n.iso3code=b.iso3
          WHERE n.code NOT IN (SELECT m.id FROM intblocks i, UNNEST(i.includes) t(m) WHERE i.id='EU')
        ) ORDER BY c.code
        """,
        13,
        {"BE", "VA", "AD"},
    ),
    (
        """
        SELECT COUNT(*) FROM intblocks WHERE predecessor IS NOT NULL OR successor IS NOT NULL
        """,
        37,
        set(),
    ),
    (
        """
        SELECT COUNT(*) FROM intblocks WHERE dissolved IS NOT NULL AND len(includes) > 0
        """,
        46,
        set(),
    ),
    (
        """
        SELECT COUNT(*) FROM intblocks child
        JOIN intblocks parent ON list_contains(child.partof, parent.id)
        JOIN intblocks grand ON list_contains(parent.partof, grand.id)
        WHERE grand.id = 'UN'
        """,
        53,
        set(),
    ),
    (
        """
        SELECT c.code FROM intblocks i CROSS JOIN UNNEST(i.includes) t(m)
        JOIN countries c ON c.code = m.id AND m.type = 'country'
        WHERE c.entity_type='disputed_territory' GROUP BY c.code ORDER BY COUNT(DISTINCT i.id) DESC LIMIT 1
        """,
        1,
        {"XK"},
    ),
    (
        """
        SELECT c.code FROM intblocks i CROSS JOIN UNNEST(i.includes) t(m)
        JOIN countries c ON c.code = m.id AND m.type = 'country'
        WHERE c.independent=true AND c.un_member=false GROUP BY c.code ORDER BY c.code
        """,
        1,
        {"VA"},
    ),
    (
        """
        SELECT COUNT(*) FROM intblocks
        WHERE membership_count IS NOT NULL AND len(includes) > 0 AND membership_count != len(includes)
        """,
        236,
        set(),
    ),
    (
        """
        SELECT COUNT(*) FROM intblocks i, UNNEST(i.includes) t(m)
        JOIN countries c ON c.code=m.id
        WHERE m.type='country' AND m.name IS NOT NULL AND m.name != c.name
          AND NOT list_contains(c.common_names, m.name)
        """,
        0,
        set(),
    ),
    (
        """
        SELECT id FROM intblocks ORDER BY len(blocktype) DESC, id LIMIT 1
        """,
        1,
        {"CGIARFUND"},
    ),
    (
        """
        SELECT headquarters.city FROM intblocks
        WHERE status='formal' AND headquarters.city IN ('Geneva','New York','Vienna')
        GROUP BY headquarters.city ORDER BY COUNT(*) DESC LIMIT 1
        """,
        1,
        {"Geneva"},
    ),
    (
        """
        SELECT COUNT(DISTINCT i.id) FROM intblocks i, UNNEST(i.topics) t(topic)
        WHERE topic.key = 'human_rights'
        """,
        73,
        set(),
    ),
    (
        """
        SELECT COUNT(*) FROM (
          SELECT c.code FROM intblocks i CROSS JOIN UNNEST(i.includes) t(m)
          JOIN countries c ON c.code = m.id AND m.type = 'country'
          WHERE c.wikidata_id IS NOT NULL AND c.un_member
          GROUP BY c.code HAVING COUNT(DISTINCT i.id) <= 130
        )
        """,
        0,
        set(),
    ),
    (
        """
        SELECT n.country_code AS code
        FROM memberships n
        JOIN memberships e ON e.country_code = n.country_code
        WHERE n.intblock_id = 'NATO' AND e.intblock_id = 'EU'
          AND COALESCE(n.status, 'member') != 'former_member'
          AND COALESCE(e.status, 'member') != 'former_member'
        ORDER BY 1
        """,
        23,
        {"DE", "FR", "PL"},
    ),
    (
        """
        SELECT COUNT(*) FROM intblocks
        WHERE predecessor IS NOT NULL OR successor IS NOT NULL
        """,
        37,
        set(),
    ),
    (
        """
        SELECT instrument_id, kind, status, signed, in_force
        FROM trade_agreement_instruments
        WHERE agreement_id = 'CNMO'
        ORDER BY signed, instrument_id
        """,
        17,
        {"supplement-1", "supplement-10", "investment-2017", "services-amendment-2024"},
    ),
    (
        """
        SELECT i.agreement_id, i.instrument_id, i.in_force
        FROM trade_agreement_instruments i
        WHERE i.kind = 'amending_protocol' AND i.status = 'in_force' AND i.in_force >= '2024'
        ORDER BY i.in_force DESC, i.agreement_id
        """,
        10,
        {"CNPE", "EFTATN", "EFTAJO", "CLID", "EUNO", "CNSG", "CNMO", "CNHK", "DEPA"},
    ),
]


@pytest.mark.parametrize(
    "sql,expected_count,expected_codes",
    ADDITIONAL_RECIPES,
    ids=[
        "nato_not_eu",
        "eu_not_emu",
        "eu_member_bsec_observer",
        "org_density_top",
        "org_density_bottom",
        "dense_not_oecd",
        "observer_5plus",
        "landlocked_no_trade",
        "landlocked_enclave",
        "border_income_homogeneous",
        "all_neighbors_eu",
        "successor_chains",
        "dissolved_with_roster",
        "un_grandchildren",
        "disputed_top",
        "non_un_independent",
        "membership_count_mismatch",
        "include_name_mismatch",
        "most_blocktypes",
        "hq_geneva_ny_vienna",
        "human_rights_topics",
        "wikidata_sparse",
        "nato_intersect_eu",
        "succession_chains_count",
        "agreement_instruments",
        "upgraded_since_2024",
    ],
)
def test_additional_recipes(con, sql, expected_count, expected_codes):
    rows = con.execute(sql).fetchall()
    if re.match(r"\s*SELECT\s+COUNT\s*\(", sql, re.IGNORECASE | re.DOTALL):
        assert len(rows) == 1
        assert rows[0][0] == expected_count
        return
    codes = {row[0] for row in rows}
    assert len(rows) == expected_count
    if expected_codes:
        assert expected_codes <= codes


def test_former_members_with_join_and_left(con):
    count = con.execute(
        """
        SELECT COUNT(*)
        FROM intblocks i, UNNEST(i.includes) AS t(m)
        WHERE m.status = 'former_member'
          AND m.joined IS NOT NULL
        """
    ).fetchone()[0]
    assert count == 312


def test_world_bank_region_filter_uses_region_id(con):
    """The documented World Bank region recipe filters on region.id.

    region.value holds the Bank's current label, which the Bank renames (MEA in
    2025), so the docs filter on the stable id. Each id carries one current label.
    """
    rows = con.execute(
        """
        SELECT code FROM countries
        WHERE region.id = 'ECS' AND code_status = 'official_iso3166_1'
        ORDER BY code
        """
    ).fetchall()
    codes = {r[0] for r in rows}
    assert len(rows) == 61
    assert {"DE", "FR", "UA", "KZ"} <= codes
    labels = dict(con.execute(
        "SELECT region.id, list_distinct(list(region.value)) FROM countries WHERE region.id IS NOT NULL GROUP BY 1"
    ).fetchall())
    assert labels["ECS"] == ["Europe & Central Asia"]
    assert labels["MEA"] == ["Middle East, North Africa, Afghanistan & Pakistan"]
    assert all(len(values) == 1 for values in labels.values())


def test_world_bank_classification_gap_figures(con):
    """Docs cite exact classification-gap counts; keep them anchored."""
    missing_region = con.execute(
        "SELECT COUNT(*) FROM countries WHERE region.id IS NULL"
    ).fetchone()[0]
    missing_admin = con.execute(
        "SELECT COUNT(*) FROM countries WHERE adminregion.id IS NULL"
    ).fetchone()[0]
    assert missing_region == 8
    assert missing_admin == 119


def test_pandas_struct_field_access():
    """The documented pandas struct recipes must execute as written."""
    pd = pytest.importorskip("pandas")
    parquet = DUCKDB_PATH.parent / "countries.parquet"
    if not parquet.is_file():
        pytest.skip("countries.parquet not built")
    df = pd.read_parquet(parquet)
    pop = df["population"].apply(lambda v: v["value"] if v is not None else None)
    assert pop.notna().sum() > 200
    df2 = pd.read_parquet(parquet, dtype_backend="pyarrow")
    pop2 = df2["population"].struct.field("value")
    assert pop2.notna().sum() > 200


def test_memberships_edge_table(con):
    """The flattened memberships table matches the intblocks includes."""
    edge = con.execute("SELECT COUNT(*) FROM memberships").fetchone()[0]
    derived = con.execute(
        """
        SELECT count(*) FROM (SELECT unnest(includes) AS m FROM intblocks)
        WHERE m.type != 'organization'
        """
    ).fetchone()[0]
    assert edge == derived
    nato = con.execute(
        "SELECT COUNT(*) FROM memberships WHERE intblock_id = 'NATO' AND status = 'member'"
    ).fetchone()[0]
    assert nato >= 32


def test_separate_trans_asian_railway_agreement_recipe(con):
    rows = con.execute(
        """
        SELECT country_code, joined
        FROM memberships
        WHERE intblock_id = 'TARAGREEMENT' AND status = 'member'
        ORDER BY country_code
        """
    ).fetchall()
    assert len(rows) == 22 and all(joined for _, joined in rows)
    assert con.execute(
        "SELECT count(*) FROM memberships WHERE intblock_id IN ('TAR', 'CIF', 'TELESUR')"
    ).fetchone()[0] == 0


def test_schema_property_descriptions_complete():
    """llms.txt claims every schema property has a description; enforce it."""
    import json

    schemas_dir = project_root() / "data" / "schemas"
    for name in ("countries.schema.json", "intblocks.schema.json"):
        schema = json.loads((schemas_dir / name).read_text(encoding="utf-8"))
        missing = [
            key
            for key, spec in schema["properties"].items()
            if not (isinstance(spec, dict) and spec.get("description"))
        ]
        assert not missing, f"{name} properties without description: {missing}"


def test_jaccard_value(con):
    value = con.execute(
        """
        WITH a AS (
          SELECT m.id FROM intblocks i, UNNEST(i.includes) t(m) WHERE i.id='NATO' AND m.type='country'
        ), b AS (
          SELECT m.id FROM intblocks i, UNNEST(i.includes) t(m) WHERE i.id='EU' AND m.type='country'
        )
        SELECT ROUND(
          (SELECT COUNT(*) FROM (SELECT id FROM a INTERSECT SELECT id FROM b)) * 1.0
          / NULLIF((SELECT COUNT(*) FROM (SELECT id FROM a UNION SELECT id FROM b)), 0), 2
        )
        """
    ).fetchone()[0]
    assert value == 0.64


@pytest.mark.parametrize(
    "sql,rows",
    [
        (
            "SELECT country_code FROM current_memberships WHERE intblock_id = 'NATO' "
            "AND status IN ('member', 'founding_member')",
            32,
        ),
        ("SELECT country_code FROM country_currencies WHERE currency_code = 'EUR'", 35),
        ("SELECT country_code FROM country_languages WHERE language_code = 'fra'", 46),
        ("SELECT timezone FROM country_timezones WHERE country_code = 'RU'", 27),
    ],
)
def test_canonical_view_recipes(con, sql, rows):
    assert len(con.execute(sql).fetchall()) == rows


def test_alias_resolution_recipe(con):
    resolved = con.execute(
        "SELECT x.id, COALESCE(a.target, x.id) FROM (VALUES ('USAN'), ('EU')) AS x(id) "
        "LEFT JOIN intblocks_aliases a ON a.alias = x.id AND a.reason <> 'disambiguated' ORDER BY 1"
    ).fetchall()
    assert resolved == [("EU", "EU"), ("USAN", "UNASUR")]


def _documented_sql(heading: str) -> str:
    """The first fenced SQL block under a ``### heading`` in docs/query-examples.md."""
    text = (project_root() / "docs" / "query-examples.md").read_text(encoding="utf-8")
    section = text.split(f"### {heading}\n", 1)[1]
    return section.split("```sql\n", 1)[1].split("```", 1)[0]


def test_authority_level_recipe(con):
    rows = dict(
        (row[0], row[2]) for row in con.execute(_documented_sql("Authority level from institutional design")).fetchall()
    )
    assert len(rows) == 112
    assert {rows[i] for i in ("EU", "UNSC", "WTO")} == {"high"}
    assert {rows[i] for i in ("G7", "APEC")} == {"low"}
    assert {rows[i] for i in ("UPU", "WMO", "OPEC")} == {"medium"}
    assert {rows[i] for i in ("NATO", "G-20", "CIS")} == {None}
    veto = con.execute("SELECT institutional_design.veto_holders FROM intblocks WHERE id = 'UNSC'").fetchone()[0]
    assert sorted(veto) == ["CN", "FR", "GB", "RU", "US"]


def test_authority_level_none_for_reference_enumeration(con):
    sql = _documented_sql("Authority level from institutional design").replace(
        "WHERE institutional_design IS NOT NULL", "WHERE scope_category = 'reference_enumeration'"
    )
    levels = {row[2] for row in con.execute(sql).fetchall()}
    assert levels == {"none"}


def test_member_capacity_concentration_recipe(con):
    cols = ["intblock_id", "members", "world_pop_pct", "largest_member", "largest_member_pct",
            "hhi", "effective_members", "min_pop_year", "max_pop_year"]
    rows = {
        row[0]: dict(zip(cols, row, strict=True))
        for row in con.execute(_documented_sql("Member capacity concentration (population)")).fetchall()
    }
    assert set(rows) == {"EAEU", "EU", "NATO", "UPU"}
    assert rows["UPU"]["world_pop_pct"] > 95
    assert rows["EAEU"]["largest_member"] == "RU"
    assert rows["EAEU"]["effective_members"] < 2
    assert rows["EU"]["effective_members"] > rows["EAEU"]["effective_members"]
    for row in rows.values():
        assert 0 < row["hhi"] <= 1
        assert row["min_pop_year"] <= row["max_pop_year"]


def test_country_borders_recipe(con):
    rows = dict(con.execute(_documented_sql("Current border status of a country's neighbours")).fetchall())
    assert rows == {"AZE": "closed", "GEO": None, "IRN": None, "TUR": "closed"}


def test_sea_access_gateways_recipe(con):
    rows = con.execute(_documented_sql("Sea-access gateways of landlocked countries")).fetchall()
    by_country: dict[str, dict[str, int]] = {}
    direct: dict[str, int] = {}
    for code, gateway, hops, n_direct, _single in rows:
        by_country.setdefault(code, {})[gateway] = hops
        direct[code] = n_direct
    assert len(by_country) == 44
    assert {g for g, hops in by_country["AM"].items() if hops == 1} == {"GEO", "IRN"}
    assert "TUR" not in by_country["AM"] and "AZE" not in by_country["AM"]
    assert by_country["LS"] == {"ZAF": 1}
    for code in ("LI", "UZ"):
        assert direct[code] == 0 and min(by_country[code].values()) == 2
    assert {code for code, n in direct.items() if n == 1} == {"KG", "LS", "SM", "TJ", "TM", "VA"}


def test_route_roles_recipe(con):
    rows = con.execute(_documented_sql("Countries by role on infrastructure routes")).fetchall()
    tap = {(code, role) for intblock, _name, code, role in rows if intblock == "TAP"}
    assert tap == {("GR", "origin"), ("AL", "transit"), ("IT", "destination")}
    assert {role for *_, role in rows} <= {"origin", "transit", "destination", "terminal"}
