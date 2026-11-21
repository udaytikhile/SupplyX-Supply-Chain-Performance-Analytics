# SupplyX KPI Dictionary & Column Mapping Guide
*Designed for executives, logistics operators, and non-technical stakeholders.*

---

## Executive Summary: How to Read Supply Chain Performance

In supply chain management, performance hinges on three dimensions:
1. **Fulfillment Reliability**: Did customers receive their packages by the promised date?
2. **Speed & SLA Adherence**: How long did transit take compared to our schedule?
3. **Financial Health**: Are orders generating sustainable profit after discounts?

---

## KPI Master Table & Schema Mapping

| Plain-English Metric | Business Meaning & Why It Matters | Underlying Dataset Column(s) | Mathematical Formula | DataCo Baseline Value | Target / Benchmark |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Order Count** | Total distinct customer purchase transactions. | `order_id` | `COUNT(DISTINCT order_id)` | **65,752 orders** | Growth Metric |
| **Total Order Items** | Total individual line items packed and shipped. | `order_item_id` | `COUNT(order_item_id)` | **180,519 items** | Operational Load |
| **Units Shipped** | Physical product unit volume moved through network. | `order_item_quantity` | `SUM(order_item_quantity)` | **384,079 units** | Capacity Metric |
| **Late Delivery Rate** | Percentage of orders that failed to arrive by scheduled date. | `late_delivery_risk`, `delivery_status` | `SUM(late_delivery_risk) / COUNT(*)` | **54.83%** (57.29% of non-canceled) | < 10.0% (🔴 Severe SLA issue) |
| **On-Time Delivery Rate** | Percentage of orders delivered exactly on schedule or ahead of schedule. | `delivery_status` | `COUNT(status IN ('Shipping on time', 'Advance shipping')) / COUNT(*)` | **40.88%** | > 90.0% (🔴 Needs carrier revamp) |
| **Cancellation Rate** | Percentage of shipments canceled prior to final fulfillment. | `delivery_status` | `COUNT(status = 'Shipping canceled') / COUNT(*)` | **4.30%** (7,754 orders) | < 2.0% (⚠️ Monitor lost sales) |
| **Average Transit Days** | Average calendar days taken from order placement to customer delivery. | `days_shipping_real` | `AVG(days_shipping_real)` | **3.50 days** | Target: ≤ 3.0 days |
| **Scheduled Transit Days** | Average days promised to the customer during checkout. | `days_shipping_scheduled` | `AVG(days_shipping_scheduled)` | **2.93 days** | Operating SLA |
| **SLA Delay Gap** | Average delay beyond promised delivery window. | `days_shipping_real`, `days_shipping_scheduled` | `AVG(real - scheduled)` | **+0.57 days delay** | Target: ≤ 0.0 days |
| **Gross Sales** | Catalog revenue before customer discounts. | `sales`, `product_price`, `order_item_quantity` | `SUM(sales) = SUM(price * qty)` | **\$36,784,735** | Topline Demand |
| **Customer Discounts** | Total markdown promotions absorbed by the company. | `order_item_discount` | `SUM(order_item_discount)` | **\$3,730,378** (10.1% discount) | Margin Protection |
| **Net Revenue** | Actual cash collected from customers. | `order_item_total` | `SUM(order_item_total) = Gross - Discount` | **\$33,054,402** | Net Sales |
| **Net Operating Profit** | Earnings retained after cost of goods sold. | `order_profit_per_order` | `SUM(order_profit_per_order)` | **\$3,966,903** | Bottom Line |
| **Operating Profit Margin** | Percentage of net revenue converted to operating profit. | `order_profit_per_order`, `order_item_total` | `SUM(profit) / SUM(net_sales)` | **12.00%** | > 12.0% (🟢 Healthy) |
| **Loss-Making Orders Rate** | Share of fulfilled order lines that generated negative profit. | `order_profit_per_order` | `COUNT(profit < 0) / COUNT(*)` | **18.71%** (33,784 lines) | < 5.0% (🔴 Deep discount leak) |
| **Shipping / Freight Cost** | Direct carrier freight expenses. | **ABSENT** | **UNAVAILABLE IN CORE DATASET** | **N/A (Disclosed Limitation)** | Requires carrier billing system |

---

## Critical Data Limitation & Non-Fabrication Disclosures

1. **Shipping / Freight Cost is Unavailable**:
   - The DataCo dataset contains `days_shipping_real`, `days_shipping_scheduled`, and `shipping_mode`, but contains **no column representing carrier shipping fees, freight billing, fuel surcharges, or dimensional weight costs**.
   - Rather than fabricating synthetic freight numbers that would mislead executive leadership, SupplyX reports shipping costs as **"Unavailable in Core Dataset"**.
   - An estimated mode-based cost benchmark is provided strictly in the Milestone 7 extension layer for exploratory modeling.

2. **Supplier Lead Times & On-Hand Warehouse Stock are Unavailable**:
   - `Product Status` is invariant (value `0` across all 180,519 rows).
   - Inbound replenishment lead times, supplier identifiers, and warehouse bin capacities are absent.
   - Any reorder point or safety stock modeling is documented as an **Extension Model** in Milestone 7.

---

## Actionable Takeaways for Non-Technical Leaders

1. **The Core Bottleneck**: A 54.8% late delivery rate does not mean delivery operations are failing completely; real shipping duration averages 3.5 days. The root cause is **unrealistic promise schedules**: First Class is scheduled for 1 day but takes 2–4 days, while Same Day is scheduled for 0 days.
2. **Profit Leakage**: 18.7% of all order lines lose money. This is directly driven by discount promotions exceeding 20% on low-margin sporting goods items.
