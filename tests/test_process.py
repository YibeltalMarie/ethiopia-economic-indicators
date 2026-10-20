"""Tests for econ_pipeline.process, using small hand-checkable numbers."""
import numpy as np
import pandas as pd
import pytest

from econ_pipeline.process import (
    answer_questions,
    complete_cases,
    correlation,
    exchange_rate_summary,
    growth_by_inflation_group,
    largest_jump,
    pct_change,
    years_above,
)


def test_complete_cases_drops_positions_with_missing_values_in_any_array():
    years, a, b = complete_cases([1, 2, 3, 4], [1.0, np.nan, 3.0, 4.0], [1.0, 2.0, 3.0, np.nan])
    assert list(years) == [1, 3]
    assert list(a) == [1.0, 3.0]
    assert list(b) == [1.0, 3.0]


def test_years_above_is_strictly_above_and_ignores_missing_values():
    result = years_above([1, 2, 3, 4], [10.0, 20.0, 30.0, np.nan], 20.0)
    assert list(result) == [3]


def test_pct_change_computes_year_over_year_percentages():
    years, changes = pct_change([1, 2, 3], [100.0, 110.0, 99.0])
    assert list(years) == [2, 3]
    assert changes == pytest.approx([10.0, -10.0])


def test_pct_change_raises_when_years_have_a_gap():
    with pytest.raises(ValueError):
        pct_change([1, 2, 4], [1.0, 2.0, 3.0])


def test_pct_change_raises_on_zero_starting_value():
    with pytest.raises(ValueError):
        pct_change([1, 2], [0.0, 5.0])


def test_largest_jump_returns_year_and_percent_of_biggest_increase():
    assert largest_jump([1, 2, 3, 4], [2.0, 2.0, 4.0, 5.0]) == (3, pytest.approx(100.0))


def test_exchange_rate_summary_on_a_fixed_then_moving_series():
    # changes between consecutive years: 0, 0, 100, 25
    summary = exchange_rate_summary([1, 2, 3, 4, 5], [2.0, 2.0, 2.0, 4.0, 5.0])
    assert summary["n_changes"] == 4
    assert summary["mean_pct_change"] == pytest.approx(31.25)
    assert summary["median_pct_change"] == pytest.approx(12.5)
    assert summary["n_zero_change_years"] == 2
    assert summary["largest_jump_year"] == 4
    assert summary["largest_jump_pct"] == pytest.approx(100.0)


def test_correlation_is_one_for_a_perfect_positive_relationship():
    assert correlation([1, 2, 3, 4], [1, 2, 3, 4], [2, 4, 6, 8]) == pytest.approx(1.0)


def test_correlation_is_minus_one_for_a_perfect_negative_relationship():
    assert correlation([1, 2, 3, 4], [1, 2, 3, 4], [8, 6, 4, 2]) == pytest.approx(-1.0)


def test_correlation_raises_with_too_few_points():
    with pytest.raises(ValueError):
        correlation([1, 2], [1.0, 2.0], [2.0, 4.0])


def test_growth_by_inflation_group_splits_at_the_threshold():
    result = growth_by_inflation_group(
        [1, 2, 3, 4], [10.0, 30.0, 5.0, 40.0], [5.0, -2.0, 7.0, -4.0], threshold=20.0
    )
    assert result["n_high_years"] == 2
    assert result["n_other_years"] == 2
    assert result["mean_growth_high"] == pytest.approx(-3.0)
    assert result["mean_growth_other"] == pytest.approx(6.0)


def test_growth_by_inflation_group_raises_if_one_group_is_empty():
    with pytest.raises(ValueError):
        growth_by_inflation_group([1, 2], [1.0, 2.0], [3.0, 4.0], threshold=20.0)


def test_answer_questions_on_a_small_dataset():
    dataset = pd.DataFrame(
        {
            "year": [1, 2, 3, 4, 5],
            "inflation": [10.0, 30.0, 5.0, 40.0, 25.0],
            "exchange_rate": [2.0, 2.0, 2.0, 4.0, 5.0],
            "gdp_growth": [5.0, -2.0, 7.0, -4.0, 1.0],
        }
    )
    answers = answer_questions(dataset, inflation_threshold=20.0)
    assert answers["q1"]["years"] == [2, 4, 5]
    assert answers["q1"]["count"] == 3
    assert answers["q2"]["largest_jump_year"] == 4
    assert answers["q3"]["n_high_years"] == 3
    assert answers["q3"]["mean_growth_high"] == pytest.approx(-5 / 3)
