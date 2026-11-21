"""
SupplyX - Data Profiling Module
Profiles raw supply chain dataset types, missing values, duplicates, and verifies absent fields.
"""

import json
from pathlib import Path
from typing import Any, Dict
import pandas as pd


def profile_dataset(file_path: str = "DataCoSupplyChainDataset.csv") -> Dict[str, Any]:
    """Inspects and profiles the raw DataCo dataset, falling back to cached report if raw file is deleted."""
    path = Path(file_path)
    if not path.exists():
        saved_report = Path("reports/data_profiling_report.json")
        if saved_report.exists():
            with open(saved_report, "r", encoding="utf-8") as f:
                return json.load(f)
        raise FileNotFoundError(f"Source file not found at {file_path}")

    df = pd.read_csv(path, encoding="ISO-8859-1", low_memory=False)

    # 1. Dimensions and primary identifiers
    total_rows = len(df)
    unique_orders = int(df["Order Id"].nunique()) if "Order Id" in df.columns else 0
    unique_order_items = int(df["Order Item Id"].nunique()) if "Order Item Id" in df.columns else 0

    # 2. Null analysis
    null_counts = df.isnull().sum()
    null_summary = {
        col: {"null_count": int(count), "null_pct": round(float(count / total_rows) * 100, 2)}
        for col, count in null_counts.items()
        if count > 0
    }

    # 3. Duplicate checks
    item_duplicates = int(df.duplicated(subset=["Order Item Id"]).sum())

    # 4. Dates
    order_dates = pd.to_datetime(df["order date (DateOrders)"], errors="coerce")
    shipping_dates = pd.to_datetime(df["shipping date (DateOrders)"], errors="coerce")
    invalid_date_rows = int(order_dates.isnull().sum() + shipping_dates.isnull().sum())
    ship_before_order_rows = int((shipping_dates < order_dates).sum())

    # 5. Absent field verification (crucial guardrail)
    absent_fields_check = {
        "shipping_cost": [c for c in df.columns if "cost" in c.lower()],
        "inventory_quantity": [c for c in df.columns if "inventory" in c.lower() or "stock" in c.lower()],
        "supplier_id": [c for c in df.columns if "supplier" in c.lower()],
        "warehouse_capacity": [c for c in df.columns if "warehouse" in c.lower() or "capacity" in c.lower()],
        "supplier_lead_time": [c for c in df.columns if "lead" in c.lower()],
    }

    # 6. Delivery status distributions
    delivery_status_counts = df["Delivery Status"].value_counts().to_dict() if "Delivery Status" in df.columns else {}
    late_risk_counts = df["Late_delivery_risk"].value_counts().to_dict() if "Late_delivery_risk" in df.columns else {}
    shipping_mode_counts = df["Shipping Mode"].value_counts().to_dict() if "Shipping Mode" in df.columns else {}

    # 7. Financial bounds
    financial_summary = {}
    for col in ["Sales", "Order Item Total", "Benefit per order", "Order Item Discount"]:
        if col in df.columns:
            financial_summary[col] = {
                "min": float(df[col].min()),
                "max": float(df[col].max()),
                "mean": round(float(df[col].mean()), 2),
                "sum": round(float(df[col].sum()), 2),
            }

    report = {
        "dataset_name": "DataCo Smart Supply Chain",
        "file_path": str(path),
        "total_rows": total_rows,
        "total_columns": len(df.columns),
        "unique_orders": unique_orders,
        "unique_order_items": unique_order_items,
        "order_item_is_unique_pk": bool(item_duplicates == 0 and unique_order_items == total_rows),
        "null_columns": null_summary,
        "date_quality": {
            "order_date_min": str(order_dates.min()),
            "order_date_max": str(order_dates.max()),
            "shipping_date_min": str(shipping_dates.min()),
            "shipping_date_max": str(shipping_dates.max()),
            "invalid_dates_count": invalid_date_rows,
            "ship_before_order_count": ship_before_order_rows,
        },
        "absent_fields_verification": {
            k: {
                "exists": len(v) > 0,
                "matching_columns": v,
                "status": "AVAILABLE" if len(v) > 0 else "ABSENT_IN_CORE_DATASET",
            }
            for k, v in absent_fields_check.items()
        },
        "delivery_status_distribution": delivery_status_counts,
        "late_delivery_risk_distribution": late_risk_counts,
        "shipping_mode_distribution": shipping_mode_counts,
        "financial_summary": financial_summary,
    }

    out_dir = Path("reports")
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / "data_profiling_report.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    return report


if __name__ == "__main__":
    rep = profile_dataset()
    print("Profiling Complete. Total rows:", rep["total_rows"])
    print("Absent fields verification:")
    for k, v in rep["absent_fields_verification"].items():
        print(f"  {k}: {v['status']}")
