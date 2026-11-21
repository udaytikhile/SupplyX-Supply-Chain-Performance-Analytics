"""
SupplyX - Documented Extension: Supplier & Inventory Reorder Analytics
Builds an analytically grounded inventory, safety stock, and supplier performance model
linking directly to genuine DataCo product IDs without contaminating core datasets.
"""

from pathlib import Path
import sqlite3
from typing import Dict, Any
import numpy as np
import pandas as pd


def generate_supplier_inventory_extension(
    clean_csv: str = "data/cleaned_supply_chain.csv",
    db_path: str = "data/supplyx.db",
    out_csv: str = "data/extension_supplier_inventory.csv",
) -> Dict[str, Any]:
    """Computes ROP, safety stock, and supplier metrics for core products."""
    df = pd.read_csv(clean_csv, low_memory=False)
    df["order_date"] = pd.to_datetime(df["order_date"])

    # 1. Calculate actual historical daily demand per product from core DataCo data
    total_days = (df["order_date"].max() - df["order_date"].min()).days + 1
    prod_demand = df.groupby(["product_card_id", "product_name", "category_id", "category_name", "department_name"]).agg(
        total_units_sold=("order_item_quantity", "sum"),
        total_revenue=("order_item_total", "sum"),
        unit_price=("product_price", "mean")
    ).reset_index()

    prod_demand["daily_avg_demand"] = np.round(prod_demand["total_units_sold"] / total_days, 2)
    # Ensure minimum daily demand of 0.1 units for calculation stability
    prod_demand["daily_avg_demand"] = np.maximum(prod_demand["daily_avg_demand"], 0.1)

    # 2. Assign realistic documented suppliers across 5 supplier tiers
    suppliers = [
        {"id": "SUP-101", "name": "Apex Global Athletics", "country": "USA", "base_lead_time": 4, "on_time_rate": 0.94},
        {"id": "SUP-102", "name": "Summit Outdoor Gear", "country": "Canada", "base_lead_time": 6, "on_time_rate": 0.91},
        {"id": "SUP-103", "name": "Pacific Rim Sourcing", "country": "China", "base_lead_time": 14, "on_time_rate": 0.85},
        {"id": "SUP-104", "name": "EuroElite Sports Corp", "country": "Germany", "base_lead_time": 8, "on_time_rate": 0.92},
        {"id": "SUP-105", "name": "Andean Athletic Apparel", "country": "Colombia", "base_lead_time": 10, "on_time_rate": 0.88},
    ]

    warehouses = [
        {"id": "WH-US-EAST", "region": "US East (New York)", "capacity": 250000},
        {"id": "WH-US-WEST", "region": "US West (California)", "capacity": 200000},
        {"id": "WH-EU-CENTRAL", "region": "Europe Central (Frankfurt)", "capacity": 300000},
        {"id": "WH-LATAM-NORTH", "region": "LATAM North (Bogota)", "capacity": 180000},
        {"id": "WH-APAC-HUB", "region": "Pacific Asia (Singapore)", "capacity": 220000},
    ]

    np.random.seed(42)  # Deterministic seed for reproducible results

    records = []
    for idx, row in prod_demand.iterrows():
        sup = suppliers[idx % len(suppliers)]
        wh = warehouses[idx % len(warehouses)]

        daily_d = row["daily_avg_demand"]
        lead_time = sup["base_lead_time"]
        lead_time_std = round(lead_time * 0.2, 1)
        demand_std = round(daily_d * 0.35, 2)

        # Standard Safety Stock Formula: Z * sqrt(L * sigma_d^2 + d^2 * sigma_L^2) with Z=1.645 (95% service level)
        z = 1.645
        safety_stock = int(np.ceil(z * np.sqrt(lead_time * (demand_std ** 2) + (daily_d ** 2) * (lead_time_std ** 2))))
        reorder_point = int(np.ceil((daily_d * lead_time) + safety_stock))

        # Holding cost: 20% of unit price per year
        holding_cost = round(float(row["unit_price"] * 0.20), 2)
        order_setup_cost = 50.0  # $50 standard PO processing fee
        annual_demand = daily_d * 365.0
        # Economic Order Quantity: sqrt(2 * D * S / H)
        eoq = int(np.ceil(np.sqrt((2 * annual_demand * order_setup_cost) / max(holding_cost, 1.0))))

        # Simulated on-hand stock: distributed around ROP to yield realistic mix of urgent and healthy items
        stock_factor = np.random.uniform(0.5, 2.2)
        on_hand_stock = int(round(reorder_point * stock_factor))

        if on_hand_stock <= reorder_point:
            status = "CRITICAL_REORDER"
        elif on_hand_stock > (reorder_point * 2.0):
            status = "OVERSTOCKED"
        else:
            status = "HEALTHY"

        # Model-based Freight Estimate (Exploratory benchmark based on product category weight proxy)
        freight_estimate_per_unit = round(float(min(max(row["unit_price"] * 0.08, 3.50), 35.00)), 2)

        records.append({
            "product_card_id": int(row["product_card_id"]),
            "product_name": str(row["product_name"]),
            "category_name": str(row["category_name"]),
            "department_name": str(row["department_name"]),
            "supplier_id": sup["id"],
            "supplier_name": sup["name"],
            "supplier_country": sup["country"],
            "supplier_lead_time_days": lead_time,
            "supplier_on_time_rate_pct": round(sup["on_time_rate"] * 100, 1),
            "warehouse_id": wh["id"],
            "warehouse_region": wh["region"],
            "daily_avg_demand_units": daily_d,
            "safety_stock_units": safety_stock,
            "reorder_point_units": reorder_point,
            "economic_order_quantity_units": eoq,
            "current_stock_on_hand_units": on_hand_stock,
            "stockout_risk_status": status,
            "days_of_supply_remaining": round(float(on_hand_stock / daily_d), 1),
            "annual_unit_holding_cost": holding_cost,
            "benchmark_freight_cost_est_per_unit": freight_estimate_per_unit,
        })

    ext_df = pd.DataFrame(records)

    # 3. Save CSV
    out_file = Path(out_csv)
    out_file.parent.mkdir(parents=True, exist_ok=True)
    ext_df.to_csv(out_file, index=False)

    # 4. Save into SQLite supplyx.db as separate extension table
    conn = sqlite3.connect(db_path)
    ext_df.to_sql("ext_supplier_inventory", conn, if_exists="replace", index=False)
    conn.commit()
    conn.close()

    summary = {
        "products_modeled": len(ext_df),
        "suppliers_modeled": len(suppliers),
        "warehouses_modeled": len(warehouses),
        "critical_reorder_count": int((ext_df["stockout_risk_status"] == "CRITICAL_REORDER").sum()),
        "healthy_stock_count": int((ext_df["stockout_risk_status"] == "HEALTHY").sum()),
        "overstocked_count": int((ext_df["stockout_risk_status"] == "OVERSTOCKED").sum()),
        "output_csv": str(out_file),
        "sqlite_table": "ext_supplier_inventory",
    }
    return summary


if __name__ == "__main__":
    res = generate_supplier_inventory_extension()
    print("Supplier & Inventory Extension Complete:")
    print(f"  Products Modeled: {res['products_modeled']}")
    print(f"  Critical Reorder Triggers: {res['critical_reorder_count']}")
    print(f"  Healthy Stocked Items: {res['healthy_stock_count']}")
    print(f"  Overstocked Items: {res['overstocked_count']}")
    print(f"  Output CSV: {res['output_csv']}")
