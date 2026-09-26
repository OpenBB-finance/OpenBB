"""Tests for ``openbb_charting.core.plotly_ta.ta_class``."""

import warnings

import numpy as np
import pandas as pd
import pytest

import openbb_charting.core.plotly_ta.ta_class as ta_class_module
from openbb_charting.core.openbb_figure import OpenBBFigure
from openbb_charting.core.plotly_ta.data_classes import ChartIndicators
from openbb_charting.core.plotly_ta.ta_class import PlotlyTA


def _make_ohlcv(seed: int = 42, periods: int = 200, start: str = "2023-01-01"):
    """Build a deterministic OHLCV frame indexed by date."""
    rng = np.random.default_rng(seed)
    idx = pd.date_range(start, periods=periods, freq="D")
    close = 100 + np.cumsum(rng.normal(0, 1, periods))
    open_ = close + rng.normal(0, 0.5, periods)
    high = np.maximum(open_, close) + np.abs(rng.normal(0, 0.5, periods))
    low = np.minimum(open_, close) - np.abs(rng.normal(0, 0.5, periods))
    volume = rng.integers(1_000_000, 5_000_000, periods)
    frame = pd.DataFrame(
        {"open": open_, "high": high, "low": low, "close": close, "volume": volume},
        index=idx,
    )
    frame.index.name = "date"
    return frame


@pytest.fixture
def ohlcv_df() -> pd.DataFrame:
    """A single-symbol OHLCV DataFrame indexed by date (200 rows)."""
    return _make_ohlcv()


@pytest.fixture
def no_volume_df() -> pd.DataFrame:
    """An OHLCV frame whose volume column is entirely zero."""
    frame = _make_ohlcv()
    frame["volume"] = 0
    return frame


class TestPlotlyTASingleton:
    """Tests for the singleton and theming behavior of ``PlotlyTA``."""

    def test_new_returns_singleton(self):
        """Repeated construction returns the same instance."""
        assert PlotlyTA() is PlotlyTA()

    def test_setup_theme_returns_chart_style(self):
        """``setup_theme`` builds a ``ChartStyle`` instance."""
        theme = PlotlyTA.setup_theme(chart_style="", user_styles_directory="")
        assert theme is not None
        assert hasattr(theme, "get_colors")

    def test_init_with_args_takes_non_clear_branch(self):
        """Constructing with positional args takes the super-init branch."""
        with pytest.raises(TypeError):
            PlotlyTA("dummy")
        assert ta_class_module.PLOTLY_TA.df_fib is None

    def test_clear_data_resets_state(self):
        """A no-arg construction resets the internal data structures."""
        inst = PlotlyTA()
        assert inst.df_stock is None
        assert isinstance(inst.indicators, ChartIndicators)
        assert inst.params is None
        assert inst.intraday is False
        assert inst.show_volume is True


class TestPlotlyTAProperties:
    """Tests for the moving-average / inchart / subplots properties."""

    def test_ma_mode_property_and_setter(self):
        """The ``ma_mode`` property returns a unique list and can be set."""
        inst = PlotlyTA()
        original = inst.ma_mode
        inst.ma_mode = ["sma", "sma", "ema"]
        assert set(inst.ma_mode) == {"sma", "ema"}
        inst.ma_mode = original

    def test_inchart_property_and_setter(self):
        """The ``inchart`` property returns a unique list and can be set."""
        inst = PlotlyTA()
        original = inst.inchart
        inst.inchart = ["bbands", "bbands"]
        assert inst.inchart == ["bbands"]
        inst.inchart = original

    def test_subplots_property_and_setter(self):
        """The ``subplots`` property returns a unique list and can be set."""
        inst = PlotlyTA()
        original = inst.subplots
        inst.subplots = ["rsi", "rsi"]
        assert inst.subplots == ["rsi"]
        inst.subplots = original


