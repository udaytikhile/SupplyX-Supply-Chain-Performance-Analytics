# SupplyX Comprehensive Data Dictionary
*An exhaustive reference for core DataCo attributes, derived analytical metrics, and extension fields.*

---

## 1. Verified Absent Fields (Strict Non-Fabrication Disclosure)

The following fields **DO NOT EXIST** in the DataCo Smart Supply Chain dataset. Rather than inventing synthetic placeholders that corrupt historical records, SupplyX explicitly marks them as unavailable in the core layer:

| Absent Concept | Search Pattern | Ground Truth Finding in DataCo Core | Handling & Mitigation Strategy |
| :--- | :--- | :--- | :--- |
| **Carrier Freight / Shipping Cost** | `cost`, `freight`, `carrier_fee` | **0 matching columns**. No shipping fee or carrier billing exists. | Marked as `UNAVAILABLE_IN_CORE_DATASET`. A model-based freight cost estimate is provided strictly in the Milestone 7 extension layer. |
| **On-Hand Inventory Levels** | `inventory`, `stock`, `on_hand` | `Product Status` exists but is invariant (value `0` across 100% of rows). | Physical warehouse inventory snapshot modeled analytically in Milestone 7 extension layer (`data/extension_supplier_inventory.csv`). |
| **Supplier Identifiers** | `supplier_id`, `vendor_id` | **0 matching columns**. | Documented supplier dimension created in Milestone 7 extension layer. |
| **Supplier Inbound Lead Times** | `lead_time`, `po_date`, `receipt_date` | **0 matching columns**. Core dataset only tracks outbound customer shipping duration. | Modeled with standard normal variance ($L \approx 4-14$ days) in Milestone 7 extension layer. |
| **Warehouse Facility Capacity** | `warehouse_id`, `capacity`, `bin_location` | **0 matching columns**. | Modeled across 5 regional distribution centers in Milestone 7 extension layer. |

---

## 2. Core Cleaned Dataset (`data/cleaned_supply_chain.csv`)

| Standard Column Name (snake_case) | Raw DataCo Header | Data Type | Null Count | Description & Analytical Definition |
| :--- | :--- | :--- | :--- | :--- |
| `order_item_id` | `Order Item Id` | INTEGER | 0 | **Primary Key**. Unique identifier for each order line item (180,519 rows). |
| `order_id` | `Order Id` | INTEGER | 0 | Identifier for the customer order transaction (65,752 distinct orders). |
| `order_date` | `order date (DateOrders)` | DATETIME | 0 | Timestamp when customer placed the order (Jan 1, 2015 to Jan 31, 2018). |
| `shipping_date` | `shipping date (DateOrders)` | DATETIME | 0 | Timestamp when package departed fulfillment facility (Jan 3, 2015 to Feb 6, 2018). |
| `days_shipping_real` | `Days for shipping (real)` | INTEGER | 0 | Actual days elapsed from order placement to customer delivery (0 to 6 days). |
| `days_shipping_scheduled` | `Days for shipment (scheduled)` | INTEGER | 0 | Promised delivery window communicated to customer at checkout (0 to 4 days). |
| `shipping_mode` | `Shipping Mode` | TEXT | 0 | Fulfillment class: `Standard Class`, `Second Class`, `First Class`, `Same Day`. |
| `delivery_status` | `Delivery Status` | TEXT | 0 | `Late delivery`, `Advance shipping`, `Shipping on time`, `Shipping canceled`. |
| `late_delivery_risk` | `Late_delivery_risk` | INTEGER | 0 | Binary flag: `1` if shipment was delivered after scheduled date, `0` otherwise. |
| `order_status` | `Order Status` | TEXT | 0 | Lifecycle status (`COMPLETE`, `PENDING`, `CLOSED`, `CANCELED`, etc.). |
| `product_card_id` | `Product Card Id` | INTEGER | 0 | Unique product SKU identifier (118 distinct products). |
| `product_name` | `Product Name` | TEXT | 0 | Commercial product title. |
| `product_price` | `Product Price` | REAL | 0 | Catalog list price per unit ($9.99 to $1,999.99). |
| `order_item_quantity` | `Order Item Quantity` | INTEGER | 0 | Units purchased in this line item (1 to 5 units). |
| `sales` | `Sales` | REAL | 0 | Gross catalog sales value: `order_item_quantity * product_price`. |
| `order_item_discount` | `Order Item Discount` | REAL | 0 | Dollar discount deducted from gross sales. |
| `order_item_discount_rate`| `Order Item Discount Rate`| REAL | 0 | Discount percentage applied (0.00 to 0.25). |
| `order_item_total` | `Order Item Total` | REAL | 0 | Net collected sales: `sales - order_item_discount`. |
| `order_profit_per_order` | `Order Profit Per Order` | REAL | 0 | Net operating profit attributed to this order line (-$4,274.98 to +$911.80). |
| `order_item_profit_ratio`| `Order Item Profit Ratio` | REAL | 0 | Operating profit margin ratio: `order_profit_per_order / order_item_total`. |
| `category_id` | `Category Id` | INTEGER | 0 | Product category code (50 categories). |
| `category_name` | `Category Name` | TEXT | 0 | Category title (e.g. Cleats, Men's Footwear, Women's Apparel). |
| `department_id` | `Department Id` | INTEGER | 0 | Store department code (11 departments). |
| `department_name` | `Department Name` | TEXT | 0 | Department title (e.g. Fan Shop, Apparel, Golf, Footwear, Outdoors). |
| `customer_id` | `Customer Id` | INTEGER | 0 | Unique customer account identifier (20,652 unique customers). |
| `customer_fname` | `Customer Fname` | TEXT | 0 | Customer first name. |
| `customer_lname` | `Customer Lname` | TEXT | 8 (Imputed) | Customer last name (8 missing values imputed as "Unknown"). |
| `customer_segment` | `Customer Segment` | TEXT | 0 | Customer account tier: `Consumer`, `Corporate`, `Home Office`. |
| `customer_city` | `Customer City` | TEXT | 0 | Store registration city. |
| `customer_state` | `Customer State` | TEXT | 0 | Store registration state. |
| `customer_country` | `Customer Country` | TEXT | 0 | Store registration country. |
| `customer_zipcode` | `Customer Zipcode` | INTEGER | 3 (Imputed) | Customer postal code (3 missing values filled with 0). |
| `store_latitude` | `Latitude` | REAL | 0 | Store geolocation latitude coordinate. |
| `store_longitude` | `Longitude` | REAL | 0 | Store geolocation longitude coordinate. |
| `market` | `Market` | TEXT | 0 | Global delivery market: `Europe`, `LATAM`, `Pacific Asia`, `USCA`, `Africa`. |
| `order_region` | `Order Region` | TEXT | 0 | Continental sub-region (23 regions). |
| `order_country` | `Order Country` | TEXT | 0 | Destination country for the package (164 countries). |
| `order_state` | `Order State` | TEXT | 0 | Destination state / administrative area. |
| `order_city` | `Order City` | TEXT | 0 | Destination city. |
| `order_zipcode` | `Order Zipcode` | INTEGER | 155,679 (Imputed) | Destination postal code (86.2% missing in source, filled with 0). |

