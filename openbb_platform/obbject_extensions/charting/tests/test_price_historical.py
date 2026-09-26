"""Tests for ``openbb_charting.charts.price_historical``."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest
from openbb_core.provider.abstract.data import Data

from openbb_charting.charts.price_historical import price_historical
from openbb_charting.core.openbb_figure import OpenBBFigure


def _ohlcv(seed: int, periods: int = 120, symbol: str | None = None) -> pd.DataFrame:
    """Build a deterministic OHLCV frame with a string ``date`` column."""
    rng = np.random.default_rng(seed)
    idx = pd.date_range("2023-01-01", periods=periods, freq="D")
    close = 100 + np.cumsum(rng.normal(0, 1, periods))
    open_ = close + rng.normal(0, 0.5, periods)
    high = np.maximum(open_, close) + np.abs(rng.normal(0, 0.5, periods))
    low = np.minimum(open_, close) - np.abs(rng.normal(0, 0.5, periods))
    volume = rng.integers(1_000_000, 5_000_000, periods)
    frame = pd.DataFrame(
        {
            "date": idx.strftime("%Y-%m-%d"),
            "open": open_,
            "high": high,
            "low": low,
            "close": close,
            "volume": volume,
        }
    )
    if symbol is not None:
        frame["symbol"] = symbol
    return frame


@pytest.fixture
def multi_symbol_data() -> list[Data]:
    """Long-format OHLCV records for three symbols."""
    frames = [_ohlcv(i, symbol=sym) for i, sym in enumerate(["AAA", "BBB", "CCC"])]
    long = pd.concat(frames, ignore_index=True)
    return [Data.model_validate(row) for row in long.to_dict(orient="records")]


@pytest.fixture
def two_symbol_data() -> list[Data]:
    """Long-format OHLCV records for two symbols."""
    frames = [_ohlcv(i, symbol=sym) for i, sym in enumerate(["AAA", "BBB"])]
    long = pd.concat(frames, ignore_index=True)
    return [Data.model_validate(row) for row in long.to_dict(orient="records")]


@pytest.fixture
def single_symbol_data() -> list[Data]:
    """Single-symbol OHLCV records without a ``symbol`` column."""
    return [Data.model_validate(row) for row in _ohlcv(7).to_dict(orient="records")]


class TestPriceHistoricalSingleSymbol:
    """Tests for the single-symbol candlestick path of ``price_historical``."""

    def test_candles_default(self, ohlcv_data):
        """It draws candles by default and returns a figure plus plotly JSON."""
        fig, content = price_historical(obbject_item=ohlcv_data)
        assert isinstance(fig, OpenBBFigure)
        assert isinstance(content, dict)
        assert "data" in content
        assert "layout" in content

    def test_dataframe_input(self, ohlcv_df):
        """It accepts a ready DataFrame passed via ``data``."""
        fig, _ = price_historical(data=ohlcv_df)
        assert isinstance(fig, OpenBBFigure)

    def test_list_input_via_data_kwarg(self, ohlcv_data):
        """It accepts a list of ``Data`` passed via the ``data`` kwarg."""
        fig, _ = price_historical(data=ohlcv_data)
        assert isinstance(fig, OpenBBFigure)

    def test_custom_title(self, ohlcv_data):
        """It honors a custom title on the candlestick path."""
        fig, _ = price_historical(obbject_item=ohlcv_data, title="My Prices")
        assert fig.layout.title.text == "My Prices"

    def test_heikin_ashi(self, ohlcv_data):
        """It computes Heikin-Ashi candles and tags the title."""
        fig, _ = price_historical(obbject_item=ohlcv_data, heikin_ashi=True)
        assert "Heikin Ashi" in fig.layout.title.text

    def test_indicator_sma(self, ohlcv_data):
        """It overlays a simple-moving-average indicator."""
        fig, _ = price_historical(
            obbject_item=ohlcv_data, indicators={"sma": {"length": [20]}}
        )
        assert isinstance(fig, OpenBBFigure)

    def test_indicator_atr_keeps_volume(self, ohlcv_data):
        """It adds in-chart volume back when the ATR indicator is requested."""
        fig, _ = price_historical(
            obbject_item=ohlcv_data, indicators={"atr": {"length": 14}}
        )
        assert isinstance(fig, OpenBBFigure)

    def test_volume_disabled(self, ohlcv_data):
        """It draws candles without volume when volume is disabled."""
        fig, _ = price_historical(obbject_item=ohlcv_data, volume=False)
        assert isinstance(fig, OpenBBFigure)

    def test_dataframe_with_date_column(self, ohlcv_df):
        """It moves a ``date`` column to the index when one is present."""
        with_date_col = ohlcv_df.reset_index()
        fig, _ = price_historical(data=with_date_col)
        assert isinstance(fig, OpenBBFigure)


class TestPriceHistoricalSingleSymbolTargetBranches:
    """Tests for single-symbol target selection without a ``symbol`` column."""

    def test_target_close_single_symbol(self, single_symbol_data):
        """It selects the target column for a single-symbol frame."""
        fig, _ = price_historical(obbject_item=single_symbol_data, target="close")
        assert isinstance(fig, OpenBBFigure)

    def test_normalize_single_symbol(self, single_symbol_data):
        """It normalizes the target column for a single-symbol frame."""
        fig, _ = price_historical(
            obbject_item=single_symbol_data, target="close", normalize=True
        )
        assert isinstance(fig, OpenBBFigure)

    def test_returns_single_symbol(self, single_symbol_data):
        """It computes returns on the target column for a single-symbol frame."""
        fig, _ = price_historical(
            obbject_item=single_symbol_data, target="close", returns=True
        )
        assert isinstance(fig, OpenBBFigure)


class TestPriceHistoricalLine:
    """Tests for the line/scatter rendering path of ``price_historical``."""

    def test_candles_off_single_symbol(self, ohlcv_data):
        """It draws a single line when candles are turned off."""
        fig, _ = price_historical(obbject_item=ohlcv_data, candles=False)
        assert isinstance(fig, OpenBBFigure)
        assert fig.data

    def test_two_column_secondary_axis(self):
        """It places a divergent-scale second series on the secondary axis."""
        idx = pd.date_range("2023-01-01", periods=80, freq="D")
        df = pd.DataFrame(
            {"AAA": np.linspace(100, 120, 80), "BBB": np.linspace(1, 2, 80)},
            index=idx,
        )
        df.index.name = "date"
        fig, _ = price_historical(data=df, candles=False)
        yaxes = {getattr(trace, "yaxis", None) for trace in fig.data}
        assert "y2" in yaxes

    def test_two_column_shared_axis(self):
        """It shares the primary axis when the two series have similar ranges."""
        idx = pd.date_range("2023-01-01", periods=80, freq="D")
        df = pd.DataFrame(
            {"AAA": np.linspace(100, 120, 80), "BBB": np.linspace(101, 121, 80)},
            index=idx,
        )
        df.index.name = "date"
        fig, _ = price_historical(data=df, candles=False)
        yaxes = {getattr(trace, "yaxis", None) for trace in fig.data}
        assert yaxes == {"y"}

    def test_same_axis_flag(self):
        """It forces all series onto the primary axis when ``same_axis`` is set."""
        idx = pd.date_range("2023-01-01", periods=80, freq="D")
        df = pd.DataFrame(
            {"AAA": np.linspace(100, 120, 80), "BBB": np.linspace(1, 2, 80)},
            index=idx,
        )
        df.index.name = "date"
        fig, _ = price_historical(data=df, candles=False, same_axis=True)
        yaxes = {getattr(trace, "yaxis", None) for trace in fig.data}
        assert yaxes == {"y"}


class TestPriceHistoricalMultiSymbol:
    """Tests for the multi-symbol branches of ``price_historical``."""

    def test_multi_symbol_target_close(self, multi_symbol_data):
        """It pivots long-format data on ``symbol`` for the chosen target."""
        fig, _ = price_historical(obbject_item=multi_symbol_data, target="close")
        assert len(fig.data) == 3

    def test_multi_symbol_returns(self, multi_symbol_data):
        """It computes cumulative returns and labels the title accordingly."""
        fig, _ = price_historical(
            obbject_item=multi_symbol_data, target="close", returns=True
        )
        assert "Cumulative Returns" in fig.layout.title.text

    def test_multi_symbol_normalize(self, multi_symbol_data):
        """It z-score normalizes the series and labels the title."""
        fig, _ = price_historical(
            obbject_item=multi_symbol_data, target="close", normalize=True
        )
        assert "Normalized" in fig.layout.title.text

    def test_multi_symbol_normalize_and_returns(self, multi_symbol_data):
        """It applies normalized cumulative returns when both flags are set."""
        fig, _ = price_historical(
            obbject_item=multi_symbol_data,
            target="close",
            returns=True,
            normalize=True,
        )
        assert "Normalized Cumulative Returns" in fig.layout.title.text

    def test_two_symbol_returns(self, two_symbol_data):
        """It renders cumulative returns for a two-column pivot."""
        fig, _ = price_historical(
            obbject_item=two_symbol_data, target="close", returns=True
        )
        assert isinstance(fig, OpenBBFigure)

    def test_multi_symbol_same_axis(self, multi_symbol_data):
        """It forces a single axis when ``same_axis`` is set with many series."""
        fig, _ = price_historical(
            obbject_item=multi_symbol_data, target="close", same_axis=True
        )
        assert isinstance(fig, OpenBBFigure)

    def test_multi_symbol_custom_title(self, multi_symbol_data):
        """It honors a custom title on the multi-symbol scatter path."""
        fig, _ = price_historical(
            obbject_item=multi_symbol_data, target="close", title="Custom"
        )
        assert fig.layout.title.text == "Custom"
