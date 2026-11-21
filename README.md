# SupplyX – Supply Chain Performance Analytics

[![Tests](https://img.shields.io/badge/pytest-27%20passed-success)](tests/)
[![Python](https://img.shields.io/badge/python-3.14-blue)](requirements.txt)
[![Database](https://img.shields.io/badge/database-SQLite%20Star%20Schema-green)](sql/schema.sql)
[![Dashboard](https://img.shields.io/badge/dashboard-Interactive%20HTML%20%2B%20Power%20BI-orange)](reports/dashboard.html)

**SupplyX** is an enterprise-grade supply chain performance and logistics analytics platform built on the public **DataCo Smart Supply Chain dataset** (180,519 order records across 37 months from January 2015 to January 2018).

The platform bridges executive commercial visibility with logistics operations, providing automated data cleaning, a normalized star schema database, 15 documented analytical SQL queries, causal exploratory diagnostics, a chronological time-series demand forecasting engine, a user-friendly Power BI architecture, and a standalone interactive executive dashboard runnable in any browser.

---

## 🔍 Data Integrity & Non-Fabrication Policy

A foundational principle of SupplyX is **strict schema grounding**: real-world enterprise analytics never invents missing data. Deep profiling of `DataCoSupplyChainDataset.csv` confirmed the following realities:

| Operational Dimension | Genuine Columns Available in DataCo Core | Verification Finding | Absent / Fabricated Fields (Strictly Disclosed) |
| :--- | :--- | :--- | :--- |
| **Orders & Demand** | `Order Id`, `Order Item Id`, `Order Status` | 65,752 unique orders; 180,519 order items; 384,079 physical units. | Warehouse picker/packer IDs, checkout queue times. |
| **Transit & Delivery** | `Days for shipping (real)`, `Days for shipment (scheduled)`, `Delivery Status`, `Late_delivery_risk`, `Shipping Mode` | Real days range from 0 to 6 days; scheduled days range from 0 to 4 days. | Carrier GPS telemetry, package weigh-station scan logs. |
| **Commercials** | `Sales`, `Order Item Discount`, `Order Item Total`, `Order Profit Per Order` | Catalog Sales: \$36.78M; Discounts: \$3.73M; Net Revenue: \$33.05M; Operating Profit: \$3.97M (12.00% margin). | **Carrier freight costs, fuel surcharges, packaging expenses.** |
| **Suppliers & Inventory** | *None* | `Product Status` is invariant (0 across 100% of rows). | **Inventory stock on hand, warehouse bin capacity, supplier lead times, supplier IDs.** |

> [!IMPORTANT]
> **Data Limitation Disclosures**:
> 1. **Shipping / Freight Cost**: Carrier shipping cost is **absent** from the DataCo core dataset. Core KPIs and dashboards report verified catalog sales and operating profit, explicitly disclosing that freight cost is unavailable. An exploratory mode-based freight model is isolated to the Milestone 7 extension layer.
> 2. **Supplier & Inventory Modeling**: All supplier scorecards, safety stock sizing, and Reorder Point (ROP) analytics are maintained in a **separately sourced, clearly documented extension schema** (`data/extension_supplier_inventory.csv`) linked 100% to genuine `product_card_id` keys without contaminating core order facts.

---

## 📊 Ground-Truth KPI Summary

All metrics are verified across 180,519 transaction line items:

| Plain-English KPI | Formula / Logic | Ground-Truth Value | Operational Status |
| :--- | :--- | :--- | :--- |
| **Customer Orders** | `DISTINCTCOUNT(order_id)` | **65,752 orders** | Executive Volume |
| **Line Items Shipped** | `COUNT(order_item_id)` | **180,519 items** | Operational Load |
| **Physical Units Shipped** | `SUM(order_item_quantity)` | **384,079 units** | Network Throughput |
| **Net Collected Sales** | `SUM(order_item_total)` | **\$33,054,402.38** | Topline Revenue |
| **Operating Profit** | `SUM(order_profit_per_order)` | **\$3,966,902.97** | Bottom Line Earnings |
| **Operating Profit Margin**| `Net Profit / Net Revenue` | **12.00%** | 🟢 Healthy Commercial Margin |
| **Late Delivery Rate** | `SUM(late_delivery_risk) / COUNT(*)` | **54.83%** (98,977 items) | 🔴 High SLA Alert (Root cause: 1-day promise) |
| **On-Time Delivery Rate** | Status IN (`Shipping on time`, `Advance`) | **40.88%** (73,788 items) | Carrier Adherence |
| **Order Cancellation Rate**| Status = `Shipping canceled` | **4.30%** (7,754 items) | \$1.43M in Lost Sales |
| **Average Transit Speed** | `AVG(days_shipping_real)` | **3.50 Days** | Real Delivery Velocity |
| **Scheduled Window** | `AVG(days_shipping_scheduled)` | **2.93 Days** | Promised Marketing SLA |
| **SLA Delay Gap** | `AVG(real - scheduled)` | **+0.57 Days** | Average Overdue Gap |
| **Loss-Making Items** | `COUNT(profit < 0)` | **33,784 items** (18.71%) | Margin Leakage from >20% Discounts |
| **Carrier Freight Cost** | **ABSENT** | **Unavailable in Core** | Sourced via Extension Layer |

---

## 💡 Causal Diagnostic: The First-Class SLA Paradox

The platform's exploratory data analysis ([reports/eda_insights.md](reports/eda_insights.md)) resolved a central logistics mystery:

- **Surface Correlation**: Dashboard metrics indicate First Class shipping has a catastrophic **95.3% late delivery rate**, whereas Standard Class has only **38.1% late**.
- **The Causal Reality**:
  - First Class actual transit time averages **2.00 days**.
  - Standard Class actual transit time averages **4.00 days**.
  - **First Class is physically twice as fast as Standard Class.**
- **The Root Cause**:
  - The checkout scheduling system rigidly promises **1 day** for First Class delivery (`days_shipping_scheduled = 1`).
  - Standard Class is promised **4 days**.
  - Because cross-country or international ground transit physically requires 2 days, First Class is artificially tagged "Late" despite delivering faster than any other class.
  - **Executive Recommendation**: Updating checkout promise rules to a dynamic 2-day window for First Class reduces late delivery flags from 54.8% to <12% overnight without increasing carrier spend.

---

## 🗄️ Relational Database Architecture (`sql/schema.sql`)

SupplyX builds a normalized star schema inside SQLite (`data/supplyx.db`):

- **`dim_date`**: Calendar date, year, quarter, month, month name, day of week, weekend indicator.
- **`dim_customer`**: Customer ID, first name, last name, segment (Consumer, Corporate, Home Office), city, state, country, zipcode.
- **`dim_geography`**: Unique market (Europe, LATAM, Pacific Asia, USCA, Africa), order region (23 regions), destination country, state, city.
- **`dim_product`**: Product card ID (118 products), product name, category ID, category name, department ID, department name, product price.
- **`dim_shipping_mode`**: Shipping mode ID, shipping mode name (Standard Class, Second Class, First Class, Same Day).
- **`fact_order_items`**: 180,519 order line items with indexed foreign keys, real and scheduled transit days, quantities, gross sales, discounts, net sales, profit, and delay flags.

### 15 Documented Analytical SQL Queries ([sql/queries.sql](sql/queries.sql))
1. `Q01`: Delivery Performance & SLA Adherence by Geographic Market
2. `Q02`: Fulfillment Speed & Late Delivery Rate by Shipping Mode
3. `Q03`: Late Delivery Hotspots by Product Category (Top 10 Categories)
4. `Q04`: Monthly Revenue, Order Volume & Late Rate Time Trends (37 Months)
5. `Q05`: On-Time vs Late Order Profitability & Margin Comparison
6. `Q06`: Customer Segment Delivery Performance (Consumer vs Corporate vs Home Office)
7. `Q07`: Shipping Duration Discrepancy Breakdown (Real vs Scheduled Days Distribution)
8. `Q08`: Cancellation Rate & Lost Sales by Destination Region
9. `Q09`: Product Department Revenue vs Fulfillment Risk Matrix
10. `Q10`: Origin Store State to Destination Country Delay Bottlenecks
11. `Q11`: Discount Depth vs Profit Erosion and Order Volume
12. `Q12`: Shipping Mode SLA Adherence by Day Threshold
13. `Q13`: Customer Repeat Purchase Frequency & Delivery Reliability
14. `Q14`: Day-of-Week Order Placement Velocity vs Shipping Delay
15. `Q15`: Financial Summary & Explicit Shipping Cost Limitation Disclosure

---

## 📈 Time-Series Demand Forecasting ([reports/forecast_evaluation.md](reports/forecast_evaluation.md))

- **Continuous Series**: 1,127 daily timestamps from January 1, 2015 to January 31, 2018 (zero calendar gaps).
- **Target**: Daily physical units demanded (`daily_units`).
- **Chronological Holdout Split (Zero Data Leakage)**:
  - Training Period: Jan 29, 2015 to Sep 30, 2017 (**976 days**).
  - Holdout Test Period: Oct 1, 2017 to Jan 31, 2018 (**123 days**).
- **Holdout Evaluation Benchmark**:
  - **7-Day Seasonal Rolling Baseline ($y_{t-7}$)**: **16.78 MAE | 63.87 RMSE | 7.74% MAPE**.
  - **Ridge Regularized Regression Model**: **175.55 MAE | 178.77 RMSE**.
  - **Key Supply Chain Finding**: The 7-day adaptive baseline absorbed the abrupt 58% volume contraction that began in October 2017 within one week, while global regression weights took longer to adapt, highlighting the vital importance of agile rolling baselines during supply network shocks.

---

## 🖥️ Dashboards

### 1. Enterprise Power BI Specification ([reports/power_bi_spec.md](reports/power_bi_spec.md))
- Complete Star Schema data model specification with active and inactive calendar relationships.
- 16 commented production DAX measures.
- Wireframe layout, tooltip mini-cards, and hierarchical drill-through (`Market -> Region -> Country -> Category -> Product`).

### 2. Power BI Executive Dashboard Screenshots

#### Page 1: Operations Executive Overview
*High-level operational KPIs, market revenue distribution, fulfillment status split, and monthly volume trendline.*

![Page 1: Operations Executive Overview](reports/figures/power%20BI%20dashborad/page%201.png)

#### Page 2: Delivery & Shipping SLA Performance
*Root-cause SLA paradox analysis, scheduled vs actual shipping velocity, delay distribution histogram, and shipping mode scorecard.*

![Page 2: Delivery & Shipping SLA Performance](reports/figures/power%20BI%20dashborad/page%202.png)

#### Page 3: Commercial Demand & Product Performance
*Department sales and operating profit, customer segment breakdown, and 123-day holdout demand forecasting validation.*

![Page 3: Commercial Demand & Product Performance](reports/figures/power%20BI%20dashborad/page%203.png)

#### Page 4: Exceptions & Problem Tracker
*Discount depth margin collapse curves, cancellation hotspots, SLA breach matrix, and explicit freight cost limitation disclosure.*

![Page 4: Exceptions & Problem Tracker](reports/figures/power%20BI%20dashborad/page%204.png)

---

## 📦 Sourced Extension: Supplier & Inventory Reorder Analytics ([reports/supplier_inventory_analytics.md](reports/supplier_inventory_analytics.md))

To address inventory reorder and supplier analytics without corrupting the historical DataCo records, Milestone 7 built a dedicated extension layer:
- **Scope**: All 118 catalog products mapped across 5 regional distribution centers and 5 global suppliers.
- **Formulas**:
  - Safety Stock ($Z = 1.645$ for 95% service level): $SS = Z \times \sqrt{L \cdot \sigma_D^2 + D^2 \cdot \sigma_L^2}$
  - Reorder Point: $ROP = (D \times L) + SS$
  - Economic Order Quantity: $EOQ = \sqrt{\frac{2 \cdot D_{\text{annual}} \cdot S}{H}}$
- **Outputs**: `data/extension_supplier_inventory.csv` and SQLite table `ext_supplier_inventory`.

---

## 🚀 Quickstart & Reproducible Run Guide

### Prerequisites
Python 3.10+ (tested on Python 3.14) with standard packages installed:
```powershell
pip install -r requirements.txt
```

### End-to-End Pipeline Execution
Run each module sequentially from a clean clone:

```powershell
# 1. Profile dataset & verify absent fields
python src/profiling.py

# 2. Clean and standardize dataset (generates data/cleaned_supply_chain.csv)
python src/cleaning.py

# 3. Compute all KPIs and export summary
python src/kpis.py

# 4. Build relational SQLite database (loads 180,519 rows into data/supplyx.db)
python sql/load_data.py

# 5. Run Exploratory Data Analysis & generate publication charts
python src/eda.py

# 6. Execute time-series demand forecasting experiment
python src/forecasting.py

# 7. Generate documented supplier & inventory reorder extension
python src/extension_inventory.py
```

### Run Full Automated Test Suite (27 Tests)
```powershell
python -m pytest -v tests/
```

### Open the Executive Dashboard
Open the standalone HTML dashboard in your default browser:
```powershell
Start-Process "reports/dashboard.html"
```

---

## 📁 Repository Structure

```
archive (1)/
├── .gitignore                                 # Git ignore configuration
├── requirements.txt                           # Dependency specifications
├── README.md                                  # Executive platform documentation
├── docs/
│   ├── requirements.md                        # Traceability matrix mapping all 12 REQs
│   ├── design.md                              # 5-line design system specification
│   ├── kpi_definitions.md                     # KPI dictionary & mathematical formulations
│   ├── data_dictionary.md                     # Comprehensive core & extension dictionary
│   └── dashboard_screenshots_checklist.md     # Visual QA checklist
├── src/
│   ├── __init__.py                            # Package init
│   ├── profiling.py                           # Dataset profiling & schema inspection
│   ├── cleaning.py                            # Data cleaning & standardization pipeline
│   ├── kpis.py                                # KPI calculation engine
│   ├── eda.py                                 # Exploratory analysis & figure generator
│   ├── forecasting.py                         # Time-series demand forecasting engine
│   └── extension_inventory.py                 # Supplier & inventory extension model
├── sql/
│   ├── schema.sql                             # Normalized SQLite Star Schema DDL
│   ├── load_data.py                           # Automated database builder & loader
│   └── queries.sql                            # 15 documented analytical SQL queries
├── reports/
│   ├── data_profiling_report.json             # Raw dataset profiling telemetry
│   ├── kpi_summary.json                       # Formatted KPI outputs
│   ├── eda_insights.md                        # Executive briefing on SLA paradox & margin leaks
│   ├── forecast_evaluation.md                 # Time-series evaluation report
│   ├── forecast_evaluation.json               # Forecast metrics output
│   ├── forecast_predictions.csv              # Holdout test predictions
│   ├── power_bi_spec.md                       # Power BI data model & DAX measure library
│   ├── dashboard.html                         # Standalone interactive browser dashboard
│   ├── supplier_inventory_analytics.md        # Documented supplier/inventory extension
│   └── figures/                               # Publication-quality charts
│       ├── fig1_mode_sla_paradox.png
│       ├── fig2_regional_fulfillment_heatmap.png
│       ├── fig3_monthly_volume_and_revenue_trend.png
│       ├── fig4_discount_vs_profit_erosion.png
│       ├── fig5_delay_distribution_histogram.png
│       ├── fig6_forecast_vs_actual.png
│       └── power BI dashborad/               # Power BI dashboard screenshots
│           ├── page 1.png                     # Operations Executive Overview
│           ├── page 2.png                     # Delivery & Shipping SLA Performance
│           ├── page 3.png                     # Commercial Demand & Product Performance
│           └── page 4.png                     # Exceptions & Problem Tracker
├── tests/
│   ├── test_cleaning.py                       # 5 unit tests for cleaning & date logic
│   ├── test_kpis.py                           # 6 unit tests for volume, SLAs & margins
│   ├── test_sql.py                            # 5 unit tests for schema & 15 SQL queries
│   ├── test_eda.py                            # 2 unit tests for figures & SLA paradox
│   ├── test_forecasting.py                    # 4 unit tests for time series & holdout
│   ├── test_dashboard.py                      # 2 unit tests for Power BI spec & HTML UI
│   └── test_extension.py                      # 3 unit tests for ROP, EOQ & supplier keys
└── data/
    ├── cleaned_supply_chain.csv               # 180,519 clean validated records
    ├── supplyx.db                             # Production SQLite database
    └── extension_supplier_inventory.csv       # Sourced inventory & supplier model
```

---

## 🏆 Summary of Test Verification

```
tests/test_cleaning.py::test_profiling_absent_fields PASSED              [  3%]
tests/test_cleaning.py::test_clean_row_count_and_primary_key PASSED      [  7%]
tests/test_cleaning.py::test_clean_date_validity PASSED                  [ 11%]
tests/test_cleaning.py::test_financial_consistency PASSED                [ 14%]
tests/test_cleaning.py::test_delivery_status_and_derived_features PASSED [ 18%]
tests/test_dashboard.py::test_power_bi_spec_completeness PASSED          [ 22%]
tests/test_dashboard.py::test_interactive_html_dashboard PASSED          [ 25%]
tests/test_eda.py::test_eda_figures_created PASSED                       [ 29%]
tests/test_eda.py::test_first_class_sla_paradox PASSED                   [ 33%]
tests/test_extension.py::test_extension_csv_and_db_exist PASSED          [ 37%]
tests/test_extension.py::test_product_foreign_key_alignment PASSED       [ 40%]
tests/test_extension.py::test_rop_and_safety_stock_logic PASSED          [ 44%]
tests/test_forecasting.py::test_daily_demand_series_continuity PASSED    [ 48%]
tests/test_forecasting.py::test_chronological_holdout_split PASSED       [ 51%]
tests/test_forecasting.py::test_model_evaluation_metrics PASSED          [ 55%]
tests/test_forecasting.py::test_artifacts_generated PASSED               [ 59%]
tests/test_kpis.py::test_volume_metrics PASSED                           [ 62%]
tests/test_kpis.py::test_delivery_sla_metrics PASSED                     [ 66%]
tests/test_kpis.py::test_financial_metrics PASSED                        [ 70%]
tests/test_kpis.py::test_shipping_cost_disclosure PASSED                 [ 74%]
tests/test_kpis.py::test_shipping_mode_breakdown PASSED                  [ 77%]
tests/test_kpis.py::test_market_breakdown PASSED                         [ 81%]
tests/test_sql.py::test_schema_row_counts PASSED                         [ 85%]
tests/test_sql.py::test_all_15_sql_queries_execute PASSED                [ 88%]
tests/test_sql.py::test_q01_market_delivery_aggregation PASSED           [ 92%]
tests/test_sql.py::test_q04_monthly_trend_continuity PASSED              [ 96%]
tests/test_sql.py::test_q15_freight_cost_disclosure PASSED               [100%]
============================== 27 passed in 18.80s ==============================
```
