"""
SupplyX - SQLite Database Loader
Builds normalized star schema and loads 180,519 order items into data/supplyx.db.
"""

from pathlib import Path
import sqlite3
import pandas as pd


def load_database(
    clean_csv: str = "data/cleaned_supply_chain.csv",
    schema_sql: str = "sql/schema.sql",
    db_path: str = "data/supplyx.db",
) -> None:
    """Builds and loads the SQLite database."""
    csv_file = Path(clean_csv)
    if not csv_file.exists():
        raise FileNotFoundError(f"Clean CSV not found: {clean_csv}")

    db_file = Path(db_path)
    db_file.parent.mkdir(parents=True, exist_ok=True)

    # 1. Connect and initialize schema
    conn = sqlite3.connect(db_file)
    with open(schema_sql, "r", encoding="utf-8") as f:
        conn.executescript(f.read())

    df = pd.read_csv(csv_file, low_memory=False)
    df["order_date_dt"] = pd.to_datetime(df["order_date"])
    df["shipping_date_dt"] = pd.to_datetime(df["shipping_date"])

    # 2. Populate dim_date
    all_dates = pd.concat([
        df["order_date_dt"].dt.floor("D"),
        df["shipping_date_dt"].dt.floor("D")
    ]).drop_duplicates().sort_values()

    date_records = []
    for d in all_dates:
        date_records.append((
            int(d.strftime("%Y%m%d")),
            d.strftime("%Y-%m-%d"),
            d.year,
            (d.month - 1) // 3 + 1,
            d.month,
            d.strftime("%B"),
            d.day,
            d.strftime("%A"),
            1 if d.weekday() >= 5 else 0,
        ))

    conn.executemany("""
        INSERT OR IGNORE INTO dim_date (
            date_key, full_date, year, quarter, month, month_name, day_of_month, day_of_week, is_weekend
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, date_records)
    conn.commit()

    # 3. Populate dim_customer
    cust_df = df[[
        "customer_id", "customer_fname", "customer_lname", "customer_segment",
        "customer_city", "customer_state", "customer_country", "customer_zipcode"
    ]].drop_duplicates(subset=["customer_id"])

    cust_records = [
        (
            int(row["customer_id"]),
            str(row["customer_fname"]),
            str(row["customer_lname"]),
            str(row["customer_segment"]),
            str(row["customer_city"]),
            str(row["customer_state"]),
            str(row["customer_country"]),
            int(row["customer_zipcode"]),
        )
        for _, row in cust_df.iterrows()
    ]
    conn.executemany("""
        INSERT OR IGNORE INTO dim_customer (
            customer_id, customer_fname, customer_lname, customer_segment,
            customer_city, customer_state, customer_country, customer_zipcode
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, cust_records)
    conn.commit()

    # 4. Populate dim_shipping_mode
    modes = sorted(df["shipping_mode"].unique())
    for m in modes:
        conn.execute("INSERT OR IGNORE INTO dim_shipping_mode (shipping_mode) VALUES (?)", (str(m),))
    conn.commit()
    mode_lookup = {row[1]: row[0] for row in conn.execute("SELECT shipping_mode_id, shipping_mode FROM dim_shipping_mode").fetchall()}

    # 5. Populate dim_geography
    geo_df = df[[
        "market", "order_region", "order_country", "order_state", "order_city"
    ]].drop_duplicates()

    geo_records = [
        (str(r["market"]), str(r["order_region"]), str(r["order_country"]), str(r["order_state"]), str(r["order_city"]))
        for _, r in geo_df.iterrows()
    ]
    conn.executemany("""
        INSERT OR IGNORE INTO dim_geography (
            market, order_region, order_country, order_state, order_city
        ) VALUES (?, ?, ?, ?, ?)
    """, geo_records)
    conn.commit()

    geo_lookup = {
        (row[1], row[2], row[3], row[4], row[5]): row[0]
        for row in conn.execute("SELECT geo_id, market, order_region, order_country, order_state, order_city FROM dim_geography").fetchall()
    }

    # 6. Populate dim_product
    prod_df = df[[
        "product_card_id", "product_name", "category_id", "category_name",
        "department_id", "department_name", "product_price"
    ]].drop_duplicates(subset=["product_card_id"])

    prod_records = [
        (
            int(r["product_card_id"]),
            str(r["product_name"]),
            int(r["category_id"]),
            str(r["category_name"]),
            int(r["department_id"]),
            str(r["department_name"]),
            float(r["product_price"]),
        )
        for _, r in prod_df.iterrows()
    ]
    conn.executemany("""
        INSERT OR IGNORE INTO dim_product (
            product_card_id, product_name, category_id, category_name,
            department_id, department_name, product_price
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
    """, prod_records)
    conn.commit()

    # 7. Map and populate fact_order_items
    print("Mapping fact records to dimension keys...")
    df["order_date_key"] = df["order_date_dt"].dt.strftime("%Y%m%d").astype(int)
    df["shipping_date_key"] = df["shipping_date_dt"].dt.strftime("%Y%m%d").astype(int)
    df["shipping_mode_id"] = df["shipping_mode"].map(mode_lookup)

    geo_keys = [
        geo_lookup[(r["market"], r["order_region"], r["order_country"], r["order_state"], r["order_city"])]
        for _, r in df.iterrows()
    ]
    df["geo_id"] = geo_keys

    fact_records = [
        (
            int(r["order_item_id"]),
            int(r["order_id"]),
            int(r["order_date_key"]),
            int(r["shipping_date_key"]),
            int(r["customer_id"]),
            int(r["product_card_id"]),
            int(r["geo_id"]),
            int(r["shipping_mode_id"]),
            str(r["order_status"]),
            str(r["delivery_status"]),
            int(r["late_delivery_risk"]),
            int(r["days_shipping_real"]),
            int(r["days_shipping_scheduled"]),
            int(r["shipping_delay_days"]),
            int(r["order_item_quantity"]),
            float(r["product_price"]),
            float(r["sales"]),
            float(r["order_item_discount"]),
            float(r["order_item_discount_rate"]),
            float(r["order_item_total"]),
            float(r["order_profit_per_order"]),
            float(r["order_item_profit_ratio"]),
            int(r["is_delayed"]),
            int(r["is_canceled"]),
            int(r["is_negative_profit"]),
        )
        for _, r in df.iterrows()
    ]

    print("Inserting 180,519 records into fact_order_items...")
    conn.execute("BEGIN TRANSACTION;")
    conn.executemany("""
        INSERT OR REPLACE INTO fact_order_items (
            order_item_id, order_id, order_date_key, shipping_date_key,
            customer_id, product_card_id, geo_id, shipping_mode_id,
            order_status, delivery_status, late_delivery_risk,
            days_shipping_real, days_shipping_scheduled, shipping_delay_days,
            order_item_quantity, product_price, sales,
            order_item_discount, order_item_discount_rate, order_item_total,
            order_profit_per_order, order_item_profit_ratio,
            is_delayed, is_canceled, is_negative_profit
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, fact_records)
    conn.commit()

    # Integrity verification
    count_facts = conn.execute("SELECT COUNT(*) FROM fact_order_items").fetchone()[0]
    count_orders = conn.execute("SELECT COUNT(DISTINCT order_id) FROM fact_order_items").fetchone()[0]
    print(f"Database build verified: {count_facts:,} line items across {count_orders:,} orders.")
    conn.close()


if __name__ == "__main__":
    load_database()
