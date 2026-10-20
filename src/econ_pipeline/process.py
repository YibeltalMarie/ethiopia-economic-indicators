"""Stage 3 (process): answer the project questions using NumPy.

The math functions take NumPy arrays and return plain numbers or arrays.
Pandas is used only at the edge (answer_questions), to pull columns out of
the merged dataset.
"""
from __future__ import annotations

import numpy as np
import pandas as pd


def complete_cases(years, *values):
    """Keep only positions where every values array has a number (no NaN).

    Returns the filtered years followed by each filtered values array.
    """
    years = np.asarray(years)
    arrays = [np.asarray(v, dtype=float) for v in values]
    keep = np.ones(years.shape, dtype=bool)
    for arr in arrays:
        if arr.shape != years.shape:
            raise ValueError("years and every values array must have the same shape")
        keep &= ~np.isnan(arr)
    return (years[keep], *[arr[keep] for arr in arrays])


def years_above(years, values, threshold):
    """Return the years whose value is strictly above the threshold."""
    years, values = complete_cases(years, values)
    return years[values > threshold]


def pct_change(years, values):
    """Year-over-year percentage change.

    Returns (years[1:], changes), where changes[i] is the change from the
    previous year to years[i]. Requires consecutive years and no zero values.
    """
    years, values = complete_cases(years, values)
    if len(values) < 2:
        raise ValueError("Need at least two values to compute a change")
    if not np.all(np.diff(years) == 1):
        raise ValueError("Years are not consecutive; a change across a gap would be misleading")
    if np.any(values[:-1] == 0):
        raise ValueError("Cannot compute a percentage change from a value of zero")
    changes = np.diff(values) / values[:-1] * 100
    return years[1:], changes


def largest_jump(years, values):
    """Return (year, percent) for the largest year-over-year increase."""
    change_years, changes = pct_change(years, values)
    i = int(np.argmax(changes))
    return int(change_years[i]), float(changes[i])


def exchange_rate_summary(years, values):
    """Summarize year-over-year percentage changes (question 2)."""
    _, changes = pct_change(years, values)
    jump_year, jump_pct = largest_jump(years, values)
    return {
        "n_changes": int(len(changes)),
        "mean_pct_change": float(np.mean(changes)),
        "median_pct_change": float(np.median(changes)),
        "n_zero_change_years": int(np.sum(changes == 0)),
        "largest_jump_year": jump_year,
        "largest_jump_pct": jump_pct,
    }


def correlation(years, x, y):
    """Pearson correlation of x and y over the years where both have values."""
    _, x, y = complete_cases(years, x, y)
    if len(x) < 3:
        raise ValueError("Need at least three paired values for a correlation")
    return float(np.corrcoef(x, y)[0, 1])


def growth_by_inflation_group(years, inflation, growth, threshold=20.0):
    """Compare mean growth in high-inflation years against all other years."""
    _, inflation, growth = complete_cases(years, inflation, growth)
    high = inflation > threshold
    if not high.any() or high.all():
        raise ValueError("Need years both above and not above the threshold")
    return {
        "threshold": float(threshold),
        "n_high_years": int(high.sum()),
        "n_other_years": int((~high).sum()),
        "mean_growth_high": float(growth[high].mean()),
        "mean_growth_other": float(growth[~high].mean()),
    }


def answer_questions(dataset: pd.DataFrame, inflation_threshold: float = 20.0) -> dict:
    """Answer the three project questions from the merged dataset."""
    years = dataset["year"].to_numpy()
    inflation = dataset["inflation"].to_numpy(dtype=float)
    rate = dataset["exchange_rate"].to_numpy(dtype=float)
    growth = dataset["gdp_growth"].to_numpy(dtype=float)

    high_years = years_above(years, inflation, inflation_threshold)
    return {
        "q1": {
            "threshold": float(inflation_threshold),
            "years": [int(y) for y in high_years],
            "count": int(len(high_years)),
        },
        "q2": exchange_rate_summary(years, rate),
        "q3": {
            "correlation": correlation(years, inflation, growth),
            **growth_by_inflation_group(years, inflation, growth, inflation_threshold),
        },
    }
