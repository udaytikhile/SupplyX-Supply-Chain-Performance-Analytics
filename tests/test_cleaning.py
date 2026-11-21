"""
Tests for Data Profiling and Cleaning Modules
"""

from pathlib import Path
import pandas as pd
import pytest
from src.profiling import profile_dataset
from src.cleaning import clean_dataset


@pytest.fixture(scope="session")
def clean_data():
    """Session-scoped fixture to run data cleaning once."""
    out_csv = "data/cleaned_supply_chain.csv"
    if not Path(out_csv).exists():
        df, meta = clean_dataset("DataCoSupplyChainDataset.csv", out_csv)
    else:
        df = pd.read_csv(out_csv, low_memory=False)
        df["order_date"] = pd.to_datetime(df["order_date"])
        df["shipping_date"] = pd.to_datetime(df["shipping_date"])
    return df


def test_profiling_absent_fields():
    """Verify that absent fields are strictly identified and not fabricated."""
    report = profile_dataset("DataCoSupplyChainDataset.csv")
    absent = report["absent_fields_verification"]

    assert absent["shipping_cost"]["status"] == "ABSENT_IN_CORE_DATASET"
    assert absent["inventory_quantity"]["status"] == "ABSENT_IN_CORE_DATASET"
    assert absent["supplier_id"]["status"] == "ABSENT_IN_CORE_DATASET"
    assert absent["warehouse_capacity"]["status"] == "ABSENT_IN_CORE_DATASET"
    assert absent["supplier_lead_time"]["status"] == "ABSENT_IN_CORE_DATASET"


def test_clean_row_count_and_primary_key(clean_data):
    """Verify row preservation and uniqueness of order_item_id."""
    assert len(clean_data) == 180519
    assert clean_data["order_item_id"].nunique() == 180519
    assert clean_data["order_id"].nunique() == 65752


def test_clean_date_validity(clean_data):
    """Verify date sequencing and bounds."""
    # Shipping date must be on or after order date
    assert (clean_data["shipping_date"] >= clean_data["order_date"]).all()

    # Bound verification
    assert clean_data["order_date"].min().year == 2015
    assert clean_data["order_date"].max().year == 2018


def test_financial_consistency(clean_data):
    """Verify financial formulas."""
    # Expected gross sales: quantity * product_price
    expected_sales = clean_data["order_item_quantity"] * clean_data["product_price"]
    diff = (clean_data["sales"] - expected_sales).abs()
    assert (diff < 0.05).mean() > 0.99  # >99% exact match to cents

    # Net sales: sales - discount
    net_diff = (clean_data["order_item_total"] - (clean_data["sales"] - clean_data["order_item_discount"])).abs()
    assert (net_diff < 0.05).mean() > 0.99


def test_delivery_status_and_derived_features(clean_data):
    """Verify delivery status categorization and derived features."""
    expected_statuses = {"Late delivery", "Advance shipping", "Shipping on time", "Shipping canceled"}
    assert set(clean_data["delivery_status"].unique()) == expected_statuses

    expected_results = {"Late", "Early", "On-Time", "Canceled"}
    assert set(clean_data["fulfillment_result"].unique()) == expected_results

    # Delay days formula
    expected_delay = clean_data["days_shipping_real"] - clean_data["days_shipping_scheduled"]
    assert (clean_data["shipping_delay_days"] == expected_delay).all()
