"""Tests for ``openbb_charting.core.plotly_ta.data_classes``."""

import numpy as np
import pandas as pd
import pytest

from openbb_charting.core.plotly_ta.data_classes import (
    Arguments,
    ChartIndicators,
    TA_Data,
    TA_DataException,
    TAIndicator,
    columns_regex,
)


@pytest.fixture
def ohlcv_df() -> pd.DataFrame:
    """Build a deterministic OHLCV frame indexed by date."""
    rng = np.random.default_rng(7)
    idx = pd.date_range("2023-01-01", periods=120, freq="D")
    close = 100 + np.cumsum(rng.normal(0, 1, 120))
    open_ = close + rng.normal(0, 0.5, 120)
    high = np.maximum(open_, close) + np.abs(rng.normal(0, 0.5, 120))
    low = np.minimum(open_, close) - np.abs(rng.normal(0, 0.5, 120))
    volume = rng.integers(1_000_000, 5_000_000, 120)
    frame = pd.DataFrame(
        {"open": open_, "high": high, "low": low, "close": close, "volume": volume},
        index=idx,
    )
    frame.index.name = "date"
    return frame


@pytest.fixture
def no_volume_df(ohlcv_df) -> pd.DataFrame:
    """Return an OHLCV frame whose volume is entirely zero."""
    frame = ohlcv_df.copy()
    frame["volume"] = 0
    return frame


class TestColumnsRegex:
    """Tests for the module-level ``columns_regex`` helper."""

    def test_matches_named_columns(self):
        """It returns columns matching the regex name."""
        df_ta = pd.DataFrame({"SMA_20": [1], "SMA_50": [2], "RSI_14": [3]})
        assert columns_regex(df_ta, "SMA") == ["SMA_20", "SMA_50"]

    def test_no_match_returns_empty(self):
        """It returns an empty list when nothing matches."""
        df_ta = pd.DataFrame({"close": [1.0]})
        assert columns_regex(df_ta, "DOES_NOT_EXIST") == []


class TestArguments:
    """Tests for the ``Arguments`` dataclass."""

    def test_single_element_list_collapses(self):
        """A one-element list is collapsed to its scalar value."""
        arg = Arguments(label="length", values=[20])
        assert arg.values == 20

    def test_multi_element_list_preserved(self):
        """A multi-element list is preserved as-is."""
        arg = Arguments(label="length", values=[20, 50])
        assert arg.values == [20, 50]

    def test_scalar_preserved(self):
        """A scalar value is preserved unchanged."""
        arg = Arguments(label="length", values=14)
        assert arg.values == 14


class TestTAIndicator:
    """Tests for the ``TAIndicator`` dataclass."""

    def test_iter_yields_arguments(self):
        """Iterating an indicator yields its arguments."""
        args = [Arguments("length", 14), Arguments("scalar", 3)]
        indicator = TAIndicator(name="rsi", args=args)
        assert list(indicator) == args

    def test_get_args_found(self):
        """``get_args`` returns the matching argument."""
        arg = Arguments("length", 14)
        indicator = TAIndicator(name="rsi", args=[arg])
        assert indicator.get_args("length") is arg

    def test_get_args_not_found(self):
        """``get_args`` returns None when the label is absent."""
        indicator = TAIndicator(name="rsi", args=[Arguments("length", 14)])
        assert indicator.get_args("missing") is None

    def test_get_argument_values_found(self):
        """``get_argument_values`` returns the matching values."""
        indicator = TAIndicator(name="rsi", args=[Arguments("length", 14)])
        assert indicator.get_argument_values("length") == 14

    def test_get_argument_values_not_found(self):
        """``get_argument_values`` returns an empty list when absent."""
        indicator = TAIndicator(name="rsi", args=[Arguments("length", 14)])
        assert indicator.get_argument_values("missing") == []


