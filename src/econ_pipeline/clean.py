"""Stage 2 (clean): turn raw World Bank files into tidy, validated data.

Every function takes data in and returns new data out. Nothing here edits
the raw files or modifies its inputs.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from .load import INDICATORS

SKIP_ROWS = 4  # metadata lines above the real header in World Bank CSVs


def read_raw(path: str | Path) -> pd.DataFrame:
    """Read a raw World Bank CSV, skipping metadata lines and the BOM."""
    return pd.read_csv(path, skiprows=SKIP_ROWS, encoding="utf-8-sig")


def drop_unnamed_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Drop phantom 'Unnamed: N' columns created by trailing commas."""
    keep = [c for c in df.columns if not str(c).startswith("Unnamed")]
    return df[keep].copy()


def filter_country(df: pd.DataFrame, country_code: str = "ETH") -> pd.DataFrame:
    """Keep only the row for one country code. Raise if it is not exactly one row."""
    rows = df[df["Country Code"] == country_code]
    if len(rows) != 1:
        raise ValueError(f"Expected exactly one row for {country_code!r}, found {len(rows)}")
    return rows.copy()


def wide_to_long(df: pd.DataFrame) -> pd.DataFrame:
    """Reshape one-column-per-year data into rows of (country, indicator, year, value)."""
    year_cols = [c for c in df.columns if str(c).isdigit()]
    long = df.melt(
        id_vars=["Country Code", "Indicator Code"],
        value_vars=year_cols,
        var_name="year",
        value_name="value",
    )
    long["year"] = long["year"].astype(int)
    long["value"] = pd.to_numeric(long["value"], errors="raise")
    return long.rename(
        columns={"Country Code": "country_code", "Indicator Code": "indicator_code"}
    )


def drop_missing(df: pd.DataFrame) -> pd.DataFrame:
    """Drop rows with no value. Missing values are never filled in."""
    return df.dropna(subset=["value"]).reset_index(drop=True)


def sort_by_year(df: pd.DataFrame) -> pd.DataFrame:
    """Sort rows by year, oldest first."""
    return df.sort_values("year").reset_index(drop=True)


def validate_series(df: pd.DataFrame) -> pd.DataFrame:
    """Check a cleaned series. Return it unchanged, or raise ValueError."""
    for column in ("year", "value"):
        if column not in df.columns:
            raise ValueError(f"Missing required column: {column!r}")
    if df.empty:
        raise ValueError("Series is empty after cleaning")
    if df["year"].duplicated().any():
        raise ValueError("Duplicate years found")
    if not np.isfinite(df["value"].to_numpy(dtype=float)).all():
        raise ValueError("Non-finite values (NaN or infinity) found in 'value'")
    return df


def clean_indicator(path: str | Path, country_code: str = "ETH") -> pd.DataFrame:
    """Rules 1 to 6 plus validation, for one raw file and one country."""
    df = read_raw(path)
    df = drop_unnamed_columns(df)
    df = filter_country(df, country_code)
    df = wide_to_long(df)
    df = drop_missing(df)
    df = sort_by_year(df)
    return validate_series(df)


def merge_indicators(series_by_name: dict[str, pd.DataFrame], how: str = "outer") -> pd.DataFrame:
    """Combine cleaned series into one table: a 'year' column, then one column per name.

    With how='outer' every year found in any series is kept; years missing from
    a series stay empty (NaN) and are never filled.
    """
    columns = [
        df.set_index("year")["value"].rename(name) for name, df in series_by_name.items()
    ]
    merged = pd.concat(columns, axis=1, join=how).sort_index()
    merged.index.name = "year"
    return merged.reset_index()


def build_dataset(
    raw_dir: str | Path = "data/raw",
    country_code: str = "ETH",
    indicators: dict[str, str] | None = None,
) -> pd.DataFrame:
    """Clean every indicator for one country and merge them on year."""
    indicators = INDICATORS if indicators is None else indicators
    cleaned = {
        name: clean_indicator(Path(raw_dir) / f"{code}.csv", country_code)
        for name, code in indicators.items()
    }
    return merge_indicators(cleaned)


def save_dataset(df: pd.DataFrame, path: str | Path) -> Path:
    """Write the cleaned dataset to CSV, creating the folder if needed."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)
    return path
