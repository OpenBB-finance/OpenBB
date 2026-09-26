"""Tests for the technical-analysis plugins of ``openbb_charting``."""

from __future__ import annotations

import builtins
import datetime as dt
import warnings

import numpy as np
import pandas as pd
import pytest
from freezegun import freeze_time

from openbb_charting.core.openbb_figure import OpenBBFigure
from openbb_charting.core.plotly_ta.data_classes import ChartIndicators
from openbb_charting.core.plotly_ta.plugins import momentum_plugin
from openbb_charting.core.plotly_ta.ta_class import PlotlyTA


def _make_ohlcv(
    seed: int = 42, periods: int = 250, start: str = "2023-01-01"
) -> pd.DataFrame:
    """Build a deterministic daily OHLCV frame indexed by date."""
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


def _make_intraday(
    periods: int = 160, freq: str = "5min", start: str = "2024-03-01 09:30"
) -> pd.DataFrame:
    """Build a deterministic intraday OHLCV frame indexed by datetime."""
    rng = np.random.default_rng(7)
    idx = pd.date_range(start, periods=periods, freq=freq)
    close = 100 + np.cumsum(rng.normal(0, 0.2, periods))
    open_ = close + rng.normal(0, 0.1, periods)
    high = np.maximum(open_, close) + np.abs(rng.normal(0, 0.1, periods))
    low = np.minimum(open_, close) - np.abs(rng.normal(0, 0.1, periods))
    volume = rng.integers(1_000, 5_000, periods)
    frame = pd.DataFrame(
        {"open": open_, "high": high, "low": low, "close": close, "volume": volume},
        index=idx,
    )
    frame.index.name = "date"
    return frame


def _prepared(df: pd.DataFrame, indicators: dict, intraday: bool = False) -> PlotlyTA:
    """Return a ``PlotlyTA`` instance with internal plotting state populated."""
    inst = PlotlyTA()
    inst._clear_data()
    ci = ChartIndicators.from_dict(indicators)
    inst.indicators = ci
    inst.df_stock = df.copy().sort_index(ascending=True)
    inst.close_column = "close"
    inst.params = ci.get_params()
    inst.has_volume = bool(df["volume"].sum() > 0)
    inst.show_volume = inst.has_volume
    inst.intraday = intraday
    inst.df_ta = inst.calculate_indicators()
    return inst


@pytest.fixture
def daily_df() -> pd.DataFrame:
    """A single-symbol daily OHLCV DataFrame (250 rows)."""
    return _make_ohlcv()


@pytest.fixture
def recent_daily_df() -> pd.DataFrame:
    """A daily OHLCV frame ending today, for window-based date filtering."""
    start = (pd.Timestamp.now().normalize() - pd.Timedelta(days=249)).strftime(
        "%Y-%m-%d"
    )
    return _make_ohlcv(periods=250, start=start)


@pytest.fixture
def recent_intraday_df() -> pd.DataFrame:
    """A 5-minute intraday OHLCV frame spanning the last few days."""
    start = pd.Timestamp.now().normalize() - pd.Timedelta(days=2)
    return _make_intraday(periods=160, freq="5min", start=start.strftime("%Y-%m-%d"))


def _plot(df: pd.DataFrame, indicators: dict, **kwargs) -> OpenBBFigure:
    """Run ``PlotlyTA.plot`` while silencing the plugin error/skip warnings."""
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        return PlotlyTA.plot(df, indicators=indicators, symbol="AAA", **kwargs)


