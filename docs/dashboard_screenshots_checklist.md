# SupplyX Dashboard Visual & Screenshot Verification Checklist
*A QA guide for inspecting both the Power BI wireframe specifications and the standalone HTML dashboard.*

---

## 1. Global Header & Navigation Checkpoints

- [x] **Brand Title & Subtitle**: "SupplyX Executive Analytics" clearly visible with dataset metadata subtitle (180,519 Shipments | Jan 2015 – Jan 2018).
- [x] **System Status Badge**: Green "Network Health: Online" indicator confirming live verified schema.
- [x] **Navigation Bar**: 4 accessible tabs with active state indicator:
  - 1. Executive Overview
  - 2. Delivery & SLA Performance
  - 3. Demand & Revenue
  - 4. Exceptions & Disclosures
- [x] **"How to Read This Dashboard" Guide**: Top banner explaining color semantics (Green = Healthy, Red = Late SLA, Amber = Warning) and noting absent carrier freight costs.
- [x] **Interactive Slicers**: Functional dropdowns for Global Market (Europe, LATAM, Pacific Asia, USCA, Africa) and Shipping Mode (Standard, Second, First, Same Day) that dynamically update KPI cards.

---

## 2. Page 1: Executive Overview Checkpoints

- [x] **Card 1 (Customer Orders)**: Displays `65,752` with blue chip `180,519 Line Items` and subtitle `384,079 total units fulfilled`.
- [x] **Card 2 (Net Sales Revenue)**: Displays `$33.05M` with green chip `+$3.97M Profit` and subtitle `12.00% healthy operating margin`.
- [x] **Card 3 (Late Delivery Rate)**: Displays `54.83%` in crimson red with red badge `🔴 98,977 Breaches` and benchmark disclaimer `Target: <10% (Root cause: 1-day promise)`.
- [x] **Card 4 (Avg Shipping Speed)**: Displays `3.50 Days` with amber badge `⚠️ +0.57 Days Overdue` and subtitle `Promised checkout window: 2.93 Days`.
- [x] **Card 5 (Order Cancellation Rate)**: Displays `4.30%` with subtitle `$1.43M in lost gross sales`.
- [x] **Visual 1 (Market Bar Chart)**: Europe ($10.87M) and LATAM ($9.47M) shown as top commercial revenue markets.
- [x] **Visual 2 (Outcome Donut Chart)**: Visual share of Late (54.8%), Early (23.0%), On-Time (17.8%), and Canceled (4.3%).
- [x] **Visual 3 (Timeline Chart)**: Continuous 37-month timeline clearly showing the volume contraction in Q4 2017.

---

## 3. Page 2: Delivery & Shipping SLA Performance Checkpoints

- [x] **Diagnostic Alert Callout**: Plain-English banner explaining the First Class paradox (physically 2.0 days vs 1.0 day promise).
- [x] **Visual 1 (SLA Paradox Chart)**: Grouped bars comparing promised days vs actual days by shipping mode.
- [x] **Visual 2 (Delay Distribution Histogram)**: Clear histogram showing peak shipment overdue delay at +1 day overdue.
- [x] **Visual 3 (Shipping Mode Master Scorecard)**: Structured table listing all 4 modes, shipment counts, actual speed, delay gaps, and plain-English operational diagnoses.

---

## 4. Page 3: Commercial Demand & Product Trends Checkpoints

- [x] **Visual 1 (Department Margin Bar Chart)**: Top departments (Fan Shop, Apparel, Golf) with both revenue and profit bars.
- [x] **Visual 2 (Customer Segment Donut)**: Clean segment breakdown (Consumer: 52%, Corporate: 30%, Home Office: 18%).
- [x] **Visual 3 (Holdout Forecast Chart)**: Actual daily demand compared against the 7-day seasonal baseline model across the 123-day holdout period.

---

## 5. Page 4: Exceptions & Problem Tracker Checkpoints

- [x] **Mandatory Freight Limitation Banner**: Prominent amber alert box explaining that direct carrier freight costs are not captured in source DataCo data and are strictly excluded from core metrics to avoid fabrication.
- [x] **Visual 1 (Discount Depth Chart)**: Bar chart showing profit margin collapsing from 12.4% down to single digits when discounts exceed 20%.
- [x] **Visual 2 (Exception Summary Table)**: 4-row matrix detailing loss-making lines (33,784), canceled shipments (7,754), First Class SLA breaches (26,513), and total late deliveries (98,977) with executive action plans.

---

## 6. How to Open and Review the Live Dashboard

Open the standalone dashboard file directly in your default browser:
```powershell
Start-Process "reports/dashboard.html"
```
Or open via browser URL:
`file:///c:/Users/udayt/Downloads/archive%20(1)/reports/dashboard.html`
