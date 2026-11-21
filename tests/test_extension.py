"""
Tests for Documented Supplier and Inventory Extension
"""

from pathlib import Path
import sqlite3
import pandas as pd
import pytest
from src.extension_inventory import generate_supplier_inventory_extension


@pytest.fixture(scope="session")
def ext_summary():
    """Generate extension and cache output."""
    return generate_supplier_inventory_extension(
        clean_csv="data/cleaned_supply_chain.csv",
        db_path="data/supplyx.db",
        out_csv="data/extension_supplier_inventory.csv",
    )


def test_extension_csv_and_db_exist(ext_summary):
    """Verify extension CSV and SQLite table creation."""
    csv_p = Path(ext_summary["output_csv"])
    assert csv_p.exists()
    assert csv_p.stat().st_size > 5000

    conn = sqlite3.connect("data/supplyx.db")
    count = conn.execute("SELECT COUNT(*) FROM ext_supplier_inventory").fetchone()[0]
    conn.close()
    assert count == 118


def test_product_foreign_key_alignment():
    """Verify that every extension product_card_id genuinely exists in core dim_product."""
    conn = sqlite3.connect("data/supplyx.db")
    core_prods = set(pd.read_sql("SELECT product_card_id FROM dim_product", conn)["product_card_id"])
    ext_prods = set(pd.read_sql("SELECT product_card_id FROM ext_supplier_inventory", conn)["product_card_id"])
    conn.close()

    assert ext_prods == core_prods, "Extension products do not match core dim_product"


def test_rop_and_safety_stock_logic(ext_summary):
    """Verify ROP, Safety Stock, and Stockout Risk categorization logic."""
    df = pd.read_csv(ext_summary["output_csv"])

    # ROP must exceed or equal safety stock
    assert (df["reorder_point_units"] >= df["safety_stock_units"]).all()

    # Verify risk status logic
    for _, row in df.iterrows():
        on_hand = row["current_stock_on_hand_units"]
        rop = row["reorder_point_units"]
        status = row["stockout_risk_status"]

        if on_hand <= rop:
            assert status == "CRITICAL_REORDER"
        elif on_hand > (rop * 2.0):
            assert status == "OVERSTOCKED"
        else:
            assert status == "HEALTHY"