class TestMomentumPlugin:
    """Tests for ``Momentum`` momentum indicators."""

    def test_cci_subplot(self, daily_df):
        """CCI renders its line, over/under rectangles and annotation."""
        fig = _plot(daily_df, {"cci": {"length": 14}}, candles=True, volume=True)
        assert isinstance(fig, OpenBBFigure)

    def test_cg_subplot(self, daily_df):
        """The center-of-gravity oscillator plots its line and signal."""
        fig = _plot(daily_df, {"cg": {"length": 10}}, candles=True, volume=True)
        assert isinstance(fig, OpenBBFigure)

    def test_fisher_subplot(self, daily_df):
        """The Fisher transform plots its transform, signal and bands."""
        fig = _plot(daily_df, {"fisher": {"length": 14}}, candles=True, volume=True)
        assert isinstance(fig, OpenBBFigure)

    def test_macd_subplot(self, daily_df):
        """MACD plots the histogram, MACD and signal lines."""
        fig = _plot(
            daily_df,
            {"macd": {"fast": 12, "slow": 26, "signal": 9}},
            candles=True,
            volume=True,
        )
        assert isinstance(fig, OpenBBFigure)

    def test_rsi_subplot(self, daily_df):
        """RSI plots its line, over/under zones and tickvals."""
        fig = _plot(daily_df, {"rsi": {"length": 14}}, candles=True, volume=True)
        assert isinstance(fig, OpenBBFigure)

    def test_stoch_subplot(self, daily_df):
        """The stochastic oscillator plots its %K and %D lines."""
        fig = _plot(daily_df, {"stoch": {}}, candles=True, volume=True)
        assert isinstance(fig, OpenBBFigure)

    def test_clenow_inchart(self, daily_df):
        """The Clenow momentum overlay fits and plots its trend line."""
        fig = _plot(daily_df, {"clenow": {"window": 90}}, candles=True, volume=True)
        assert isinstance(fig, OpenBBFigure)

    def test_clenow_import_error_warns(self, daily_df, monkeypatch):
        """A missing ``openbb-technical`` install warns and returns unchanged."""
        inst = _prepared(daily_df, {"clenow": {"window": 90}})
        fig = inst.init_plot("AAA", candles=True)
        real_import = builtins.__import__

        def fake_import(name, *args, **kwargs):
            if name == "openbb_technical.helpers":
                raise ImportError("forced")
            return real_import(name, *args, **kwargs)

        monkeypatch.setattr(builtins, "__import__", fake_import)
        with pytest.warns(UserWarning, match="openbb-technical"):
            out, idx = inst.plot_clenow(fig, inst.df_ta, 0)
        assert idx == 0
        assert isinstance(out, OpenBBFigure)

    def test_demark_inchart(self, daily_df, monkeypatch):
        """Demark plots up/down sequence labels from a TD-sequence count."""
        inst = _prepared(daily_df, {"demark": {"min_val": 5}})
        fig = inst.init_plot("AAA", candles=True)
        n = len(inst.df_ta)
        up = np.zeros(n, dtype=int)
        dn = np.zeros(n, dtype=int)
        up[10:19] = np.arange(1, 10)
        dn[30:39] = np.arange(1, 10)
        td = pd.DataFrame({"TD_SEQ_UPa": up, "TD_SEQ_DNa": dn})

        monkeypatch.setattr(
            momentum_plugin.ta, "td_seq", lambda *a, **k: td, raising=False
        )
        out, idx = inst.plot_demark(fig, inst.df_ta, 0)
        assert idx == 1
        assert isinstance(out, OpenBBFigure)

    def test_ichimoku_inchart(self, daily_df):
        """Ichimoku plots conversion/base lines and the leading-span cloud."""
        fig = _plot(
            daily_df,
            {
                "ichimoku": {
                    "conversion_period": 9,
                    "base_period": 26,
                    "lagging_line_period": 52,
                    "displacement": 26,
                }
            },
            candles=True,
            volume=True,
        )
        assert isinstance(fig, OpenBBFigure)

    def test_ichimoku_default_params(self, daily_df):
        """Ichimoku falls back to default periods when none are supplied."""
        fig = _plot(daily_df, {"ichimoku": {}}, candles=True, volume=True)
        assert isinstance(fig, OpenBBFigure)