class TestChartIndicators:
    """Tests for the ``ChartIndicators`` dataclass."""

    def test_from_dict_builds_indicators(self):
        """``from_dict`` constructs indicators and arguments."""
        ci = ChartIndicators.from_dict({"sma": {"length": [20, 50]}})
        assert ci.indicators is not None
        assert ci.indicators[0].name == "sma"
        assert ci.indicators[0].args[0].label == "length"
        assert ci.indicators[0].args[0].values == [20, 50]

    def test_get_indicator_found(self):
        """``get_indicator`` returns the matching indicator."""
        ci = ChartIndicators.from_dict({"rsi": {"length": 14}})
        assert ci.get_indicator("rsi").name == "rsi"

    def test_get_indicator_not_found(self):
        """``get_indicator`` returns None when absent."""
        ci = ChartIndicators.from_dict({"rsi": {"length": 14}})
        assert ci.get_indicator("sma") is None

    def test_get_indicator_args_found(self):
        """``get_indicator_args`` returns argument values when present."""
        ci = ChartIndicators.from_dict({"rsi": {"length": 14}})
        assert ci.get_indicator_args("rsi", "length") == 14

    def test_get_indicator_args_label_missing(self):
        """``get_indicator_args`` returns None when the label is absent."""
        ci = ChartIndicators.from_dict({"rsi": {"length": 14}})
        assert ci.get_indicator_args("rsi", "missing") is None

    def test_get_indicator_args_indicator_missing(self):
        """``get_indicator_args`` returns None when the indicator is absent."""
        ci = ChartIndicators.from_dict({"rsi": {"length": 14}})
        assert ci.get_indicator_args("sma", "length") is None

    def test_get_indicators(self):
        """``get_indicators`` returns the underlying list."""
        ci = ChartIndicators.from_dict({"rsi": {"length": 14}})
        assert ci.get_indicators() == ci.indicators

    def test_get_params_with_indicators(self):
        """``get_params`` maps names to indicators."""
        ci = ChartIndicators.from_dict({"rsi": {"length": 14}})
        params = ci.get_params()
        assert set(params) == {"rsi"}
        assert isinstance(params["rsi"], TAIndicator)

    def test_get_params_without_indicators(self):
        """``get_params`` returns an empty dict when there are no indicators."""
        assert ChartIndicators(indicators=None).get_params() == {}

    def test_get_active_ids_with_indicators(self):
        """``get_active_ids`` returns the active indicator names."""
        ci = ChartIndicators.from_dict({"rsi": {"length": 14}, "sma": {"length": 20}})
        assert ci.get_active_ids() == ["rsi", "sma"]

    def test_get_active_ids_without_indicators(self):
        """``get_active_ids`` returns an empty list when there are none."""
        assert ChartIndicators(indicators=None).get_active_ids() == []

    def test_get_arg_names_found(self):
        """``get_arg_names`` returns argument labels for an indicator."""
        ci = ChartIndicators.from_dict({"macd": {"fast": 12, "slow": 26}})
        assert ci.get_arg_names("macd") == ["fast", "slow"]

    def test_get_arg_names_not_found(self):
        """``get_arg_names`` returns an empty list when indicator absent."""
        ci = ChartIndicators.from_dict({"macd": {"fast": 12}})
        assert ci.get_arg_names("rsi") == []

    def test_get_options_dict_with_options(self):
        """``get_options_dict`` maps labels to values when present."""
        ci = ChartIndicators.from_dict({"macd": {"fast": 12, "slow": 26}})
        assert ci.get_options_dict("macd") == {"fast": 12, "slow": 26}

    def test_get_options_dict_no_options(self):
        """``get_options_dict`` returns None when there are no arguments."""
        ci = ChartIndicators.from_dict({"obv": {}})
        assert ci.get_options_dict("obv") is None

    def test_get_available_indicators(self):
        """``get_available_indicators`` returns the literal name tuple."""
        available = ChartIndicators.get_available_indicators()
        assert "sma" in available
        assert "rsi" not in available
        assert isinstance(available, tuple)

    def test_remove_indicator(self):
        """``remove_indicator`` drops the named indicator."""
        ci = ChartIndicators.from_dict({"rsi": {"length": 14}, "sma": {"length": 20}})
        ci.remove_indicator("rsi")
        assert ci.get_active_ids() == ["sma"]

    def test_remove_indicator_no_indicators(self):
        """``remove_indicator`` is a no-op when there are no indicators."""
        ci = ChartIndicators(indicators=None)
        ci.remove_indicator("rsi")
        assert ci.indicators is None

    def test_to_dataframe_empty_input(self):
        """``to_dataframe`` returns the (empty) frame unchanged when empty."""
        ci = ChartIndicators.from_dict({"sma": {"length": 20}})
        empty = pd.DataFrame()
        result = ci.to_dataframe(empty)
        assert result.empty

    def test_to_dataframe_no_indicators(self, ohlcv_df):
        """``to_dataframe`` returns input unchanged when no indicators."""
        ci = ChartIndicators(indicators=None)
        result = ci.to_dataframe(ohlcv_df)
        assert list(result.columns) == list(ohlcv_df.columns)

    def test_to_dataframe_success(self, ohlcv_df):
        """``to_dataframe`` joins computed indicator columns."""
        ci = ChartIndicators.from_dict({"sma": {"length": 20}})
        result = ci.to_dataframe(ohlcv_df, ["sma"])
        assert any("SMA" in c for c in result.columns)

    def test_to_dataframe_swallows_exception(self, ohlcv_df):
        """``to_dataframe`` warns and returns input on processing error."""
        ci = ChartIndicators.from_dict({"sma": {"length": [20, 20]}})
        with pytest.warns(UserWarning):
            result = ci.to_dataframe(ohlcv_df, ["sma"])
        assert "SMA_20" not in result.columns

    def test_get_indicator_data_success(self, ohlcv_df):
        """``get_indicator_data`` returns indicator data for an indicator."""
        ci = ChartIndicators.from_dict({"sma": {"length": 20}})
        indicator = ci.get_indicator("sma")
        result = ci.get_indicator_data(ohlcv_df, indicator, length=20)
        assert result is not None

    def test_get_indicator_data_no_indicators(self, ohlcv_df):
        """``get_indicator_data`` returns None with no active indicators."""
        ci = ChartIndicators(indicators=None)
        indicator = TAIndicator(name="sma", args=[Arguments("length", 20)])
        assert ci.get_indicator_data(ohlcv_df, indicator, length=20) is None

    def test_get_indicator_data_swallows_exception(self):
        """``get_indicator_data`` warns and returns None on error."""
        ci = ChartIndicators.from_dict({"sma": {"length": 20}})
        indicator = ci.get_indicator("sma")
        bad = pd.DataFrame({"open": [1, 2, 3], "volume": [1, 2, 3]})
        with pytest.warns(UserWarning):
            assert ci.get_indicator_data(bad, indicator, length=20) is None


