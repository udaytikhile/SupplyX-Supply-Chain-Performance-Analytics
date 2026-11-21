"""
SupplyX - Data Cleaning and Standardization Pipeline
Transforms raw DataCo records into validated, snake_case analytical datasets.
"""

from pathlib import Path
from typing import Dict, Tuple
import pandas as pd


COLUMN_MAPPING: Dict[str, str] = {
    "Type": "order_type",
    "Days for shipping (real)": "days_shipping_real",
    "Days for shipment (scheduled)": "days_shipping_scheduled",
    "Benefit per order": "benefit_per_order",
    "Sales per customer": "sales_per_customer",
    "Delivery Status": "delivery_status",
    "Late_delivery_risk": "late_delivery_risk",
    "Category Id": "category_id",
    "Category Name": "category_name",
    "Customer City": "customer_city",
    "Customer Country": "customer_country",
    "Customer Email": "customer_email",
    "Customer Fname": "customer_fname",
    "Customer Id": "customer_id",
    "Customer Lname": "customer_lname",
    "Customer Segment": "customer_segment",
    "Customer State": "customer_state",
    "Customer Street": "customer_street",
    "Customer Zipcode": "customer_zipcode",
    "Department Id": "department_id",
    "Department Name": "department_name",
    "Latitude": "store_latitude",
    "Longitude": "store_longitude",
    "Market": "market",
    "Order City": "order_city",
    "Order Country": "order_country",
    "Order Customer Id": "order_customer_id",
    "order date (DateOrders)": "order_date",
    "Order Id": "order_id",
    "Order Item Cardprod Id": "order_item_cardprod_id",
    "Order Item Discount": "order_item_discount",
    "Order Item Discount Rate": "order_item_discount_rate",
    "Order Item Id": "order_item_id",
    "Order Item Product Price": "order_item_product_price",
    "Order Item Profit Ratio": "order_item_profit_ratio",
    "Order Item Quantity": "order_item_quantity",
    "Sales": "sales",
    "Order Item Total": "order_item_total",
    "Order Profit Per Order": "order_profit_per_order",
    "Order Region": "order_region",
    "Order State": "order_state",
    "Order Status": "order_status",
    "Order Zipcode": "order_zipcode",
    "Product Card Id": "product_card_id",
    "Product Category Id": "product_category_id",
    "Product Name": "product_name",
    "Product Price": "product_price",
    "shipping date (DateOrders)": "shipping_date",
    "Shipping Mode": "shipping_mode",
}

COLUMNS_TO_DROP = [
    "Product Description",  # 100% null
    "Customer Password",    # Masked non-analytical values
    "Product Image",        # External URLs
    "Product Status",       # 100% constant (0)
]


def clean_dataset(
    raw_path: str = "DataCoSupplyChainDataset.csv",
    output_csv_path: str = "data/cleaned_supply_chain.csv",
) -> Tuple[pd.DataFrame, Dict[str, int]]:
    """Loads, cleans, validates, and persists the SupplyX dataset."""
    raw_file = Path(raw_path)
    if not raw_file.exists():
        raise FileNotFoundError(f"Input file not found: {raw_path}")

    # 1. Load raw file
    df = pd.read_csv(raw_file, encoding="ISO-8859-1", low_memory=False)
    initial_rows = len(df)

    # 2. Drop dead columns
    cols_to_remove = [c for c in COLUMNS_TO_DROP if c in df.columns]
    if cols_to_remove:
        df = df.drop(columns=cols_to_remove)

    # 3. Rename columns to snake_case
    df = df.rename(columns=COLUMN_MAPPING)

    # 4. Standardize text categories (strip whitespace)
    text_cols = [
        "order_type", "delivery_status", "category_name", "customer_segment",
        "department_name", "market", "order_region", "order_country",
        "order_state", "order_city", "order_status", "shipping_mode", "product_name"
    ]
    for col in text_cols:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()

    # 5. Parse and validate dates
    df["order_date"] = pd.to_datetime(df["order_date"], errors="coerce")
    df["shipping_date"] = pd.to_datetime(df["shipping_date"], errors="coerce")

    # Assert no invalid unparseable dates
    if df["order_date"].isnull().any() or df["shipping_date"].isnull().any():
        raise ValueError("Data contains unparseable dates")

    # 6. Row-level checks and assertions
    # Verify shipping date is on or after order date
    invalid_dates = df["shipping_date"] < df["order_date"]
    if invalid_dates.any():
        raise ValueError(f"Found {invalid_dates.sum()} rows where shipping_date < order_date")

    # Fill customer lname/zipcode missing with standard values
    if "customer_lname" in df.columns:
        df["customer_lname"] = df["customer_lname"].fillna("Unknown")
    if "customer_zipcode" in df.columns:
        df["customer_zipcode"] = df["customer_zipcode"].fillna(0).astype(int)
    if "order_zipcode" in df.columns:
        df["order_zipcode"] = df["order_zipcode"].fillna(0).astype(int)

    # 7. Add derived analytical features
    df["shipping_delay_days"] = df["days_shipping_real"] - df["days_shipping_scheduled"]
    df["is_delayed"] = (df["days_shipping_real"] > df["days_shipping_scheduled"]).astype(int)
    df["order_year"] = df["order_date"].dt.year
    df["order_month"] = df["order_date"].dt.month
    df["order_year_month"] = df["order_date"].dt.strftime("%Y-%m")
    df["order_day_of_week"] = df["order_date"].dt.day_name()
    df["is_negative_profit"] = (df["order_profit_per_order"] < 0).astype(int)
    df["is_canceled"] = (df["delivery_status"] == "Shipping canceled").astype(int)

    # Simplified user-friendly performance bucket
    def map_performance(row):
        if row["delivery_status"] == "Late delivery":
            return "Late"
        elif row["delivery_status"] == "Advance shipping":
            return "Early"
        elif row["delivery_status"] == "Shipping on time":
            return "On-Time"
        elif row["delivery_status"] == "Shipping canceled":
            return "Canceled"
        return "Other"

    df["fulfillment_result"] = df.apply(map_performance, axis=1)

    # 8. Sort deterministically by order date and order item id
    df = df.sort_values(by=["order_date", "order_id", "order_item_id"]).reset_index(drop=True)

    # 9. Save clean dataset
    out_path = Path(output_csv_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_path, index=False)

    metadata = {
        "initial_rows": initial_rows,
        "clean_rows": len(df),
        "clean_columns": len(df.columns),
        "unique_orders": int(df["order_id"].nunique()),
        "output_path": str(out_path),
    }

    return df, metadata


if __name__ == "__main__":
    _, meta = clean_dataset()
    print("Clean dataset created successfully:")
    for k, v in meta.items():
        print(f"  {k}: {v}")
