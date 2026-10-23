"""Tests for ``openbb_charting.charts.helpers``."""

from __future__ import annotations

import pandas as pd
import pytest

from openbb_charting.charts import helpers
from openbb_charting.charts.helpers import (
    calculate_returns,
    duration_sorter,
    get_charting_functions,
    get_charting_functions_list,
    heikin_ashi,
    should_share_axis,
    z_score_standardization,
)


class _View:
    """A small stand-in module-like view object for discovery tests."""

    __module__ = "tests._fake_view_module"


def _public_implemented(self):  # pragma: no cover - body never executed
    """A public function that is implemented."""
    return 1


def _public_not_implemented(self):  # pragma: no cover - body never executed
    """A public function that raises NotImplementedError."""
    raise NotImplementedError


class TestZScoreStandardization:
    """Tests for ``z_score_standardization``."""

    def test_returns_zero_mean_unit_std(self, ohlcv_df):
        """It returns a Series with ~zero mean and ~unit standard deviation."""
        result = z_score_standardization(ohlcv_df["close"])
        assert isinstance(result, pd.Series)
        assert abs(result.mean()) < 1e-9
        assert abs(result.std() - 1) < 1e-9


class TestCalculateReturns:
    """Tests for ``calculate_returns``."""

    def test_first_value_is_zero(self, ohlcv_df):
        """It returns cumulative percentage returns starting at zero."""
        result = calculate_returns(ohlcv_df["close"])
        assert isinstance(result, pd.Series)
        assert result.iloc[0] == 0
        assert len(result) == len(ohlcv_df)


class TestShouldShareAxis:
    """Tests for ``should_share_axis``."""

    def test_true_when_ratio_within_threshold(self):
        """It returns True when two columns have a similar range."""
        df = pd.DataFrame({"a": [0, 1, 2, 3], "b": [0, 1, 2, 3]})
        assert should_share_axis(df, "a", "b", threshold=2.5) is True

    def test_true_when_ratio_exactly_one(self):
        """It returns True when the range ratio equals exactly one."""
        df = pd.DataFrame({"a": [0, 10], "b": [5, 15]})
        assert should_share_axis(df, "a", "b") is True

    def test_false_when_ratio_exceeds_threshold(self):
        """It returns False when the ranges differ beyond the threshold."""
        df = pd.DataFrame({"a": [0, 1], "b": [0, 1000]})
        assert should_share_axis(df, "a", "b", threshold=2.5) is False

    def test_series_input_is_coerced_to_frame(self):
        """It coerces a Series input to a frame and shares the axis with itself."""
        series = pd.Series([1, 2, 3], name="x")
        assert should_share_axis(series, "x", "x") is True

    def test_exception_returns_false(self):
        """It returns False when an invalid column triggers an exception."""
        df = pd.DataFrame({"a": [1, 2, 3]})
        assert should_share_axis(df, "missing", "a") is False


class TestHeikinAshi:
    """Tests for ``heikin_ashi``."""

    def test_returns_recomputed_ohlc(self, ohlcv_df):
        """It returns a copy with Heikin Ashi OHLC values."""
        result = heikin_ashi(ohlcv_df)
        assert isinstance(result, pd.DataFrame)
        assert list(result.columns) == list(ohlcv_df.columns)
        assert len(result) == len(ohlcv_df)
        assert not result["close"].equals(ohlcv_df["close"])

    def test_missing_columns_raises_value_error(self):
        """It raises ValueError when required OHLC columns are missing."""
        df = pd.DataFrame({"open": [1, 2], "close": [1, 2]})
        with pytest.raises(ValueError, match="expected column labels"):
            heikin_ashi(df)


class TestDurationSorter:
    """Tests for ``duration_sorter``."""

    def test_sorts_months_and_years(self):
        """It sorts mixed month and year duration labels ascending."""
        durations = ["year_1", "month_3", "month_1", "year_2"]
        assert duration_sorter(durations) == [
            "month_1",
            "month_3",
            "year_1",
            "year_2",
        ]

    def test_long_term_sorts_last(self):
        """It places the special ``long_term`` label after shorter durations."""
        durations = ["long_term", "month_6", "year_1"]
        assert duration_sorter(durations) == ["month_6", "year_1", "long_term"]


class TestGetChartingFunctions:
    """Tests for ``get_charting_functions`` and its list variant."""

    def test_discovers_only_implemented_public_functions(self):
        """It returns implemented, public, same-module functions only."""

        class View:
            """A view exposing implemented, private and not-implemented funcs."""

        View.__module__ = __name__
        View.implemented = staticmethod(_public_implemented)
        View.not_implemented = staticmethod(_public_not_implemented)
        View._private = staticmethod(_public_implemented)
        _public_implemented.__module__ = __name__
        _public_not_implemented.__module__ = __name__

        result = get_charting_functions(View)
        assert "implemented" in result
        assert "not_implemented" not in result
        assert "_private" not in result

    def test_excludes_functions_from_other_modules(self):
        """It excludes functions whose module differs from the view's module."""

        class View:
            """A view whose function comes from a different module."""

        View.__module__ = "some.other.module"
        View.implemented = staticmethod(_public_implemented)
        _public_implemented.__module__ = __name__

        result = get_charting_functions(View)
        assert result == {}

    def test_list_returns_names(self):
        """It returns the names of the discovered functions as a list."""

        class View:
            """A view exposing a single implemented function."""

        View.__module__ = __name__
        View.implemented = staticmethod(_public_implemented)
        _public_implemented.__module__ = __name__

        result = get_charting_functions_list(View)
        assert isinstance(result, list)
        assert result == ["implemented"]

    def test_get_charting_functions_returns_name_callable_dict(self):
        """It discovers implemented functions as a name->callable mapping."""

        def _view_fn():
            """An implemented view function."""
            return None

        class View:
            """A view exposing a single implemented function."""

        View.__module__ = __name__
        View.view_chart = staticmethod(_view_fn)
        _view_fn.__module__ = __name__

        result = get_charting_functions(View)
        assert isinstance(result, dict)
        assert "view_chart" in result
        assert callable(result["view_chart"])


class TestModuleExports:
    """Tests confirming the module exposes the expected callables."""

    def test_callables_present(self):
        """It exposes all documented helper callables at module level."""
        for name in (
            "z_score_standardization",
            "calculate_returns",
            "should_share_axis",
            "heikin_ashi",
            "duration_sorter",
            "get_charting_functions",
            "get_charting_functions_list",
        ):
            assert callable(getattr(helpers, name))
