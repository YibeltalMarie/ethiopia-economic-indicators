"""Tests for econ_pipeline.clean, using small hand-made data (no real files)."""
import numpy as np
import pandas as pd
import pytest

from econ_pipeline.clean import (
    build_dataset,
    clean_indicator,
    drop_missing,
    drop_unnamed_columns,
    filter_country,
    merge_indicators,
    read_raw,
    sort_by_year,
    validate_series,
    wide_to_long,
)

HEADER = '"Country Name","Country Code","Indicator Name","Indicator Code","1960","1961","1962",'


def make_raw_csv(tmp_path, filename="FP.CPI.TOTL.ZG.csv"):
    """Write a tiny file shaped like a real World Bank CSV (same quirks)."""
    lines = [
        '\ufeff"Data Source","World Development Indicators",',
        "",
        '"Last Updated Date","2026-10-08",',
        "",
        HEADER,
        '"Aruba","ABW","Inflation","FP.CPI.TOTL.ZG","","","",',
        '"Ethiopia","ETH","Inflation","FP.CPI.TOTL.ZG","","5.5","-2.0",',
        '"Africa Eastern and Southern","AFE","Inflation","FP.CPI.TOTL.ZG","1.0","2.0","3.0",',
    ]
    path = tmp_path / filename
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def test_read_raw_skips_metadata_lines(tmp_path):
    df = read_raw(make_raw_csv(tmp_path))
    assert list(df.columns[:2]) == ["Country Name", "Country Code"]
    assert len(df) == 3


def test_drop_unnamed_columns_removes_phantom_column(tmp_path):
    raw = read_raw(make_raw_csv(tmp_path))
    assert any(str(c).startswith("Unnamed") for c in raw.columns)  # the problem exists
    cleaned = drop_unnamed_columns(raw)
    assert not any(str(c).startswith("Unnamed") for c in cleaned.columns)


def test_filter_country_keeps_exactly_one_row(tmp_path):
    raw = drop_unnamed_columns(read_raw(make_raw_csv(tmp_path)))
    result = filter_country(raw, "ETH")
    assert len(result) == 1
    assert result["Country Code"].iloc[0] == "ETH"


def test_filter_country_raises_for_unknown_code(tmp_path):
    raw = drop_unnamed_columns(read_raw(make_raw_csv(tmp_path)))
    with pytest.raises(ValueError):
        filter_country(raw, "XXX")


def test_wide_to_long_makes_one_row_per_year_with_numeric_types(tmp_path):
    raw = drop_unnamed_columns(read_raw(make_raw_csv(tmp_path)))
    long = wide_to_long(filter_country(raw, "ETH"))
    assert list(long["year"]) == [1960, 1961, 1962]
    assert pd.api.types.is_integer_dtype(long["year"])
    assert pd.api.types.is_float_dtype(long["value"])


def test_drop_missing_removes_empty_values_without_filling():
    df = pd.DataFrame({"year": [1, 2, 3], "value": [1.0, np.nan, 3.0]})
    result = drop_missing(df)
    assert list(result["year"]) == [1, 3]
    assert list(result["value"]) == [1.0, 3.0]


def test_drop_missing_does_not_modify_its_input():
    df = pd.DataFrame({"year": [1, 2], "value": [1.0, np.nan]})
    drop_missing(df)
    assert len(df) == 2


def test_sort_by_year_orders_oldest_first():
    df = pd.DataFrame({"year": [3, 1, 2], "value": [30.0, 10.0, 20.0]})
    assert list(sort_by_year(df)["year"]) == [1, 2, 3]


def test_validate_series_accepts_good_data():
    df = pd.DataFrame({"year": [1, 2], "value": [1.0, 2.0]})
    assert validate_series(df) is df


@pytest.mark.parametrize(
    "bad_df",
    [
        pd.DataFrame({"year": [1, 1], "value": [1.0, 2.0]}),          # duplicate years
        pd.DataFrame({"year": [], "value": []}),                       # empty
        pd.DataFrame({"year": [1, 2], "value": [1.0, np.nan]}),        # NaN value
        pd.DataFrame({"year": [1, 2], "value": [1.0, np.inf]}),        # infinite value
        pd.DataFrame({"year": [1, 2]}),                                # missing column
    ],
    ids=["duplicate-years", "empty", "nan", "infinite", "missing-column"],
)
def test_validate_series_raises_on_bad_data(bad_df):
    with pytest.raises(ValueError):
        validate_series(bad_df)


def test_clean_indicator_end_to_end(tmp_path):
    result = clean_indicator(make_raw_csv(tmp_path), "ETH")
    assert list(result["year"]) == [1961, 1962]
    assert list(result["value"]) == [5.5, -2.0]


def test_merge_indicators_outer_keeps_all_years_and_never_fills():
    a = pd.DataFrame({"year": [1, 2, 3], "value": [1.0, 2.0, 3.0]})
    b = pd.DataFrame({"year": [2, 3, 4], "value": [20.0, 30.0, 40.0]})
    merged = merge_indicators({"a": a, "b": b})
    assert list(merged.columns) == ["year", "a", "b"]
    assert list(merged["year"]) == [1, 2, 3, 4]
    assert np.isnan(merged.loc[merged["year"] == 1, "b"].iloc[0])
    assert np.isnan(merged.loc[merged["year"] == 4, "a"].iloc[0])


def test_build_dataset_merges_every_indicator(tmp_path):
    make_raw_csv(tmp_path, "CODE_A.csv")
    make_raw_csv(tmp_path, "CODE_B.csv")
    result = build_dataset(
        raw_dir=tmp_path, indicators={"alpha": "CODE_A", "beta": "CODE_B"}
    )
    assert list(result.columns) == ["year", "alpha", "beta"]
    assert list(result["year"]) == [1961, 1962]
