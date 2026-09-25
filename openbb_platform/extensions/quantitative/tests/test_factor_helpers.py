"""Tests for ``openbb_quantitative._factor_helpers``."""

import pandas as pd
import pytest
from openbb_core.app.utils import df_to_basemodel

from openbb_quantitative import _factor_helpers as fh


@pytest.fixture
def anchor() -> pd.Timestamp:
    return pd.Timestamp("2025-06-15")


def test_period_start_one_month(anchor):
    assert fh.period_start(anchor, "1 Month") == anchor - pd.DateOffset(months=1)


def test_period_start_three_month(anchor):
    assert fh.period_start(anchor, "3 Month") == anchor - pd.DateOffset(months=3)


def test_period_start_ytd(anchor):
    assert fh.period_start(anchor, "YTD") == pd.Timestamp(f"{anchor.year}-01-01")


def test_period_start_one_year(anchor):
    assert fh.period_start(anchor, "1 Year") == anchor - pd.DateOffset(years=1)


def test_period_start_three_year(anchor):
    assert fh.period_start(anchor, "3 Year") == anchor - pd.DateOffset(years=3)


def test_period_start_max(anchor):
    assert fh.period_start(anchor, "Max") is None


def test_period_start_invalid(anchor):
    with pytest.raises(ValueError, match="Unsupported period"):
        fh.period_start(anchor, "1 Decade")


def test_align_inputs_happy_path(target_returns_data, factor_matrix_data):
    factor_matrix, target_series, factor_cols = fh.align_inputs(
        target_returns_data,
        factor_matrix_data,
        target="close",
        index="date",
        risk_free_column=None,
    )
    assert factor_cols == ["f1", "f2", "rf"]
    assert list(factor_matrix.columns) == ["f1", "f2", "rf"]
    assert len(factor_matrix) == len(target_series)
    assert target_series.name == "close"


def test_align_inputs_with_risk_free(target_returns_data, factor_matrix_data):
    factor_matrix, target_series, factor_cols = fh.align_inputs(
        target_returns_data,
        factor_matrix_data,
        target="close",
        index="date",
        risk_free_column="rf",
    )
    assert factor_cols == ["f1", "f2"]
    assert "rf" not in factor_matrix.columns
    # Target should be reduced by the constant rf value at every observation.
    assert target_series.iloc[0] != pytest.approx(0.0)


def test_align_inputs_target_missing(factor_matrix_data):
    data = df_to_basemodel(
        pd.DataFrame({"date": pd.date_range("2020", periods=3), "x": [1.0, 2.0, 3.0]})
    )
    with pytest.raises(ValueError, match="Target column 'close' not found"):
        fh.align_inputs(
            data,
            factor_matrix_data,
            target="close",
            index="date",
            risk_free_column=None,
        )


def test_align_inputs_no_overlap(factor_matrix_data):
    far_future = df_to_basemodel(
        pd.DataFrame(
            {"date": pd.date_range("2099-01-01", periods=5), "close": [1.0] * 5}
        )
    )
    with pytest.raises(ValueError, match="No overlapping dates"):
        fh.align_inputs(
            far_future,
            factor_matrix_data,
            target="close",
            index="date",
            risk_free_column=None,
        )


def test_align_inputs_rf_missing(target_returns_data, factor_matrix_data):
    with pytest.raises(ValueError, match="risk_free_column='missing'"):
        fh.align_inputs(
            target_returns_data,
            factor_matrix_data,
            target="close",
            index="date",
            risk_free_column="missing",
        )


def test_align_inputs_no_factor_cols(target_returns_data):
    rf_only = df_to_basemodel(
        pd.DataFrame(
            {
                "date": pd.date_range("2018-01-01", periods=800, freq="B"),
                "rf": [0.0001] * 800,
            }
        )
    )
    with pytest.raises(ValueError, match="No factor columns remain"):
        fh.align_inputs(
            target_returns_data,
            rf_only,
            target="close",
            index="date",
            risk_free_column="rf",
        )


def test_align_inputs_all_nan_after_alignment(factor_matrix_data, factor_dates):
    """When the target is NaN at every overlapping date the aligned frame is empty."""
    import numpy as np

    # One valid value at a date that is NOT in the factor index keeps the column
    # alive through the basemodel round trip; the overlapping rows are all NaN.
    anchor = factor_dates[0] - pd.Timedelta(days=1)
    overlap_dates = factor_dates[:5]
    target_df = pd.DataFrame(
        {
            "date": [anchor] + list(overlap_dates),
            "close": [1.0] + [np.nan] * len(overlap_dates),
        }
    )
    nan_target = df_to_basemodel(target_df)
    with pytest.raises(ValueError, match="No observations remain"):
        fh.align_inputs(
            nan_target,
            factor_matrix_data,
            target="close",
            index="date",
            risk_free_column=None,
        )