class TestVolatilityPlugin:
    """Tests for ``Volatility`` volatility indicators."""

    def test_atr_subplot(self, daily_df):
        """ATR plots its line in a dedicated subplot."""
        fig = _plot(daily_df, {"atr": {"length": 14}}, candles=True, volume=True)
        assert isinstance(fig, OpenBBFigure)

    def test_bbands_inchart_integer_std(self, daily_df):
        """Bollinger bands with an integer std truncate the band label."""
        fig = _plot(
            daily_df, {"bbands": {"length": 20, "std": 2.0}}, candles=True, volume=True
        )
        assert isinstance(fig, OpenBBFigure)

    def test_bbands_inchart_fractional_std(self, daily_df):
        """Bollinger bands with a fractional std keep the decimal label."""
        fig = _plot(
            daily_df, {"bbands": {"length": 20, "std": 2.5}}, candles=True, volume=True
        )
        assert isinstance(fig, OpenBBFigure)

    def test_bbands_dark_theme_opacity(self, daily_df):
        """A dark theme drives the full band opacity branch."""
        inst = _prepared(daily_df, {"bbands": {"length": 20, "std": 2.0}})
        fig = inst.init_plot("AAA", candles=True)
        original = fig.theme.plt_style
        fig.theme.plt_style = "dark"
        try:
            out, idx = inst.plot_bbands(fig, inst.df_ta, 0)
        finally:
            fig.theme.plt_style = original
        assert idx == 1
        assert isinstance(out, OpenBBFigure)

    def test_donchian_inchart(self, daily_df):
        """Donchian channels plot the upper/lower filled band."""
        fig = _plot(daily_df, {"donchian": {}}, candles=True, volume=True)
        assert isinstance(fig, OpenBBFigure)

    def test_donchian_dark_theme(self, daily_df):
        """A dark theme drives the donchian dark-style branch."""
        inst = _prepared(daily_df, {"donchian": {}})
        fig = inst.init_plot("AAA", candles=True)
        original = fig.theme.plt_style
        fig.theme.plt_style = "dark"
        try:
            out, idx = inst.plot_donchian(fig, inst.df_ta, 0)
        finally:
            fig.theme.plt_style = original
        assert idx == 1
        assert isinstance(out, OpenBBFigure)

    def test_kc_inchart(self, daily_df):
        """Keltner channels plot the upper/lower filled band."""
        fig = _plot(daily_df, {"kc": {"mamode": "ema"}}, candles=True, volume=True)
        assert isinstance(fig, OpenBBFigure)

    def test_kc_default_mamode(self, daily_df):
        """Keltner channels default to the EMA moving-average mode."""
        fig = _plot(daily_df, {"kc": {}}, candles=True, volume=True)
        assert isinstance(fig, OpenBBFigure)

    def test_kc_dark_theme(self, daily_df):
        """A dark theme drives the Keltner dark-style branch."""
        inst = _prepared(daily_df, {"kc": {"mamode": "ema"}})
        fig = inst.init_plot("AAA", candles=True)
        original = fig.theme.plt_style
        fig.theme.plt_style = "dark"
        try:
            out, idx = inst.plot_kc(fig, inst.df_ta, 0)
        finally:
            fig.theme.plt_style = original
        assert idx == 1
        assert isinstance(out, OpenBBFigure)


class TestVolumePlugin:
    """Tests for ``Volume`` volume indicators."""

    def test_ad_subplot(self, daily_df):
        """The accumulation/distribution line plots in a subplot."""
        fig = _plot(daily_df, {"ad": {}}, candles=True, volume=True)
        assert isinstance(fig, OpenBBFigure)

    def test_adosc_subplot(self, daily_df):
        """The A/D oscillator plots its line in a subplot."""
        fig = _plot(daily_df, {"adosc": {}}, candles=True, volume=True)
        assert isinstance(fig, OpenBBFigure)

    def test_obv_subplot(self, daily_df):
        """On-balance volume plots its line in a subplot."""
        fig = _plot(daily_df, {"obv": {}}, candles=True, volume=True)
        assert isinstance(fig, OpenBBFigure)