---

## 3. Derived Analytical Features

| Column Name | Mathematical Formula | Purpose |
| :--- | :--- | :--- |
| `shipping_delay_days` | `days_shipping_real - days_shipping_scheduled` | Measures exact days overdue (+ values) or early (- values). |
| `is_delayed` | `1 if shipping_delay_days > 0 else 0` | Binary indicator for delivery SLA breach. |
| `order_year` | `YEAR(order_date)` | Temporal slicing (2015, 2016, 2017, 2018). |
| `order_month` | `MONTH(order_date)` | Calendar seasonality index (1 to 12). |
| `order_year_month` | `FORMAT(order_date, 'YYYY-MM')` | Monthly trend continuity tracking (37 months). |
| `order_day_of_week` | `DAYNAME(order_date)` | Day-of-week order velocity analysis. |
| `is_negative_profit` | `1 if order_profit_per_order < 0 else 0` | Identifies commercial margin loss leakage (33,784 items). |
| `is_canceled` | `1 if delivery_status = 'Shipping canceled' else 0` | Flags abandoned or canceled shipments (7,754 items). |
| `fulfillment_result` | Categorical mapping | `Late`, `On-Time`, `Early`, `Canceled`. |

---

## 4. Extension Layer Schema (`data/extension_supplier_inventory.csv`)

| Extension Field | Data Type | Formula / Origin | Supply Chain Definition |
| :--- | :--- | :--- | :--- |
| `supplier_id` | TEXT | Synthetic Key (`SUP-101`..`SUP-105`) | Documented supplier code. |
| `supplier_name` | TEXT | Partner Directory | Legal entity name of manufacturing supplier. |
| `supplier_country` | TEXT | Origin Sourcing | Geographic manufacturing location. |
| `supplier_lead_time_days` | INTEGER | Sourced Benchmark | Average inbound replenishment lead time (4 to 14 days). |
| `warehouse_id` | TEXT | Distribution Network | Assigned regional fulfillment center (`WH-US-EAST`, etc.). |
| `daily_avg_demand_units` | REAL | `SUM(order_item_quantity) / 1127` | Real daily velocity derived from core DataCo history. |
| `safety_stock_units` | INTEGER | $Z \times \sqrt{L \cdot \sigma_D^2 + D^2 \cdot \sigma_L^2}$ | Safety buffer sized for 95% service level ($Z=1.645$). |
| `reorder_point_units` | INTEGER | $(D \times L) + SS$ | Inventory threshold triggering automated PO replenishment. |
| `economic_order_quantity_units`| INTEGER | $\sqrt{2 \cdot D_{\text{annual}} \cdot S / H}$ | Optimal batch order quantity balancing order & holding cost. |
| `current_stock_on_hand_units` | INTEGER | Simulated Snapshot | Physical unit inventory in distribution center. |
| `stockout_risk_status` | TEXT | Condition Check | `CRITICAL_REORDER` (stock $\le$ ROP), `HEALTHY`, `OVERSTOCKED`. |
| `benchmark_freight_cost_est_per_unit`| REAL | Weight/Value Proxy | Analytical model for estimated carrier freight cost per unit. |
