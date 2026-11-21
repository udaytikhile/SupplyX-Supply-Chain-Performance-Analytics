# SupplyX Time-Series Demand Forecasting Evaluation
*Rigorous chronological holdout validation for daily order fulfillment volume.*

---

## Executive Overview

Accurate daily demand forecasting enables warehouse operations to right-size packing staff, carrier truckload commitments, and inventory buffer allocations. SupplyX implements a strict **chronological train-test experiment** using actual physical demand (`daily_units` shipped) across all 1,127 days in the DataCo dataset.

---

## Experiment Design & Integrity Guardrails

1. **Adequate Date Coverage**: 1,127 continuous daily timestamps from January 1, 2015 to January 31, 2018 (37 full months with zero missing calendar dates).
2. **Target Variable**: `daily_units` — total physical product units demanded per day.
3. **No Data Leakage (Chronological Holdout)**:
   - **Training Period**: January 29, 2015 to September 30, 2017 (**976 days**).
   - **Holdout Test Period**: October 1, 2017 to January 31, 2018 (**123 days**).
   - Standard random K-Fold splits are strictly forbidden for time series to avoid future data leaking into the past.
4. **Structural Shift Consideration**: The holdout period tests the model during the lower-volume regime observed starting October 2017.

---

## Model Comparison & Benchmark Results

| Model | Architecture & Inputs | Mean Absolute Error (MAE) | Root Mean Squared Error (RMSE) | Mean Absolute % Error (MAPE) | Key Strengths & Operational Suitability |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **7-Day Seasonal Baseline** | Naive Seasonal Lag ($y_{t-7}$) | **16.78 units** | **63.87 units** | **7.74%** | **Winner**: Quickly adapts within 7 days to sudden structural breaks; superior for operational dispatch. |
| **Ridge Regression** | L2 Regularization, lags 1..28, rolling stats (7/14/28), calendar flags | **175.55 units** | **178.77 units** | **123.63%** | Struggles initially after an unannounced regime drop because pre-October weights anchored to high historical mean. |

### Operational Insight: Why the Local Baseline Outperformed Global Regression
In October 2017, the DataCo business suffered an abrupt 58% volume contraction (from ~370 units/day to ~150 units/day). 
- The **7-Day Seasonal Baseline** absorbed this regime shift after just 7 days, achieving an outstanding **7.74% MAPE**.
- The global **Ridge Regression Model** trained on 33 months of high volume took significantly longer to recalibrate its intercept.
- **Key Supply Chain Takeaway**: In dynamic supply chain networks subject to structural shocks (e.g. supplier contract loss, platform migrations), agile rolling seasonal baselines should be retained as an active operational safeguard alongside machine learning models.

---

## How Operations Planners Should Use This Model

1. **Shift Scheduling**: Forecasted daily unit demand provides warehouse supervisors a 7-day forward packing workload estimate.
2. **Carrier Capacity Reservations**: Booking line-haul trucks 3–5 days ahead based on model projections avoids last-minute spot freight premiums.
3. **Buffer Sizing**: When actual daily orders deviate from forecast by more than 2x RMSE, trigger an operational alert to review promotional surges or technical feed interruptions.