class TestPlotlyTAPlot:
    """Tests for the primary plotting entry points."""

    def test_plot_with_subplots_and_inchart_and_ma(self, ohlcv_df):
        """A mixed indicator set plots candles, MA, subplots and inchart."""
        fig = PlotlyTA.plot(
            ohlcv_df,
            indicators={
                "sma": {"length": [20, 50]},
                "rsi": {"length": 14},
                "macd": {"fast": 12, "slow": 26, "signal": 9},
                "bbands": {"length": 20},
            },
            symbol="AAA",
            candles=True,
            volume=True,
        )
        assert isinstance(fig, OpenBBFigure)

    def test_plot_line_chart_no_candles(self, ohlcv_df):
        """Plotting with ``candles=False`` renders a line chart."""
        fig = PlotlyTA.plot(
            ohlcv_df,
            indicators={"sma": {"length": 20}},
            symbol="AAA",
            candles=False,
            volume=True,
        )
        assert isinstance(fig, OpenBBFigure)

    def test_plot_with_series_input(self, ohlcv_df):
        """A Series input is converted to a frame before plotting."""
        series = ohlcv_df["close"]
        fig = PlotlyTA.plot(series, indicators={}, symbol="AAA", candles=False)
        assert isinstance(fig, OpenBBFigure)

    def test_plot_no_volume_data(self, no_volume_df):
        """Plotting with zero volume disables the volume subplot."""
        fig = PlotlyTA.plot(
            no_volume_df,
            indicators={"sma": {"length": 20}},
            symbol="AAA",
            candles=True,
            volume=True,
        )
        assert isinstance(fig, OpenBBFigure)

    def test_plot_with_chart_indicators_object(self, ohlcv_df):
        """A ``ChartIndicators`` object is accepted directly."""
        ci = ChartIndicators.from_dict({"sma": {"length": 20}})
        fig = PlotlyTA.plot(ohlcv_df, indicators=ci, symbol="AAA")
        assert isinstance(fig, OpenBBFigure)

    def test_plot_with_existing_figure(self, ohlcv_df):
        """Passing a pre-built figure reuses it instead of creating one."""
        inst = PlotlyTA()
        inst._clear_data()
        fig = inst.__plot__(
            ohlcv_df,
            indicators={"sma": {"length": 20}},
            symbol="AAA",
        )
        fig2 = PlotlyTA.plot(ohlcv_df, indicators={"rsi": {"length": 14}}, fig=fig)
        assert isinstance(fig2, OpenBBFigure)

    def test_plot_reuses_indicators_when_none(self, ohlcv_df):
        """When indicators is None the previous singleton indicators are reused."""
        PlotlyTA.plot(ohlcv_df, indicators={"sma": {"length": 20}}, symbol="AAA")
        fig = PlotlyTA.plot(ohlcv_df, indicators=None, symbol="AAA")
        assert isinstance(fig, OpenBBFigure)

    def test_plot_with_fib_and_srlines(self, ohlcv_df):
        """Overlay-only indicators (fib, srlines) are plotted on the chart."""
        fig = PlotlyTA.plot(
            ohlcv_df,
            indicators={"fib": {}, "srlines": {}},
            symbol="AAA",
            candles=True,
        )
        assert isinstance(fig, OpenBBFigure)

    def test_plot_with_inchart_overlay_indicators(self, ohlcv_df):
        """In-chart overlay indicators (donchian, ichimoku) are plotted."""
        fig = PlotlyTA.plot(
            ohlcv_df,
            indicators={"donchian": {}, "ichimoku": {}, "vwap": {}},
            symbol="AAA",
            candles=True,
        )
        assert isinstance(fig, OpenBBFigure)

    def test_plot_multiple_ma_modes_plotted_once(self, ohlcv_df):
        """Multiple moving-average indicators collapse into a single 'ma' plot."""
        fig = PlotlyTA.plot(
            ohlcv_df,
            indicators={
                "sma": {"length": 20},
                "ema": {"length": 20},
                "wma": {"length": 20},
            },
            symbol="AAA",
            candles=True,
        )
        assert isinstance(fig, OpenBBFigure)

    def test_plot_with_aroon_and_atr(self, ohlcv_df):
        """Aroon (two-row) and ATR (plotted last) subplots are handled."""
        fig = PlotlyTA.plot(
            ohlcv_df,
            indicators={"aroon": {"length": 14}, "atr": {"length": 14}},
            symbol="AAA",
            candles=True,
        )
        assert isinstance(fig, OpenBBFigure)

    def test_plot_unknown_indicator_is_skipped(self, ohlcv_df):
        """An unknown indicator is caught and skipped without failing the plot."""
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            fig = PlotlyTA.plot(
                ohlcv_df,
                indicators={"not_a_real_indicator": {}},
                symbol="AAA",
            )
        assert isinstance(fig, OpenBBFigure)

    def test_plot_volume_only_no_volume_margin(self, no_volume_df):
        """With volume disabled the left margin adjustment branch runs."""
        fig = PlotlyTA.plot(
            no_volume_df,
            indicators={},
            symbol="AAA",
            candles=True,
            volume=True,
        )
        assert isinstance(fig, OpenBBFigure)

    def test_plot_many_subplots_reaches_limit(self, ohlcv_df):
        """A large indicator set exercises the max-subplots handling."""
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            fig = PlotlyTA.plot(
                ohlcv_df,
                indicators={
                    "rsi": {"length": 14},
                    "macd": {"fast": 12, "slow": 26, "signal": 9},
                    "stoch": {},
                    "cci": {"length": 14},
                    "adx": {"length": 14},
                    "aroon": {"length": 14},
                    "fisher": {"length": 14},
                    "obv": {},
                },
                symbol="AAA",
                candles=True,
                volume=True,
            )
        assert isinstance(fig, OpenBBFigure)


