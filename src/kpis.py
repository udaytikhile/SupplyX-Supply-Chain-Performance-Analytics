"""
SupplyX - KPI Computation & Reporting Engine
Calculates core supply chain metrics and enforces strict data limitation disclosures.
"""

import json
from pathlib import Path
from typing import Any, Dict
import pandas as pd


def compute_all_kpis(cleaned_csv_path: str = "data/cleaned_supply_chain.csv") -> Dict[str, Any]:
    """Computes all genuine KPIs mapped to clean dataset columns."""
    path = Path(cleaned_csv_path)
    if not path.exists():
        raise FileNotFoundError(f"Cleaned dataset not found at {cleaned_csv_path}")

    df = pd.read_csv(path, low_memory=False)
    total_items = len(df)
    unique_orders = int(df["order_id"].nunique())

    # 1. Volume & Demand Metrics
    total_quantity = int(df["order_item_quantity"].sum())
    avg_items_per_order = round(float(total_items / unique_orders), 2)
    avg_units_per_order = round(float(total_quantity / unique_orders), 2)

    # 2. Fulfillment & SLA Metrics
    late_count = int((df["late_delivery_risk"] == 1).sum())
    late_rate_overall = round(float(late_count / total_items) * 100, 2)

    # Exclude canceled shipments for delivered late rate
    shipped_mask = df["delivery_status"] != "Shipping canceled"
    shipped_count = int(shipped_mask.sum())
    late_shipped_count = int(((df["late_delivery_risk"] == 1) & shipped_mask).sum())
    late_rate_shipped = round(float(late_shipped_count / shipped_count) * 100, 2)

    ontime_mask = df["delivery_status"].isin(["Shipping on time", "Advance shipping"])
    ontime_count = int(ontime_mask.sum())
    ontime_rate = round(float(ontime_count / total_items) * 100, 2)

    canceled_count = int((df["delivery_status"] == "Shipping canceled").sum())
    canceled_rate = round(float(canceled_count / total_items) * 100, 2)

    avg_real_days = round(float(df["days_shipping_real"].mean()), 2)
    avg_scheduled_days = round(float(df["days_shipping_scheduled"].mean()), 2)
    avg_delay_gap_days = round(float((df["days_shipping_real"] - df["days_shipping_scheduled"]).mean()), 2)

    # 3. Financial & Margin Metrics
    gross_sales = round(float(df["sales"].sum()), 2)
    total_discount = round(float(df["order_item_discount"].sum()), 2)
    net_sales = round(float(df["order_item_total"].sum()), 2)
    net_profit = round(float(df["order_profit_per_order"].sum()), 2)
    profit_margin_pct = round(float(net_profit / net_sales) * 100, 2) if net_sales > 0 else 0.0
    discount_rate_overall = round(float(total_discount / gross_sales) * 100, 2) if gross_sales > 0 else 0.0

    negative_profit_items = int((df["order_profit_per_order"] < 0).sum())
    negative_profit_rate = round(float(negative_profit_items / total_items) * 100, 2)

    # 4. Mode-Level Performance
    mode_perf = {}
    for mode, group in df.groupby("shipping_mode"):
        mode_perf[str(mode)] = {
            "order_item_count": int(len(group)),
            "share_of_orders_pct": round(float(len(group) / total_items) * 100, 2),
            "late_delivery_rate_pct": round(float((group["late_delivery_risk"] == 1).mean()) * 100, 2),
            "avg_real_days": round(float(group["days_shipping_real"].mean()), 2),
            "avg_scheduled_days": round(float(group["days_shipping_scheduled"].mean()), 2),
            "delay_gap_days": round(float((group["days_shipping_real"] - group["days_shipping_scheduled"]).mean()), 2),
        }

    # 5. Market-Level Performance
    market_perf = {}
    for market, group in df.groupby("market"):
        market_perf[str(market)] = {
            "order_item_count": int(len(group)),
            "net_sales": round(float(group["order_item_total"].sum()), 2),
            "net_profit": round(float(group["order_profit_per_order"].sum()), 2),
            "profit_margin_pct": round(float(group["order_profit_per_order"].sum() / group["order_item_total"].sum()) * 100, 2),
            "late_delivery_rate_pct": round(float((group["late_delivery_risk"] == 1).mean()) * 100, 2),
            "avg_real_days": round(float(group["days_shipping_real"].mean()), 2),
        }

    kpis = {
        "volume": {
            "unique_orders": unique_orders,
            "total_order_items": total_items,
            "units_shipped": total_quantity,
            "avg_items_per_order": avg_items_per_order,
            "avg_units_per_order": avg_units_per_order,
        },
        "delivery": {
            "late_delivery_count": late_count,
            "late_delivery_rate_overall_pct": late_rate_overall,
            "late_delivery_rate_shipped_pct": late_rate_shipped,
            "ontime_count": ontime_count,
            "ontime_rate_pct": ontime_rate,
            "canceled_count": canceled_count,
            "cancellation_rate_pct": canceled_rate,
            "avg_real_shipping_days": avg_real_days,
            "avg_scheduled_shipping_days": avg_scheduled_days,
            "avg_delay_gap_days": avg_delay_gap_days,
        },
        "financial": {
            "gross_sales": gross_sales,
            "total_discount_absorbed": total_discount,
            "net_revenue": net_sales,
            "net_operating_profit": net_profit,
            "operating_profit_margin_pct": profit_margin_pct,
            "average_discount_rate_pct": discount_rate_overall,
            "loss_making_order_items": negative_profit_items,
            "loss_making_order_rate_pct": negative_profit_rate,
        },
        "shipping_cost_kpi": {
            "status": "UNAVAILABLE_IN_CORE_DATASET",
            "message": "Direct freight/shipping cost column is absent in the DataCo dataset. Fabricated figures are strictly avoided.",
            "mode_freight_extension": "Available as estimated analytical model in Milestone 7 only.",
        },
        "performance_by_shipping_mode": mode_perf,
        "performance_by_market": market_perf,
    }

    out_file = Path("reports/kpi_summary.json")
    out_file.parent.mkdir(parents=True, exist_ok=True)
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(kpis, f, indent=2)

    return kpis


if __name__ == "__main__":
    summary = compute_all_kpis()
    print("KPI Summary Generated:")
    print(f"  Unique Orders: {summary['volume']['unique_orders']:,}")
    print(f"  Total Items: {summary['volume']['total_order_items']:,}")
    print(f"  Late Delivery Rate: {summary['delivery']['late_delivery_rate_overall_pct']}%")
    print(f"  Avg Real Days: {summary['delivery']['avg_real_shipping_days']} days (Scheduled: {summary['delivery']['avg_scheduled_shipping_days']} days)")
    print(f"  Net Revenue: ${summary['financial']['net_revenue']:,.2f}")
    print(f"  Operating Profit: ${summary['financial']['net_operating_profit']:,.2f} ({summary['financial']['operating_profit_margin_pct']}%)")
    print(f"  Shipping Cost: {summary['shipping_cost_kpi']['status']}")
