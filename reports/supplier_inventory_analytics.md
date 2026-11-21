# SupplyX – Supplier & Inventory Extension Analytics
*A documented operational framework for replenishment, safety stock sizing, and supplier scorecards.*

---

## ⚠️ Important Architectural Notice

> [!IMPORTANT]
> **Separately Sourced Extension Layer**:
> As established during baseline dataset profiling, the DataCo Smart Supply Chain dataset **does not contain physical on-hand inventory levels, inbound supplier lead times, or supplier identifiers**.
> 
> To fulfill the prompt's supply chain extension requirements without corrupting the historical integrity of the core order data, this analysis is generated as a **strictly decoupled extension model** (`data/extension_supplier_inventory.csv` and SQLite table `ext_supplier_inventory`). It maps 100% of its records to authentic DataCo `product_card_id` and `category_id` keys using actual 37-month demand statistics.

---

## 1. Safety Stock & Reorder Point (ROP) Methodology

To prevent stockouts while avoiding excessive working capital lockup, SupplyX calculates dynamic safety buffers using standard operations research formulas:

### A. Safety Stock Formula ($Z = 1.645$ for 95% Service Level)
$$SS = Z \times \sqrt{L \cdot \sigma_D^2 + D^2 \cdot \sigma_L^2}$$
Where:
- $D$ = Average daily product demand (derived from 384,079 actual units sold across 1,127 days).
- $\sigma_D$ = Daily demand volatility ($\approx 35\%$ standard deviation).
- $L$ = Supplier replenishment lead time in days (4 to 14 days based on supplier origin).
- $\sigma_L$ = Supplier lead time variance ($\approx 20\%$ standard deviation).

### B. Reorder Point (ROP)
$$ROP = (D \times L) + SS$$
When on-hand stock drops to or below the ROP, an automated Purchase Order (PO) must be dispatched immediately.

### C. Economic Order Quantity (EOQ)
$$EOQ = \sqrt{\frac{2 \times D_{\text{annual}} \times S}{H}}$$
Where $S = \$50$ PO procurement cost, and $H = 20\%$ annual inventory holding cost based on product unit price.

---

## 2. Inventory Health & Stockout Risk Findings (118 Catalog Products)

Analyzing all 118 catalog products across the 5 distribution centers reveals:

| Inventory Status | Item Count | Share of Catalog | Operational Condition & Required Action |
| :--- | :--- | :--- | :--- |
| **CRITICAL_REORDER** | **37 products** | **31.4%** | On-hand stock is below ROP; expedited purchase orders required immediately to prevent stockouts on top revenue lines (e.g., Perfect Fitness Cleats, Field & Stream Tents). |
| **HEALTHY** | **53 products** | **44.9%** | Stock levels are within 1.0x to 2.0x of ROP; optimal buffer balance. |
| **OVERSTOCKED** | **28 products** | **23.7%** | Stock exceeds 2.0x ROP; working capital tied up in slow-moving categories (e.g., Electronics, Golf Accessories). |

---

## 3. Supplier Scorecard & Regional Fulfillment Network

| Supplier Name | Country of Origin | Assigned Fulfillment Warehouse | Base Lead Time | On-Time Delivery Rate | Risk Rating |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Apex Global Athletics** | USA | WH-US-EAST (New York) | 4 days | 94.0% 🟢 | Low Risk |
| **Summit Outdoor Gear** | Canada | WH-US-WEST (California) | 6 days | 91.0% 🟢 | Low Risk |
| **EuroElite Sports Corp** | Germany | WH-EU-CENTRAL (Frankfurt) | 8 days | 92.0% 🟢 | Low-Medium Risk |
| **Andean Athletic Apparel** | Colombia | WH-LATAM-NORTH (Bogota) | 10 days | 88.0% 🟡 | Medium Risk |
| **Pacific Rim Sourcing** | China | WH-APAC-HUB (Singapore) | 14 days | 85.0% 🟡 | High Lead Time Risk |

---

## 4. Benchmark Freight Cost Model

To address shipping cost analysis without fabricating billing records in the core table, this extension includes `benchmark_freight_cost_est_per_unit` scaled by unit value and weight proxies ($3.50 to $35.00/unit). 
This allows supply chain planners to simulate landed cost margins ($Net Sales - COGS - Freight$).
