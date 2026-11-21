"""
Tests for SupplyX EDA and Causal Insights Engine
"""

from pathlib import Path
import pytest
from src.eda import run_eda


@pytest.fixture(scope="session")
def eda_results():
    """Execute EDA and cache results."""
    return run_eda("data/cleaned_supply_chain.csv", "reports/figures")


def test_eda_figures_created(eda_results):
    """Verify that all 5 publication-ready charts are generated and non-empty."""
    figures = eda_results["figures_generated"]
    assert len(figures) == 5
    for fig_path in figures:
        p = Path(fig_path)
        assert p.exists(), f"Missing figure: {fig_path}"
        assert p.stat().st_size > 10_000, f"Figure too small: {fig_path} ({p.stat().st_size} bytes)"


def test_first_class_sla_paradox(eda_results):
    """
    Verify the fundamental EDA insight:
    First class is physically faster than standard class, but has a higher late rate
    due to artificial 1-day scheduling promise.
    """
    first_days = eda_results["first_class_avg_real_days"]
    standard_days = eda_results["standard_class_avg_real_days"]
    first_late = eda_results["first_class_late_rate"]
    standard_late = eda_results["standard_class_late_rate"]

    # Physical speed verification
    assert first_days < standard_days
    assert first_days <= 2.2
    assert standard_days >= 3.9

    # Paradoxical late rate verification
    assert first_late > standard_late
    assert first_late > 0.90
    assert standard_late < 0.45
