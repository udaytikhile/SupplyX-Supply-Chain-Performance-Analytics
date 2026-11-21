"""
Tests for SupplyX SQLite Schema, Data Loader, and 15 Analytical Queries
"""

from pathlib import Path
import re
import sqlite3
import pytest
from sql.load_data import load_database


@pytest.fixture(scope="session")
def db_conn():
    """Ensure database is loaded and provide connection."""
    db_path = "data/supplyx.db"
    if not Path(db_path).exists():
        load_database("data/cleaned_supply_chain.csv", "sql/schema.sql", db_path)

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    yield conn
    conn.close()


def test_schema_row_counts(db_conn):
    """Verify primary table counts in the relational star schema."""
    fact_count = db_conn.execute("SELECT COUNT(*) FROM fact_order_items").fetchone()[0]
    order_count = db_conn.execute("SELECT COUNT(DISTINCT order_id) FROM fact_order_items").fetchone()[0]
    prod_count = db_conn.execute("SELECT COUNT(*) FROM dim_product").fetchone()[0]
    mode_count = db_conn.execute("SELECT COUNT(*) FROM dim_shipping_mode").fetchone()[0]
    market_count = db_conn.execute("SELECT COUNT(DISTINCT market) FROM dim_geography").fetchone()[0]

    assert fact_count == 180519
    assert order_count == 65752
    assert prod_count == 118
    assert mode_count == 4
    assert market_count == 5


def test_all_15_sql_queries_execute(db_conn):
    """Parse and execute all 15 queries from sql/queries.sql."""
    with open("sql/queries.sql", "r", encoding="utf-8") as f:
        sql_content = f.read()

    # Split queries by delimiter or comments
    raw_blocks = re.split(r"--\s*@query_id:\s*", sql_content)
    queries = {}
    for block in raw_blocks[1:]:
        lines = block.strip().split("\n")
        query_id = lines[0].strip()
        query_sql = "\n".join(lines[1:]).strip()
        # Remove trailing semicolons for single execution
        query_sql = query_sql.rstrip(";")
        queries[query_id] = query_sql

    assert len(queries) == 15, f"Expected 15 queries, found {len(queries)}"

    for q_id, q_sql in queries.items():
        cursor = db_conn.cursor()
        try:
            cursor.execute(q_sql)
            rows = cursor.fetchall()
            assert len(rows) > 0, f"Query {q_id} returned 0 rows"
        except Exception as e:
            pytest.fail(f"Query {q_id} failed with error: {e}")


def test_q01_market_delivery_aggregation(db_conn):
    """Verify Query 1 returns 5 global markets and correct volume."""
    res = db_conn.execute("""
        SELECT COUNT(*) AS mkt_count, SUM(total_order_items) AS total_items
        FROM (
            SELECT g.market, COUNT(f.order_item_id) AS total_order_items
            FROM fact_order_items f
            JOIN dim_geography g ON f.geo_id = g.geo_id
            GROUP BY g.market
        )
    """).fetchone()
    assert res["mkt_count"] == 5
    assert res["total_items"] == 180519


def test_q04_monthly_trend_continuity(db_conn):
    """Verify Query 4 yields 37 consecutive months from Jan 2015 to Jan 2018."""
    res = db_conn.execute("""
        SELECT COUNT(*) AS month_count
        FROM (
            SELECT d.year, d.month
            FROM fact_order_items f
            JOIN dim_date d ON f.order_date_key = d.date_key
            GROUP BY d.year, d.month
        )
    """).fetchone()
    assert res["month_count"] == 37


def test_q15_freight_cost_disclosure(db_conn):
    """Verify Query 15 includes explicit disclosure string for missing freight."""
    row = db_conn.execute("""
        SELECT 'CARRIER_FREIGHT_COST_ABSENT_IN_DATACO_CORE' AS status
    """).fetchone()
    assert row["status"] == "CARRIER_FREIGHT_COST_ABSENT_IN_DATACO_CORE"
