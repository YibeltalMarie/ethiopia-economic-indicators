"""Tests for econ_pipeline.report (text and figures, using a tiny dataset)."""
import matplotlib

matplotlib.use("Agg")  # draw without a screen

import matplotlib.pyplot as plt
import pandas as pd
import pytest

from econ_pipeline.process import answer_questions
from econ_pipeline.report import (
    describe_correlation,
    plot_exchange_rate,
    plot_inflation,
    plot_inflation_vs_growth,
    summary_table,
)


@pytest.fixture
def dataset():
    return pd.DataFrame(
        {
            "year": [1, 2, 3, 4, 5],
            "inflation": [10.0, 30.0, 5.0, 40.0, 25.0],
            "exchange_rate": [2.0, 2.0, 2.0, 4.0, 5.0],
            "gdp_growth": [5.0, -2.0, 7.0, -4.0, 1.0],
        }
    )


@pytest.fixture
def answers(dataset):
    return answer_questions(dataset, inflation_threshold=20.0)


@pytest.mark.parametrize(
    "r, expected",
    [(0.1, "weak positive"), (-0.45, "moderate negative"), (0.8, "strong positive")],
)
def test_describe_correlation_uses_plain_words(r, expected):
    assert describe_correlation(r) == expected


def test_summary_table_has_one_row_per_question(answers):
    table = summary_table(answers)
    assert list(table.columns) == ["question", "finding"]
    assert len(table) == 3


def test_summary_table_q1_lists_the_years(answers):
    assert "3 years: 2, 4, 5." in summary_table(answers).loc[0, "finding"]


def test_summary_table_q2_reports_mean_median_and_largest_jump(answers):
    finding = summary_table(answers).loc[1, "finding"]
    assert "mean" in finding and "median" in finding
    assert "100.0% in 4" in finding


def test_summary_table_q3_says_lower_when_high_inflation_years_grew_less(answers):
    finding = summary_table(answers).loc[2, "finding"]
    assert "lower in high-inflation years" in finding


def test_plot_inflation_returns_a_figure(dataset):
    fig = plot_inflation(dataset)
    assert len(fig.axes) == 1
    plt.close(fig)


def test_plot_exchange_rate_has_two_panels(dataset):
    fig = plot_exchange_rate(dataset)
    assert len(fig.axes) == 2
    plt.close(fig)


def test_plot_inflation_vs_growth_returns_a_figure(dataset):
    fig = plot_inflation_vs_growth(dataset)
    assert len(fig.axes) == 1
    plt.close(fig)
