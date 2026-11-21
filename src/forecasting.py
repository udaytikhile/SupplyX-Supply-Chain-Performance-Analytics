"""
SupplyX - Time-Series Demand Forecasting Engine
Evaluates daily supply chain order demand using a chronological holdout split,
comparing a 7-day seasonal rolling baseline against a regularized lag-feature ML model.
"""

import json
from pathlib import Path
from typing import Dict, Any, Tuple
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error


def build_daily_demand_series(clean_csv: str = "data/cleaned_supply_chain.csv") -> pd.DataFrame:
    """Aggregates line items into a continuous daily demand time series."""
    df = pd.read_csv(clean_csv, low_memory=False)
    df["order_date"] = pd.to_datetime(df["order_date"])

    # Aggregate daily demand
    daily = df.groupby(df["order_date"].dt.floor("D")).agg({
        "order_item_quantity": "sum",
        "order_item_total": "sum",
        "order_id": "nunique"
    }).reset_index()

    daily = daily.rename(columns={
        "order_date": "date",
        "order_item_quantity": "daily_units",
        "order_item_total": "daily_revenue",
        "order_id": "daily_orders"
    })

    # Reindex to ensure continuous calendar without missing dates
    daily = daily.set_index("date").asfreq("D", fill_value=0).reset_index()
    return daily


def create_forecasting_features(daily: pd.DataFrame) -> pd.DataFrame:
    """Generates lag features, rolling windows, and calendar indicators."""
    df = daily.copy()

    # Target: daily unit demand
    y_col = "daily_units"

    # Lags
    for lag in [1, 2, 3, 7, 14, 21, 28]:
        df[f"lag_{lag}"] = df[y_col].shift(lag)

    # Rolling window statistics (lagged by 1 to prevent leakage)
    df["rolling_mean_7"] = df[y_col].shift(1).rolling(window=7).mean()
    df["rolling_mean_14"] = df[y_col].shift(1).rolling(window=14).mean()
    df["rolling_mean_28"] = df[y_col].shift(1).rolling(window=28).mean()
    df["rolling_std_7"] = df[y_col].shift(1).rolling(window=7).std()

    # Calendar features
    df["day_of_week"] = df["date"].dt.day_of_week
    df["day_of_month"] = df["date"].dt.day
    df["month"] = df["date"].dt.month
    df["is_weekend"] = (df["day_of_week"] >= 5).astype(int)

    # Time trend index
    df["time_idx"] = np.arange(len(df))

    # Drop warm-up rows containing NaN from 28-day lags
    df = df.dropna().reset_index(drop=True)
    return df


