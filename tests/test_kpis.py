"""
Tests for SupplyX KPI Engine and Metric Formulations
"""

import pytest
from src.kpis import compute_all_kpis


@pytest.fixture(scope="session")
def kpi_data():
    """Compute and cache KPIs."""
    return compute_all_kpis("data/cleaned_supply_chain.csv")


def test_volume_metrics(kpi_data):
    """Verify distinct orders, line items, and unit volume."""
    vol = kpi_data["volume"]
    assert vol["unique_orders"] == 65752
    assert vol["total_order_items"] == 180519
    assert vol["units_shipped"] == 384079
    assert 2.7 <= vol["avg_items_per_order"] <= 2.8


def test_delivery_sla_metrics(kpi_data):
    """Verify delivery and late rate calculations."""
    deliv = kpi_data["delivery"]
    assert 54.8 <= deliv["late_delivery_rate_overall_pct"] <= 54.9
    assert 57.2 <= deliv["late_delivery_rate_shipped_pct"] <= 57.4
    assert 40.8 <= deliv["ontime_rate_pct"] <= 41.0
    assert 4.2 <= deliv["cancellation_rate_pct"] <= 4.4
    assert 3.48 <= deliv["avg_real_shipping_days"] <= 3.52
    assert 2.90 <= deliv["avg_scheduled_shipping_days"] <= 2.95
    assert deliv["avg_delay_gap_days"] > 0.5  # Real days exceed scheduled days


def test_financial_metrics(kpi_data):
    """Verify revenue, discounts, and margin calculations."""
    fin = kpi_data["financial"]
    assert 36_700_000 <= fin["gross_sales"] <= 36_900_000
    assert 3_700_000 <= fin["total_discount_absorbed"] <= 3_800_000
    assert 33_000_000 <= fin["net_revenue"] <= 33_100_000
    assert 3_900_000 <= fin["net_operating_profit"] <= 4_000_000
    assert 11.9 <= fin["operating_profit_margin_pct"] <= 12.1
    assert 18.0 <= fin["loss_making_order_rate_pct"] <= 19.0


def test_shipping_cost_disclosure(kpi_data):
    """Ensure missing shipping cost is truthfully flagged as unavailable."""
    cost_kpi = kpi_data["shipping_cost_kpi"]
    assert cost_kpi["status"] == "UNAVAILABLE_IN_CORE_DATASET"
    assert "absent" in cost_kpi["message"].lower()


def test_shipping_mode_breakdown(kpi_data):
    """Verify presence of all shipping classes with correct SLA gaps."""
    modes = kpi_data["performance_by_shipping_mode"]
    assert set(modes.keys()) == {"Standard Class", "Second Class", "First Class", "Same Day"}

    # First Class should show highest late rate due to 1-day scheduling promise
    assert modes["First Class"]["late_delivery_rate_pct"] > 90.0
    assert modes["Standard Class"]["late_delivery_rate_pct"] < 40.0


def test_market_breakdown(kpi_data):
    """Verify presence of all 5 geographic markets."""
    markets = kpi_data["performance_by_market"]
    assert set(markets.keys()) == {"Africa", "Europe", "LATAM", "Pacific Asia", "USCA"}
    for m in markets.values():
        assert m["net_sales"] > 0
        assert m["late_delivery_rate_pct"] > 0
