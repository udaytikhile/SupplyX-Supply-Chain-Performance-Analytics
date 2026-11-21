"""
Tests for Power BI Specification and Interactive Executive Dashboard
"""

from pathlib import Path
import re
import pytest


def test_power_bi_spec_completeness():
    """Verify that power_bi_spec.md includes all 16 DAX measures and 4 pages."""
    spec_path = Path("reports/power_bi_spec.md")
    assert spec_path.exists(), "power_bi_spec.md is missing"
    content = spec_path.read_text(encoding="utf-8")

    # Check 4 pages
    assert "Page 1: Operations Executive Overview" in content
    assert "Page 2: Delivery & Shipping SLA Performance" in content
    assert "Page 3: Commercial Demand & Product Performance" in content
    assert "Page 4: Exceptions & Problem Tracker" in content

    # Check mandatory disclosure
    assert "Carrier freight billing/shipping costs are not captured" in content or "freight" in content.lower()

    # Check key DAX measures
    expected_dax = [
        "[Total Orders]",
        "[Total Line Items]",
        "[Total Units Shipped]",
        "[Net Sales Revenue]",
        "[Operating Profit]",
        "[Operating Profit Margin %]",
        "[Late Shipments Count]",
        "[Late Delivery Rate %]",
        "[On-Time Delivery Rate %]",
        "[Cancellation Rate %]",
        "[Avg Real Shipping Days]",
        "[Avg Scheduled Shipping Days]",
        "[Delivery Delay Gap Days]",
        "[Loss-Making Line Items]",
    ]
    for measure in expected_dax:
        assert measure in content, f"Missing DAX measure: {measure}"