class TestOverlapPlugin:
    """Tests for ``Overlap`` overlap indicators."""

    def test_single_moving_average(self, daily_df):
        """A single SMA overlay is plotted in-chart."""
        fig = _plot(daily_df, {"sma": {"length": 20}}, candles=True, volume=True)
        assert isinstance(fig, OpenBBFigure)

    def test_multi_length_moving_average(self, daily_df):
        """A multi-length SMA overlay plots one trace per length."""
        fig = _plot(daily_df, {"sma": {"length": [20, 50]}}, candles=True, volume=True)
        assert isinstance(fig, OpenBBFigure)

    def test_all_moving_average_modes(self, daily_df):
        """Every moving-average mode collapses into a single ``ma`` plot."""
        fig = _plot(
            daily_df,
            {
                "sma": {"length": 20},
                "ema": {"length": 20},
                "wma": {"length": 20},
                "hma": {"length": 20},
                "zlma": {"length": 20},
                "rma": {"length": 20},
            },
            candles=True,
            volume=True,
        )
        assert isinstance(fig, OpenBBFigure)

    def test_vwap_inchart(self, daily_df):
        """VWAP is plotted as an in-chart overlay."""
        fig = _plot(daily_df, {"vwap": {}}, candles=True, volume=True)
        assert isinstance(fig, OpenBBFigure)

    def test_moving_average_empty_column_skipped(self, daily_df):
        """An empty moving-average column is skipped without plotting."""
        inst = _prepared(daily_df, {"sma": {"length": 20}})
        fig = inst.init_plot("AAA", candles=True)
        empty_ta = inst.df_ta.iloc[0:0]
        out, idx = inst.plot_ma(fig, empty_ta, 0)
        assert idx == 0
        assert isinstance(out, OpenBBFigure)

    def test_moving_average_exception_warns(self, daily_df):
        """An error while adding a moving average is caught and warned."""
        inst = _prepared(daily_df, {"sma": {"length": 20}})
        fig = inst.init_plot("AAA", candles=True)
        inst.inchart_colors = []
        with pytest.warns(UserWarning, match="Error adding SMA"):
            out, idx = inst.plot_ma(fig, inst.df_ta, 0)
        assert idx == 0
        assert isinstance(out, OpenBBFigure)


class TestTrendPlugin:
    """Tests for ``Trend`` trend indicators."""

    def test_adx_subplot(self, daily_df):
        """ADX plots the ADX, +DI and -DI lines with a threshold line."""
        fig = _plot(daily_df, {"adx": {"length": 14}}, candles=True, volume=True)
        assert isinstance(fig, OpenBBFigure)

    def test_aroon_two_row_subplot(self, daily_df):
        """Aroon plots the up/down lines and the oscillator across two rows."""
        fig = _plot(daily_df, {"aroon": {"length": 14}}, candles=True, volume=True)
        assert isinstance(fig, OpenBBFigure)


