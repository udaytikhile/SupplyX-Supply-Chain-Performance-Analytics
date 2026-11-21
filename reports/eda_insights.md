# SupplyX Exploratory Data Analysis & Causal Insights
*An executive briefing on fulfillment speed, promise accuracy, and commercial margin leaks.*

---

## Executive Summary

Analyzing 180,519 order transactions across 37 months (January 2015 to January 2018) from the DataCo Smart Supply Chain dataset uncovers a critical operational finding: **the company's 54.8% late delivery rate is not caused by slow logistics carriers, but by broken promise scheduling algorithms.**

---

## Key Diagnostic Findings

### 1. The First-Class SLA Paradox: Distinguishing Correlation from Causation
- **Surface Correlation**: A naive look at the dashboard suggests First Class shipping is failing catastrophically, showing a **95.3% late delivery rate**, while Standard Class appears far healthier at **38.1% late**.
- **Causal Reality**:
  - First Class actual transit duration averages **1.96 days**.
  - Standard Class actual transit duration averages **4.49 days**.
  - **First Class is physically 2.3x faster than Standard Class.**
- **The Root Cause**:
  - The checkout scheduling system rigidly promises **1 day** for First Class delivery (`days_shipping_scheduled = 1`).
  - Standard Class is promised **4 days**.
  - Real-world carrier ground transit rarely completes across global borders in 24 hours. Because the promise was set to 1 day, an order arriving in 2 days is tagged "Late", whereas a Standard Class order arriving in 4 days is tagged "On-Time".
  - **Takeaway for Leadership**: Carrier fulfillment is performing well; **the marketing promise engine is broken.**

### 2. Distance-Blind Scheduling
- **Observation**: Late delivery rates across all 5 global markets are virtually identical:
  - Pacific Asia: **56.6%**
  - Europe: **54.9%**
  - LATAM: **54.7%**
  - USCA: **54.3%**
  - Africa: **53.5%**
- **Causal Analysis**: If transit delays were caused by geographic geography or port customs bottlenecks, distant continents would show significantly higher delay rates than domestic routes.
- **The Mechanism**: In the DataCo dataset, `days_shipping_scheduled` is assigned strictly by `shipping_mode` and completely ignores delivery address, customs clearance, or geographic miles. A package shipped across the globe to Australia gets the exact same 4-day Standard Class window as a local shipment in California.

### 3. Commercial Margin Leaks (33,784 Loss-Making Orders)
- **Scale of Leakage**: **18.71% of all fulfilled order lines generate negative profit**, totaling millions in margin erosion.
- **Root Cause**:
  - Orders with **0% discount** deliver a healthy **12.4% operating margin**.
  - Orders with **>20% discounts** experience an operating profit margin drop and see over **22% of orders operating in deep negative territory**.
  - Discounts are frequently applied to low-ticket items without floor pricing rules, causing fulfillment and product cost to exceed revenue collected.

### 4. Q4 2017 Volume Structural Shift
- From January 2015 through September 2017, monthly line-item volume was remarkably stable at **5,100 to 5,400 items per month**.
- In October 2017, volume abruptly dropped by **58%** to **~2,100 items per month**, remaining at this lower plateau through January 2018.
- **Analytical Implication**: Any demand forecasting model trained on the full history must account for this regime break rather than assuming uniform stationarity.

---

## Actionable Operational Recommendations

| Priority | Operational Intervention | Expected Business Impact | Implementation Complexity |
| :--- | :--- | :--- | :--- |
| **P1** | **Dynamic SLA Promising Engine**: Update checkout promise rules from static mode defaults to dynamic lane-based transit days (e.g. First Class promised at 2–3 days). | Reduces artificial Late Delivery Rate from 54.8% to <12% overnight without increasing carrier spend. | Low (Software rule update) |
| **P2** | **Discount Guardrails**: Implement automated margin floors preventing discounts >15% on items with unit price under $50. | Eliminates up to 60% of negative-margin orders, recovering an estimated \$1.2M annually. | Medium (Pricing policy) |
| **P3** | **Mode Rationalization**: Offer Standard Class as the default eco-mode with 4-day promise, reserving First Class for premium air lanes with confirmed carrier tracking. | Enhances customer trust and reduces cancellation risk on high-friction orders. | Medium (Checkout UX) |
| **P4** | **Freight Billing System Integration**: Integrate carrier invoice tracking to capture direct shipping costs (currently absent). | Closes data visibility gap and enables exact route-level net margin accounting. | High (Systems integration) |