class TestTADataException:
    """Tests for the ``TA_DataException`` type."""

    def test_is_exception_subclass(self):
        """It is an ``Exception`` subclass that carries a message."""
        err = TA_DataException("boom")
        assert isinstance(err, Exception)
        assert str(err) == "boom"


class TestTAData:
    """Tests for the ``TA_Data`` processing class."""

    def test_init_from_series(self, ohlcv_df):
        """A Series input is converted to a DataFrame internally."""
        ci = ChartIndicators.from_dict({"sma": {"length": 20}})
        series = ohlcv_df["close"].rename("close")
        td = TA_Data(series, ci)
        assert isinstance(td.df_ta, pd.DataFrame)
        assert td.close_col == "close"

    def test_init_from_dict_indicators(self, ohlcv_df):
        """A dict of indicators is converted to ``ChartIndicators``."""
        td = TA_Data(ohlcv_df, {"sma": {"length": 20}})
        assert isinstance(td.indicators, ChartIndicators)

    def test_init_default_ma_mode(self, ohlcv_df):
        """The default moving-average modes are used when none given."""
        td = TA_Data(ohlcv_df, ChartIndicators.from_dict({"sma": {"length": 20}}))
        assert td.ma_mode == ["sma", "ema", "wma", "hma", "zlma", "rma"]

    def test_init_no_close_raises(self):
        """Construction raises when no close column can be resolved."""
        bad = pd.DataFrame({"high": [1, 2], "low": [1, 2], "open": [1, 2]})
        with pytest.raises(IndexError):
            TA_Data(bad, ChartIndicators.from_dict({"sma": {"length": 20}}))

    def test_init_has_volume_flag(self, ohlcv_df, no_volume_df):
        """The ``has_volume`` flag reflects whether volume sums above zero."""
        ci = ChartIndicators.from_dict({"sma": {"length": 20}})
        assert TA_Data(ohlcv_df, ci).has_volume is True
        assert TA_Data(no_volume_df, ci).has_volume is False

    def test_get_indicator_data_ma_list(self, ohlcv_df):
        """A list length for an MA indicator yields one column per length."""
        ci = ChartIndicators.from_dict({"sma": {"length": [20, 50]}})
        td = TA_Data(ohlcv_df, ci)
        out = td.get_indicator_data(ci.get_indicator("sma"), length=[20, 50])
        assert {"SMA_20", "SMA_50"} <= set(out.columns)

    def test_get_indicator_data_ma_scalar(self, ohlcv_df):
        """A scalar length for an MA indicator yields a single series."""
        ci = ChartIndicators.from_dict({"ema": {"length": 20}})
        td = TA_Data(ohlcv_df, ci)
        out = td.get_indicator_data(ci.get_indicator("ema"), length=20)
        assert out is not None

    def test_get_indicator_data_zlma_renamed(self, ohlcv_df):
        """ZLMA output is renamed from the pandas_ta ZL_EMA name."""
        ci = ChartIndicators.from_dict({"zlma": {"length": 20}})
        td = TA_Data(ohlcv_df, ci)
        out = td.get_indicator_data(ci.get_indicator("zlma"), length=20)
        assert "ZLMA" in out.name

    def test_get_indicator_data_vwap(self, ohlcv_df):
        """VWAP is computed from its declared columns."""
        ci = ChartIndicators.from_dict({"vwap": {}})
        td = TA_Data(ohlcv_df, ci)
        out = td.get_indicator_data(ci.get_indicator("vwap"))
        assert out is not None

    def test_get_indicator_data_columns_with_use_open(self, ohlcv_df):
        """A columns indicator appends open when ``use_open`` is True."""
        ci = ChartIndicators.from_dict({"stoch": {"use_open": True}})
        td = TA_Data(ohlcv_df, ci)
        out = td.get_indicator_data(ci.get_indicator("stoch"))
        assert out is not None

    def test_get_indicator_data_columns_without_use_open(self, ohlcv_df):
        """A columns indicator omits open when ``use_open`` is absent."""
        ci = ChartIndicators.from_dict({"adx": {}})
        td = TA_Data(ohlcv_df, ci)
        out = td.get_indicator_data(ci.get_indicator("adx"), length=14)
        assert out is not None

    def test_get_indicator_data_default_branch(self, ohlcv_df):
        """A non-MA, non-columns indicator is computed from close."""
        ci = ChartIndicators.from_dict({"rsi": {"length": 14}})
        td = TA_Data(ohlcv_df, ci)
        out = td.get_indicator_data(ci.get_indicator("rsi"), length=14)
        assert out is not None

    def test_get_indicator_data_scalar_returns_none(self, ohlcv_df):
        """A scalar length larger than the data yields None directly."""
        ci = ChartIndicators.from_dict({"sma": {"length": 5000}})
        td = TA_Data(ohlcv_df, ci)
        out = td.get_indicator_data(ci.get_indicator("sma"), length=5000)
        assert out is None

    def test_get_indicator_data_empty_returns_none(self, ohlcv_df):
        """An all-NaN indicator output is dropped to None after dropna."""
        ci = ChartIndicators.from_dict({"sma": {"length": [5000, 6000]}})
        td = TA_Data(ohlcv_df, ci)
        out = td.get_indicator_data(ci.get_indicator("sma"), length=[5000, 6000])
        assert out is None

    def test_to_dataframe_no_active_indicators(self, ohlcv_df):
        """``to_dataframe`` returns None when there are no indicators."""
        ci = ChartIndicators(indicators=None)
        td = TA_Data(ohlcv_df, ci)
        assert td.to_dataframe() is None

    def test_to_dataframe_skips_volume_indicator_without_volume(self, no_volume_df):
        """Volume-requiring indicators are skipped when volume is absent."""
        ci = ChartIndicators.from_dict({"obv": {}})
        td = TA_Data(no_volume_df, ci)
        out = td.to_dataframe()
        assert not any("OBV" in c for c in out.columns)

    def test_to_dataframe_skips_overlay_only_indicators(self, ohlcv_df):
        """Overlay-only indicators (fib/srlines/...) are skipped."""
        ci = ChartIndicators.from_dict({"fib": {}})
        td = TA_Data(ohlcv_df, ci)
        out = td.to_dataframe()
        assert list(out.columns) == list(ohlcv_df.columns)

    def test_to_dataframe_joins_indicator(self, ohlcv_df):
        """``to_dataframe`` joins and interpolates computed indicators."""
        ci = ChartIndicators.from_dict({"sma": {"length": 20}})
        td = TA_Data(ohlcv_df, ci)
        out = td.to_dataframe()
        assert any("SMA" in c for c in out.columns)

    def test_to_dataframe_raises_on_indicator_error(self, ohlcv_df):
        """``to_dataframe`` wraps indicator errors in ``TA_DataException``."""
        ci = ChartIndicators.from_dict({"sma": {"length": [20, 20]}})
        td = TA_Data(ohlcv_df, ci)
        with pytest.raises(TA_DataException, match="Error processing indicator sma"):
            td.to_dataframe()