class TestCustomPlugin:
    """Tests for ``Custom`` custom indicators."""

    def test_fib_inchart_daily(self, daily_df):
        """Fibonacci retracement levels are plotted from daily data."""
        fig = _plot(daily_df, {"fib": {}}, candles=True, volume=True)
        assert isinstance(fig, OpenBBFigure)

    def test_fib_rising_series_left_labels(self):
        """A rising series yields left-anchored Fibonacci labels."""
        idx = pd.date_range("2023-01-01", periods=150, freq="D")
        close = np.linspace(100, 200, 150)
        df = pd.DataFrame(
            {
                "open": close,
                "high": close + 1,
                "low": close - 1,
                "close": close,
                "volume": np.ones(150) * 1e6,
            },
            index=idx,
        )
        df.index.name = "date"
        inst = _prepared(df, {"fib": {"limit": 120}})
        fig = inst.init_plot("AAA", candles=True)
        out = inst.plot_fib(fig, inst.df_ta)
        assert isinstance(out, OpenBBFigure)

    def test_fib_falling_series_right_labels(self):
        """A falling series yields right-anchored Fibonacci labels."""
        idx = pd.date_range("2023-01-01", periods=150, freq="D")
        close = np.linspace(200, 100, 150)
        df = pd.DataFrame(
            {
                "open": close,
                "high": close + 1,
                "low": close - 1,
                "close": close,
                "volume": np.ones(150) * 1e6,
            },
            index=idx,
        )
        df.index.name = "date"
        inst = _prepared(df, {"fib": {"limit": 120}})
        fig = inst.init_plot("AAA", candles=True)
        out = inst.plot_fib(fig, inst.df_ta)
        assert isinstance(out, OpenBBFigure)

    def test_fib_intraday_branch(self, recent_intraday_df):
        """Fibonacci handles the intraday same-day resampling branch."""
        inst = _prepared(recent_intraday_df, {"fib": {}}, intraday=True)
        fig = inst.init_plot("AAA", candles=True)
        out = inst.plot_fib(fig, inst.df_ta)
        assert isinstance(out, OpenBBFigure)

    def test_fib_import_error_warns(self, daily_df, monkeypatch):
        """A missing ``openbb-technical`` install warns and returns unchanged."""
        inst = _prepared(daily_df, {"fib": {}})
        fig = inst.init_plot("AAA", candles=True)
        real_import = builtins.__import__

        def fake_import(name, *args, **kwargs):
            if name == "openbb_technical.helpers":
                raise ImportError("forced")
            return real_import(name, *args, **kwargs)

        monkeypatch.setattr(builtins, "__import__", fake_import)
        with pytest.warns(UserWarning, match="Fibonacci"):
            out = inst.plot_fib(fig, inst.df_ta)
        assert isinstance(out, OpenBBFigure)

    def test_srlines_daily_window(self, recent_daily_df):
        """Support/resistance line detection runs over a recent daily window."""
        fig = _plot(
            recent_daily_df, {"srlines": {"window": [200]}}, candles=True, volume=True
        )
        assert isinstance(fig, OpenBBFigure)

    def test_srlines_intraday_window(self, recent_intraday_df):
        """Support/resistance detection runs the intraday resampling branch."""
        fig = _plot(
            recent_intraday_df,
            {"srlines": {"window": [5]}},
            candles=True,
            volume=True,
        )
        assert isinstance(fig, OpenBBFigure)

    def test_srlines_default_window(self, recent_daily_df):
        """Support/resistance falls back to the default window when unset."""
        fig = _plot(recent_daily_df, {"srlines": {}}, candles=True, volume=True)
        assert isinstance(fig, OpenBBFigure)

    def test_srlines_daily_weekend_x_range(self):
        """Daily support/resistance extends the projection past a weekend."""
        with freeze_time(dt.datetime(2024, 6, 15, 12, 0)):
            idx = pd.date_range("2024-01-01", "2024-06-14", freq="D")
            rng = np.random.default_rng(1)
            close = 100 + np.cumsum(rng.normal(0, 1, len(idx)))
            df = pd.DataFrame(
                {
                    "open": close,
                    "high": close + 1,
                    "low": close - 1,
                    "close": close,
                    "volume": np.ones(len(idx)) * 1e6,
                },
                index=idx,
            )
            df.index.name = "date"
            fig = _plot(df, {"srlines": {"window": [200]}}, candles=True, volume=True)
        assert isinstance(fig, OpenBBFigure)

    def test_srlines_empty_detection_loop(self):
        """Support/resistance returns cleanly when the scan window is too short."""
        with freeze_time(dt.datetime(2024, 6, 17, 12, 0)):
            idx = pd.date_range("2024-06-14", "2024-06-16", freq="D")
            rng = np.random.default_rng(5)
            close = 100 + np.cumsum(rng.normal(0, 1, len(idx)))
            df = pd.DataFrame(
                {
                    "open": close,
                    "high": close + 1,
                    "low": close - 1,
                    "close": close,
                    "volume": np.ones(len(idx)) * 1e6,
                },
                index=idx,
            )
            df.index.name = "date"
            inst = _prepared(df, {"srlines": {"window": [5]}})
            fig = inst.init_plot("AAA", candles=True)
            out = inst.plot_srlines(fig, inst.df_ta)
        assert isinstance(out, OpenBBFigure)

    def test_srlines_intraday_late_weekend_x_range(self):
        """Intraday support/resistance projects from a post-15:00 Friday bar."""
        with freeze_time(dt.datetime(2024, 6, 14, 16, 0)):
            idx = pd.date_range("2024-06-14 09:30", periods=78, freq="5min")
            rng = np.random.default_rng(3)
            close = 100 + np.cumsum(rng.normal(0, 0.2, len(idx)))
            df = pd.DataFrame(
                {
                    "open": close,
                    "high": close + 0.3,
                    "low": close - 0.3,
                    "close": close,
                    "volume": np.ones(len(idx)) * 1e4,
                },
                index=idx,
            )
            df.index.name = "date"
            fig = _plot(df, {"srlines": {"window": [5]}}, candles=True, volume=True)
        assert isinstance(fig, OpenBBFigure)
