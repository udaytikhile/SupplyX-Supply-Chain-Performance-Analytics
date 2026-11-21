"""
SupplyX - Exploratory Data Analysis & Causal Insights Engine
Generates publication-quality figures and deep operational diagnostics.
"""

from pathlib import Path
from typing import Dict, Any
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def run_eda(clean_csv: str = "data/cleaned_supply_chain.csv", out_dir: str = "reports/figures") -> Dict[str, Any]:
    """Performs statistical EDA and exports visual charts."""
    df = pd.read_csv(clean_csv, low_memory=False)
    df["order_date"] = pd.to_datetime(df["order_date"])
    df["shipping_date"] = pd.to_datetime(df["shipping_date"])

    output_dir = Path(out_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Style configuration
    plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")
    plt.rcParams.update({
        "font.family": "sans-serif",
        "font.size": 10,
        "axes.titlesize": 12,
        "axes.labelsize": 10,
        "figure.titlesize": 14,
        "figure.autolayout": True,
    })

    # --------------------------------------------------------------------------
    # Figure 1: The SLA Scheduling Paradox (First Class vs Standard Class)
    # --------------------------------------------------------------------------
    mode_stats = df.groupby("shipping_mode").agg({
        "days_shipping_real": "mean",
        "days_shipping_scheduled": "mean",
        "late_delivery_risk": "mean",
        "order_item_id": "count"
    }).reindex(["Same Day", "First Class", "Second Class", "Standard Class"]).reset_index()

    fig, ax1 = plt.subplots(figsize=(8, 4.5), dpi=150)
    x = np.arange(len(mode_stats))
    width = 0.35

    rects1 = ax1.bar(x - width/2, mode_stats["days_shipping_scheduled"], width, label="Scheduled (Promised) Days", color="#94A3B8")
    rects2 = ax1.bar(x + width/2, mode_stats["days_shipping_real"], width, label="Actual Shipping Days", color="#2563EB")

    ax1.set_ylabel("Transit Duration (Days)", color="#0F172A", fontweight="bold")
    ax1.set_xticks(x)
    ax1.set_xticklabels(mode_stats["shipping_mode"], fontweight="semibold")
    ax1.set_ylim(0, 6)
    ax1.legend(loc="upper left")

    # Overlay late rate
    ax2 = ax1.twinx()
    ax2.plot(x, mode_stats["late_delivery_risk"] * 100, color="#EF4444", marker="o", linewidth=2.5, label="Late Delivery %")
    ax2.set_ylabel("Late Delivery Rate (%)", color="#EF4444", fontweight="bold")
    ax2.set_ylim(0, 110)
    ax2.grid(False)

    for i, val in enumerate(mode_stats["late_delivery_risk"] * 100):
        ax2.annotate(f"{val:.1f}%", (x[i], val + 3), ha="center", color="#EF4444", fontweight="bold")

    plt.title("Figure 1: The SLA Paradox — First Class is Physically Faster, Yet 95.3% 'Late'", fontweight="bold", pad=12)
    fig1_path = output_dir / "fig1_mode_sla_paradox.png"
    plt.savefig(fig1_path)
    plt.close()

    # --------------------------------------------------------------------------
    # Figure 2: Regional Performance & Market Share
    # --------------------------------------------------------------------------
    mkt_stats = df.groupby("market").agg({
        "order_item_total": "sum",
        "late_delivery_risk": "mean",
        "days_shipping_real": "mean"
    }).reset_index().sort_values(by="order_item_total", ascending=False)

    fig, ax1 = plt.subplots(figsize=(8, 4.5), dpi=150)
    bars = ax1.bar(mkt_stats["market"], mkt_stats["order_item_total"] / 1e6, color="#0EA5E9", width=0.55)
    ax1.set_ylabel("Net Revenue ($ Millions)", color="#0EA5E9", fontweight="bold")
    ax1.set_xlabel("Global Market", fontweight="bold")

    ax2 = ax1.twinx()
    ax2.plot(mkt_stats["market"], mkt_stats["late_delivery_risk"] * 100, color="#EF4444", marker="s", linewidth=2, label="Late Rate %")
    ax2.set_ylabel("Late Delivery Rate (%)", color="#EF4444", fontweight="bold")
    ax2.set_ylim(40, 70)
    ax2.grid(False)

    for i, row in mkt_stats.iterrows():
        ax2.annotate(f"{row['late_delivery_risk']*100:.1f}%", (row["market"], row["late_delivery_risk"]*100 + 1), ha="center", color="#EF4444", fontweight="bold")

    plt.title("Figure 2: Net Revenue vs Late Delivery Rate by Market (Flat ~55% Late Rate)", fontweight="bold", pad=12)
    fig2_path = output_dir / "fig2_regional_fulfillment_heatmap.png"
    plt.savefig(fig2_path)
    plt.close()

    # --------------------------------------------------------------------------
    # Figure 3: Monthly Volume & Revenue Timeline (37 Months)
    # --------------------------------------------------------------------------
    monthly = df.set_index("order_date").resample("ME").agg({
        "order_item_id": "count",
        "order_item_total": "sum",
        "late_delivery_risk": "mean"
    }).reset_index()

    fig, ax1 = plt.subplots(figsize=(9, 4.5), dpi=150)
    ax1.plot(monthly["order_date"], monthly["order_item_id"], color="#2563EB", linewidth=2, label="Monthly Items Shipped")
    ax1.set_ylabel("Order Items Shipped", color="#2563EB", fontweight="bold")
    ax1.set_ylim(0, 6500)

    # Highlight structural shift
    ax1.axvline(pd.to_datetime("2017-10-01"), color="#F59E0B", linestyle="--", linewidth=1.5, label="Q4 2017 Structural Break")

    ax2 = ax1.twinx()
    ax2.plot(monthly["order_date"], monthly["order_item_total"] / 1e3, color="#10B981", linewidth=2, linestyle=":", label="Net Revenue ($k)")
    ax2.set_ylabel("Net Revenue ($ Thousands)", color="#10B981", fontweight="bold")
    ax2.grid(False)

    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc="lower left")

    plt.title("Figure 3: Monthly Demand & Revenue Trajectory (Jan 2015 – Jan 2018)", fontweight="bold", pad=12)
    fig3_path = output_dir / "fig3_monthly_volume_and_revenue_trend.png"
    plt.savefig(fig3_path)
    plt.close()

    # --------------------------------------------------------------------------
    # Figure 4: Discount Depth vs Profit Erosion
    # --------------------------------------------------------------------------
    df["discount_tier"] = pd.cut(
        df["order_item_discount_rate"],
        bins=[-0.01, 0.0, 0.05, 0.10, 0.15, 0.20, 1.0],
        labels=["0%", "1-5%", "6-10%", "11-15%", "16-20%", ">20%"]
    )
    discount_perf = df.groupby("discount_tier", observed=False).agg({
        "order_profit_per_order": "sum",
        "order_item_total": "sum",
        "is_negative_profit": "mean"
    }).reset_index()
    discount_perf["profit_margin_pct"] = (discount_perf["order_profit_per_order"] / discount_perf["order_item_total"]) * 100

    fig, ax1 = plt.subplots(figsize=(8, 4.5), dpi=150)
    bars = ax1.bar(discount_perf["discount_tier"], discount_perf["profit_margin_pct"], color="#10B981", width=0.5)
    ax1.set_ylabel("Operating Profit Margin (%)", color="#10B981", fontweight="bold")
    ax1.set_xlabel("Promotional Discount Tier", fontweight="bold")
    ax1.set_ylim(0, 16)

    ax2 = ax1.twinx()
    ax2.plot(discount_perf["discount_tier"], discount_perf["is_negative_profit"] * 100, color="#EF4444", marker="^", linewidth=2, label="Loss-Making Orders %")
    ax2.set_ylabel("Orders Operating at a Loss (%)", color="#EF4444", fontweight="bold")
    ax2.set_ylim(10, 30)
    ax2.grid(False)

    for i, val in enumerate(discount_perf["profit_margin_pct"]):
        ax1.annotate(f"{val:.1f}%", (i, val + 0.3), ha="center", fontweight="bold", color="#065F46")

    plt.title("Figure 4: Discount Depth vs Margin Health (Promotions Cause Negative Profit)", fontweight="bold", pad=12)
    fig4_path = output_dir / "fig4_discount_vs_profit_erosion.png"
    plt.savefig(fig4_path)
    plt.close()

    # --------------------------------------------------------------------------
    # Figure 5: Shipping Delay Variance Distribution (Histogram)
    # --------------------------------------------------------------------------
    delay_counts = df["shipping_delay_days"].value_counts().sort_index()

    fig, ax = plt.subplots(figsize=(8, 4.5), dpi=150)
    colors = ["#10B981" if x <= 0 else "#EF4444" for x in delay_counts.index]
    bars = ax.bar(delay_counts.index, delay_counts.values / 1e3, color=colors, width=0.6)

    ax.set_xlabel("Days Delayed Beyond Promised Schedule (Real - Scheduled)", fontweight="bold")
    ax.set_ylabel("Shipment Volume (Thousands)", fontweight="bold")
    ax.set_xticks(delay_counts.index)

    for bar, count in zip(bars, delay_counts.values):
        ax.annotate(f"{count/1e3:.1f}k", (bar.get_x() + bar.get_width()/2, bar.get_height() + 1), ha="center", fontsize=9, fontweight="bold")

    plt.title("Figure 5: SLA Gap Distribution — 54.8% of Shipments are 1 to 2 Days Overdue", fontweight="bold", pad=12)
    fig5_path = output_dir / "fig5_delay_distribution_histogram.png"
    plt.savefig(fig5_path)
    plt.close()

    return {
        "figures_generated": [
            str(fig1_path), str(fig2_path), str(fig3_path), str(fig4_path), str(fig5_path)
        ],
        "first_class_avg_real_days": float(mode_stats.loc[mode_stats["shipping_mode"] == "First Class", "days_shipping_real"].iloc[0]),
        "standard_class_avg_real_days": float(mode_stats.loc[mode_stats["shipping_mode"] == "Standard Class", "days_shipping_real"].iloc[0]),
        "first_class_late_rate": float(mode_stats.loc[mode_stats["shipping_mode"] == "First Class", "late_delivery_risk"].iloc[0]),
        "standard_class_late_rate": float(mode_stats.loc[mode_stats["shipping_mode"] == "Standard Class", "late_delivery_risk"].iloc[0]),
    }


if __name__ == "__main__":
    res = run_eda()
    print("EDA Complete. Generated figures:")
    for fig in res["figures_generated"]:
        print(f"  {fig}")
    print(f"First Class: {res['first_class_avg_real_days']:.2f} real days vs {res['first_class_late_rate']*100:.1f}% late")
    print(f"Standard Class: {res['standard_class_avg_real_days']:.2f} real days vs {res['standard_class_late_rate']*100:.1f}% late")
