"""Stage 4 (report): turn answers into plain-language summaries and charts.

Plot functions return a matplotlib Figure and never call show(), so the caller
(a notebook, a script, a test) decides what to do with it. Summary text is
built from the computed answers, so it can never go out of date.
"""
from __future__ import annotations

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.figure import Figure

from .process import complete_cases, largest_jump, pct_change


def describe_correlation(r: float) -> str:
    """Describe a correlation coefficient in words.

    The cut-offs (under 0.3 weak, under 0.6 moderate, otherwise strong) are
    common rules of thumb, not strict laws.
    """
    size = abs(r)
    if size < 0.3:
        strength = "weak"
    elif size < 0.6:
        strength = "moderate"
    else:
        strength = "strong"
    return f"{strength} {'negative' if r < 0 else 'positive'}"


def summary_table(answers: dict) -> pd.DataFrame:
    """Build a table with one plain-language finding per project question."""
    q1, q2, q3 = answers["q1"], answers["q2"], answers["q3"]

    if q1["count"] == 0:
        q1_text = "No years were above the threshold."
    else:
        years_text = ", ".join(str(y) for y in q1["years"])
        q1_text = f"{q1['count']} years: {years_text}."

    q2_text = (
        f"Across {q2['n_changes']} year-over-year changes, the mean was "
        f"{q2['mean_pct_change']:.1f}% and the median was {q2['median_pct_change']:.2f}%. "
        f"The rate did not change in {q2['n_zero_change_years']} of those years. "
        f"The largest jump was {q2['largest_jump_pct']:.1f}% in {q2['largest_jump_year']}."
    )

    direction = "higher" if q3["mean_growth_high"] > q3["mean_growth_other"] else "lower"
    q3_text = (
        f"The correlation is {q3['correlation']:.2f} "
        f"({describe_correlation(q3['correlation'])}). Mean growth was "
        f"{q3['mean_growth_high']:.2f}% in the {q3['n_high_years']} years above the "
        f"threshold and {q3['mean_growth_other']:.2f}% in the other "
        f"{q3['n_other_years']} years, which is {direction} in high-inflation years. "
        f"This describes a linear pattern in these years only; it does not show "
        f"cause, and {q3['n_high_years']} high-inflation years is a small sample."
    )

    rows = [
        (f"Q1. In which years was inflation above {q1['threshold']:.0f}%?", q1_text),
        ("Q2. How much did the official exchange rate change each year?", q2_text),
        ("Q3. Is there a relationship between inflation and GDP growth?", q3_text),
    ]
    return pd.DataFrame(rows, columns=["question", "finding"])


def plot_inflation(
    dataset: pd.DataFrame, threshold: float = 20.0, country_name: str = "Ethiopia"
) -> Figure:
    """Line chart of inflation, with the threshold and the years above it marked."""
    years, inflation = complete_cases(
        dataset["year"].to_numpy(), dataset["inflation"].to_numpy(dtype=float)
    )
    above = inflation > threshold

    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(years, inflation, color="tab:blue", linewidth=1.5, label="Inflation")
    ax.axhline(threshold, color="tab:red", linestyle="--", label=f"{threshold:.0f}% threshold")
    ax.scatter(years[above], inflation[above], color="tab:red", zorder=3, label="Above threshold")
    ax.set_title(f"{country_name}: inflation")
    ax.set_xlabel("Year")
    ax.set_ylabel("Inflation, consumer prices (annual %)")
    ax.grid(alpha=0.3)
    ax.legend()
    fig.tight_layout()
    return fig


def plot_exchange_rate(dataset: pd.DataFrame, country_name: str = "Ethiopia") -> Figure:
    """Two panels: the official exchange rate, and its year-over-year % change."""
    years, rate = complete_cases(
        dataset["year"].to_numpy(), dataset["exchange_rate"].to_numpy(dtype=float)
    )
    change_years, changes = pct_change(years, rate)
    jump_year, jump_pct = largest_jump(years, rate)

    fig, (top, bottom) = plt.subplots(2, 1, figsize=(10, 6), sharex=True)
    top.plot(years, rate, color="tab:green", linewidth=1.5)
    top.set_title(f"{country_name}: official exchange rate")
    top.set_ylabel("LCU per US$")
    top.grid(alpha=0.3)

    bottom.bar(change_years, changes, color="tab:purple")
    bottom.annotate(
        f"{jump_year}: {jump_pct:.0f}%",
        xy=(jump_year, jump_pct),
        xytext=(6, -2),
        textcoords="offset points",
    )
    bottom.set_ylabel("Year-over-year change (%)")
    bottom.set_xlabel("Year")
    bottom.grid(alpha=0.3)
    fig.tight_layout()
    return fig


def plot_inflation_vs_growth(
    dataset: pd.DataFrame, threshold: float = 20.0, country_name: str = "Ethiopia"
) -> Figure:
    """Scatter of inflation against GDP growth, with high-inflation years labeled."""
    years, inflation, growth = complete_cases(
        dataset["year"].to_numpy(),
        dataset["inflation"].to_numpy(dtype=float),
        dataset["gdp_growth"].to_numpy(dtype=float),
    )
    high = inflation > threshold

    fig, ax = plt.subplots(figsize=(7, 5))
    ax.scatter(inflation[~high], growth[~high], color="tab:blue", label="Other years")
    ax.scatter(
        inflation[high], growth[high], color="tab:red", label=f"Inflation above {threshold:.0f}%"
    )
    for year, x, y in zip(years[high], inflation[high], growth[high]):
        ax.annotate(str(year), (x, y), xytext=(4, 4), textcoords="offset points", fontsize=8)
    ax.axvline(threshold, color="tab:red", linestyle="--", linewidth=0.8)
    ax.axhline(0, color="gray", linewidth=0.8)
    ax.set_title(f"{country_name}: inflation vs GDP growth")
    ax.set_xlabel("Inflation (annual %)")
    ax.set_ylabel("GDP growth (annual %)")
    ax.grid(alpha=0.3)
    ax.legend()
    fig.tight_layout()
    return fig