def run_forecasting_experiment(
    clean_csv: str = "data/cleaned_supply_chain.csv",
    split_date: str = "2017-10-01",
    out_dir: str = "reports",
) -> Dict[str, Any]:
    """Runs train-test evaluation comparing baseline vs ML model."""
    daily = build_daily_demand_series(clean_csv)
    featured = create_forecasting_features(daily)

    # Chronological Split
    split_dt = pd.to_datetime(split_date)
    train_mask = featured["date"] < split_dt
    test_mask = featured["date"] >= split_dt

    train_df = featured[train_mask].copy()
    test_df = featured[test_mask].copy()

    feature_cols = [
        "lag_1", "lag_2", "lag_3", "lag_7", "lag_14", "lag_21", "lag_28",
        "rolling_mean_7", "rolling_mean_14", "rolling_mean_28", "rolling_std_7",
        "day_of_week", "day_of_month", "month", "is_weekend", "time_idx"
    ]

    X_train = train_df[feature_cols]
    y_train = train_df["daily_units"]
    X_test = test_df[feature_cols]
    y_test = test_df["daily_units"]

    # 1. Baseline Model: 7-day Seasonal / Rolling Lag
    baseline_preds = test_df["lag_7"].values

    # 2. Predictive Model: Ridge Regularized Regression
    model = Ridge(alpha=10.0)
    model.fit(X_train, y_train)
    ml_preds = model.predict(X_test)
    ml_preds = np.maximum(ml_preds, 0)  # Demand cannot be negative

    # Evaluate metrics
    def calc_metrics(actual, pred):
        mae = float(mean_absolute_error(actual, pred))
        rmse = float(np.sqrt(mean_squared_error(actual, pred)))
        # Avoid division by zero
        non_zero = actual > 0
        mape = float(np.mean(np.abs((actual[non_zero] - pred[non_zero]) / actual[non_zero])) * 100)
        return {"mae": round(mae, 2), "rmse": round(rmse, 2), "mape_pct": round(mape, 2)}

    base_metrics = calc_metrics(y_test.values, baseline_preds)
    ml_metrics = calc_metrics(y_test.values, ml_preds)

    # Save predictions dataframe
    results_df = pd.DataFrame({
        "date": test_df["date"],
        "actual_demand": y_test.values,
        "baseline_prediction": baseline_preds,
        "ml_model_prediction": np.round(ml_preds, 1),
    })

    out_path = Path(out_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    results_csv = out_path / "forecast_predictions.csv"
    results_df.to_csv(results_csv, index=False)

    # Generate Evaluation Chart
    plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")
    fig, ax = plt.subplots(figsize=(10, 4.8), dpi=150)

    # Plot last 60 days of train + test
    plot_train = train_df.tail(60)
    ax.plot(plot_train["date"], plot_train["daily_units"], color="#94A3B8", label="Historical Demand (Pre-Split)", linewidth=1.2)
    ax.plot(test_df["date"], y_test, color="#0F172A", label="Actual Test Demand", linewidth=1.8)
    ax.plot(test_df["date"], baseline_preds, color="#F59E0B", linestyle="--", label=f"7-Day Baseline (MAE: {base_metrics['mae']})", linewidth=1.3)
    ax.plot(test_df["date"], ml_preds, color="#2563EB", label=f"Ridge Model (MAE: {ml_metrics['mae']})", linewidth=1.8)

    ax.axvline(split_dt, color="#EF4444", linestyle=":", linewidth=1.5, label="Train / Test Split (Oct 2017)")
    ax.set_ylabel("Daily Units Demanded", fontweight="bold")
    ax.set_title("Figure 6: Daily Demand Forecasting — Actual vs Model on 123-Day Holdout", fontweight="bold", pad=12)
    ax.legend(loc="upper right", framealpha=0.9)

    fig_path = out_path / "figures" / "fig6_forecast_vs_actual.png"
    fig_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(fig_path)
    plt.close()

    summary = {
        "target_variable": "daily_units (Order Item Quantity)",
        "total_days_in_series": len(daily),
        "train_days": len(train_df),
        "test_days": len(test_df),
        "train_date_range": f"{train_df['date'].min().strftime('%Y-%m-%d')} to {train_df['date'].max().strftime('%Y-%m-%d')}",
        "test_date_range": f"{test_df['date'].min().strftime('%Y-%m-%d')} to {test_df['date'].max().strftime('%Y-%m-%d')}",
        "baseline_model": {
            "name": "7-Day Seasonal Lag Naive Baseline",
            "metrics": base_metrics
        },
        "ml_model": {
            "name": "Ridge Regularized Regression (Alpha=10.0)",
            "features_used": feature_cols,
            "metrics": ml_metrics
        },
        "artifacts": {
            "predictions_csv": str(results_csv),
            "figure_png": str(fig_path)
        }
    }

    eval_json = out_path / "forecast_evaluation.json"
    with open(eval_json, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    return summary


if __name__ == "__main__":
    res = run_forecasting_experiment()
    print("Forecasting Experiment Complete:")
    print(f"  Train: {res['train_date_range']} ({res['train_days']} days)")
    print(f"  Test:  {res['test_date_range']} ({res['test_days']} days)")
    print(f"  Baseline MAE: {res['baseline_model']['metrics']['mae']} | RMSE: {res['baseline_model']['metrics']['rmse']}")
    print(f"  ML Model MAE: {res['ml_model']['metrics']['mae']} | RMSE: {res['ml_model']['metrics']['rmse']}")