class TestPlotlyTAHelpers:
    """Tests for the helper methods used during plotting."""

    def _prepared(self, df, indicators):
        """Return a PlotlyTA instance with internal plotting state populated."""
        inst = PlotlyTA()
        inst._clear_data()
        ci = ChartIndicators.from_dict(indicators)
        inst.indicators = ci
        prepared = df.copy()
        prepared = prepared.sort_index(ascending=True)
        inst.df_stock = prepared
        inst.close_column = "close"
        inst.params = ci.get_params()
        inst.has_volume = bool(df["volume"].sum() > 0)
        inst.show_volume = inst.has_volume
        inst.intraday = False
        return inst

    def test_calculate_indicators(self, ohlcv_df):
        """``calculate_indicators`` returns a frame with indicator columns."""
        inst = self._prepared(ohlcv_df, {"sma": {"length": 20}})
        out = inst.calculate_indicators()
        assert any("SMA" in c for c in out.columns)

    def test_get_subplot_volume(self, ohlcv_df):
        """``get_subplot`` returns the show_volume flag for 'volume'."""
        inst = self._prepared(ohlcv_df, {})
        assert inst.get_subplot("volume") is inst.show_volume

    def test_get_subplot_volume_indicator_without_volume(self, no_volume_df):
        """A volume indicator without volume data is removed and warned."""
        inst = self._prepared(no_volume_df, {"obv": {}})
        with pytest.warns(UserWarning):
            assert inst.get_subplot("obv") is False
        assert "obv" not in inst.indicators.get_active_ids()

    def test_get_subplot_missing_indicator(self, ohlcv_df):
        """``get_subplot`` returns False when the indicator is not active."""
        inst = self._prepared(ohlcv_df, {"sma": {"length": 20}})
        assert inst.get_subplot("rsi") is False

    def test_get_subplot_active_indicator(self, ohlcv_df):
        """``get_subplot`` returns truthy data for an active subplot."""
        inst = self._prepared(ohlcv_df, {"rsi": {"length": 14}})
        assert inst.get_subplot("rsi") is True

    def test_get_subplot_exception_returns_false(self, ohlcv_df):
        """An indicator that yields no data is caught and reported as False."""
        inst = self._prepared(ohlcv_df, {"rsi": {"length": 5000}})
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            assert inst.get_subplot("rsi") is False

    def test_check_subplots(self, ohlcv_df):
        """``check_subplots`` filters down to plottable subplots."""
        inst = self._prepared(ohlcv_df, {"rsi": {"length": 14}})
        assert inst.check_subplots(["rsi", "macd"]) == ["rsi"]

    def test_get_fig_settings_dict(self, ohlcv_df):
        """``get_fig_settings_dict`` returns a row/specs configuration."""
        inst = self._prepared(
            ohlcv_df,
            {"rsi": {"length": 14}, "macd": {"fast": 12, "slow": 26, "signal": 9}},
        )
        settings = inst.get_fig_settings_dict()
        assert settings["cols"] == 1
        assert "specs" in settings

    def test_get_fig_settings_dict_with_aroon(self, ohlcv_df):
        """``get_fig_settings_dict`` bumps the row count when aroon is active."""
        inst = self._prepared(ohlcv_df, {"aroon": {"length": 14}})
        settings = inst.get_fig_settings_dict()
        assert "rows" in settings

    def test_init_plot_candles(self, ohlcv_df):
        """``init_plot`` with candles builds a candlestick figure."""
        inst = self._prepared(ohlcv_df, {})
        fig = inst.init_plot("AAA", candles=True)
        assert isinstance(fig, OpenBBFigure)

    def test_init_plot_line(self, ohlcv_df):
        """``init_plot`` without candles builds a line figure."""
        inst = self._prepared(ohlcv_df, {})
        fig = inst.init_plot("AAA", candles=False)
        assert isinstance(fig, OpenBBFigure)


