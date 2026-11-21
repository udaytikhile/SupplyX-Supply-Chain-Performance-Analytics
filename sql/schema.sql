-- SupplyX SQLite Relational Star Schema DDL
-- Database: data/supplyx.db

PRAGMA foreign_keys = ON;

-- 1. Date Dimension
CREATE TABLE IF NOT EXISTS dim_date (
    date_key INTEGER PRIMARY KEY, -- Format YYYYMMDD
    full_date TEXT NOT NULL UNIQUE, -- ISO YYYY-MM-DD
    year INTEGER NOT NULL,
    quarter INTEGER NOT NULL,
    month INTEGER NOT NULL,
    month_name TEXT NOT NULL,
    day_of_month INTEGER NOT NULL,
    day_of_week TEXT NOT NULL,
    is_weekend INTEGER NOT NULL -- 1 if Saturday/Sunday else 0
);

-- 2. Customer Dimension
CREATE TABLE IF NOT EXISTS dim_customer (
    customer_id INTEGER PRIMARY KEY,
    customer_fname TEXT,
    customer_lname TEXT,
    customer_segment TEXT NOT NULL,
    customer_city TEXT,
    customer_state TEXT,
    customer_country TEXT,
    customer_zipcode INTEGER
);

-- 3. Geography Dimension (Order Destination)
CREATE TABLE IF NOT EXISTS dim_geography (
    geo_id INTEGER PRIMARY KEY AUTOINCREMENT,
    market TEXT NOT NULL,
    order_region TEXT NOT NULL,
    order_country TEXT NOT NULL,
    order_state TEXT,
    order_city TEXT,
    UNIQUE(market, order_region, order_country, order_state, order_city)
);

-- 4. Product Dimension
CREATE TABLE IF NOT EXISTS dim_product (
    product_card_id INTEGER PRIMARY KEY,
    product_name TEXT NOT NULL,
    category_id INTEGER NOT NULL,
    category_name TEXT NOT NULL,
    department_id INTEGER NOT NULL,
    department_name TEXT NOT NULL,
    product_price REAL NOT NULL
);

-- 5. Shipping Mode Dimension
CREATE TABLE IF NOT EXISTS dim_shipping_mode (
    shipping_mode_id INTEGER PRIMARY KEY AUTOINCREMENT,
    shipping_mode TEXT NOT NULL UNIQUE
);

-- 6. Fact Order Items (Line-Item Granularity: 180,519 rows)
CREATE TABLE IF NOT EXISTS fact_order_items (
    order_item_id INTEGER PRIMARY KEY,
    order_id INTEGER NOT NULL,
    order_date_key INTEGER NOT NULL,
    shipping_date_key INTEGER NOT NULL,
    customer_id INTEGER NOT NULL,
    product_card_id INTEGER NOT NULL,
    geo_id INTEGER NOT NULL,
    shipping_mode_id INTEGER NOT NULL,
    order_status TEXT NOT NULL,
    delivery_status TEXT NOT NULL,
    late_delivery_risk INTEGER NOT NULL, -- 1 if late else 0
    days_shipping_real INTEGER NOT NULL,
    days_shipping_scheduled INTEGER NOT NULL,
    shipping_delay_days INTEGER NOT NULL, -- real - scheduled
    order_item_quantity INTEGER NOT NULL,
    product_price REAL NOT NULL,
    sales REAL NOT NULL, -- Gross sales = price * qty
    order_item_discount REAL NOT NULL,
    order_item_discount_rate REAL NOT NULL,
    order_item_total REAL NOT NULL, -- Net sales = sales - discount
    order_profit_per_order REAL NOT NULL,
    order_item_profit_ratio REAL NOT NULL,
    is_delayed INTEGER NOT NULL, -- 1 if delay > 0
    is_canceled INTEGER NOT NULL, -- 1 if shipping canceled
    is_negative_profit INTEGER NOT NULL, -- 1 if profit < 0
    FOREIGN KEY (order_date_key) REFERENCES dim_date(date_key),
    FOREIGN KEY (shipping_date_key) REFERENCES dim_date(date_key),
    FOREIGN KEY (customer_id) REFERENCES dim_customer(customer_id),
    FOREIGN KEY (product_card_id) REFERENCES dim_product(product_card_id),
    FOREIGN KEY (geo_id) REFERENCES dim_geography(geo_id),
    FOREIGN KEY (shipping_mode_id) REFERENCES dim_shipping_mode(shipping_mode_id)
);

-- Analytical Indexes for Fast Dashboarding & SQL Querying
CREATE INDEX IF NOT EXISTS idx_fact_order_id ON fact_order_items(order_id);
CREATE INDEX IF NOT EXISTS idx_fact_order_date ON fact_order_items(order_date_key);
CREATE INDEX IF NOT EXISTS idx_fact_geo ON fact_order_items(geo_id);
CREATE INDEX IF NOT EXISTS idx_fact_product ON fact_order_items(product_card_id);
CREATE INDEX IF NOT EXISTS idx_fact_shipping_mode ON fact_order_items(shipping_mode_id);
CREATE INDEX IF NOT EXISTS idx_fact_late_risk ON fact_order_items(late_delivery_risk);
CREATE INDEX IF NOT EXISTS idx_fact_delivery_status ON fact_order_items(delivery_status);
