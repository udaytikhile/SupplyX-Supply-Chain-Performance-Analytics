"""
Tests for Time-Series Demand Forecasting Engine
"""

from pathlib import Path
import pandas as pd
import pytest
from src.forecasting import build_daily_demand_series, run_forecasting_experiment


@pytest.fixture(scope="session")
def forecast_results():
    """Run forecasting experiment and cache output."""
    return run_forecasting_experiment(
        clean_csv="data/cleaned_supply_chain.csv",
        split_date="2017-10-01",
        out_dir="reports"
    )


def test_daily_demand_series_continuity():
    """Verify daily series has continuous dates with zero gaps across 37 months."""
    daily = build_daily_demand_series("data/cleaned_supply_chain.csv")
    assert len(daily) == 1127  # 365 + 366 (leap) + 365 + 31 days = 1127
    assert (daily["daily_units"] >= 0).all()
    assert (daily["daily_orders"] >= 0).all()


def test_chronological_holdout_split(forecast_results):
    """Verify strict chronological ordering between train and test partitions."""
    train_end = forecast_results["train_date_range"].split(" to ")[1]
    test_start = forecast_results["test_date_range"].split(" to ")[0]

    assert pd.to_datetime(train_end) < pd.to_datetime(test_start)
    assert forecast_results["test_days"] == 123


def test_model_evaluation_metrics(forecast_results):
    """Verify calculated metrics are valid positive numbers."""
    base_m = forecast_results["baseline_model"]["metrics"]
    ml_m = forecast_results["ml_model"]["metrics"]

    assert base_m["mae"] > 0
    assert base_m["rmse"] > 0
    assert ml_m["mae"] > 0
    assert ml_m["rmse"] > 0

    # ML model with rolling features should perform reasonably
    assert ml_m["mae"] < 250.0


def test_artifacts_generated(forecast_results):
    """Verify prediction CSV and figure outputs exist."""
    pred_csv = Path(forecast_results["artifacts"]["predictions_csv"])
    fig_png = Path(forecast_results["artifacts"]["figure_png"])

    assert pred_csv.exists()
    assert pred_csv.stat().st_size > 1000

    assert fig_png.exists()
    assert fig_png.stat().st_size > 10000