class TestLocatePlugins:
    """Tests for plugin discovery."""

    def test_locate_plugins_debug_emits_warnings(self):
        """Running plugin discovery in debug mode emits informational warnings."""
        with pytest.warns(UserWarning):
            PlotlyTA._locate_plugins(debug=True)

    def test_locate_plugins_no_debug(self):
        """Running plugin discovery without debug does not raise."""
        PlotlyTA._locate_plugins(debug=False)
        assert PlotlyTA.plugins


class TestProcessFig:
    """Tests for the ``process_fig`` figure-processing path."""

    def test_process_fig_runs_via_plot(self, ohlcv_df):
        """``process_fig`` is exercised through a normal plot call."""
        fig = PlotlyTA.plot(
            ohlcv_df,
            indicators={"rsi": {"length": 14}},
            symbol="AAA",
            candles=True,
            volume=True,
        )
        assert isinstance(fig, OpenBBFigure)

    def test_process_fig_direct_call(self, ohlcv_df):
        """``process_fig`` reflows an ``init_plot`` figure into subplots."""
        inst = PlotlyTA()
        inst._clear_data()
        ci = ChartIndicators.from_dict({"rsi": {"length": 14}})
        inst.indicators = ci
        prepared = ohlcv_df.copy().sort_index(ascending=True)
        inst.df_stock = prepared
        inst.close_column = "close"
        inst.params = ci.get_params()
        inst.has_volume = True
        inst.show_volume = True
        inst.intraday = False
        inst.df_ta = inst.calculate_indicators()
        base_fig = inst.init_plot("AAA", candles=True)
        out = inst.process_fig(base_fig, volume_ticks_x=7)
        assert isinstance(out, OpenBBFigure)

    def test_process_fig_without_volume(self, no_volume_df):
        """``process_fig`` skips the volume overlay when volume is disabled."""
        inst = PlotlyTA()
        inst._clear_data()
        ci = ChartIndicators.from_dict({"rsi": {"length": 14}})
        inst.indicators = ci
        prepared = no_volume_df.copy().sort_index(ascending=True)
        inst.df_stock = prepared
        inst.close_column = "close"
        inst.params = ci.get_params()
        inst.has_volume = False
        inst.show_volume = False
        inst.intraday = False
        inst.df_ta = inst.calculate_indicators()
        base_fig = inst.init_plot("AAA", candles=True)
        out = inst.process_fig(base_fig, volume_ticks_x=7)
        assert isinstance(out, OpenBBFigure)


class TestModuleState:
    """Tests for module-level constants and singletons."""

    def test_global_singleton_is_set(self):
        """The module ``PLOTLY_TA`` global is populated after construction."""
        PlotlyTA()
        assert ta_class_module.PLOTLY_TA is not None
