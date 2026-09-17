"""Tests for openbb_technical.technical_views."""

from __future__ import annotations

import sys
import types
from unittest.mock import MagicMock

import numpy as np
import pandas as pd
import pytest
from openbb_core.provider.abstract.data import Data


@pytest.fixture(autouse=True)
def stub_openbb_charting(monkeypatch):
    """Stub openbb_charting module tree so technical_views imports succeed."""
    mod_names = [
        "openbb_charting",
        "openbb_charting.charts",
        "openbb_charting.charts.relative_rotation",
        "openbb_charting.core",
        "openbb_charting.core.chart_style",
        "openbb_charting.core.openbb_figure",
        "openbb_charting.core.plotly_ta",
        "openbb_charting.core.plotly_ta.ta_class",
        "openbb_charting.core.to_chart",
        "openbb_charting.styles",
        "openbb_charting.styles.colors",
    ]
    fake_modules = {name: types.ModuleType(name) for name in mod_names}

    def _make_figure(*_args, **_kwargs):
        figure = MagicMock(name="OpenBBFigure")
        figure.create_subplots.return_value = figure
        figure.show.return_value.to_plotly_json.return_value = {"plotly": "json"}
        figure.to_plotly_json.return_value = {"plotly": "json"}
        return figure

    def _make_ta(*_args, **_kwargs):
        ta = MagicMock(name="PlotlyTA")
        ta.plot.return_value = _make_figure()
        return ta

    def _make_style(*_args, **_kwargs):
        style = MagicMock(name="ChartStyle")
        style.plotly_template = {"layout": {}}
        style.plt_style = "light"
        return style

    fake_modules["openbb_charting.core.openbb_figure"].OpenBBFigure = _make_figure
    fake_modules["openbb_charting.core.plotly_ta.ta_class"].PlotlyTA = _make_ta
    fake_modules["openbb_charting.core.chart_style"].ChartStyle = _make_style
    fake_modules["openbb_charting.core.to_chart"].to_chart = MagicMock(
        return_value=(_make_figure(), MagicMock())
    )
    fake_modules["openbb_charting.styles.colors"].LARGE_CYCLER = [
        "red",
        "blue",
        "green",
    ] * 50
    rr_module = fake_modules["openbb_charting.charts.relative_rotation"]
    rr_module.create_rrg_with_tails = MagicMock(return_value=MagicMock())
    rr_module.create_rrg_without_tails = MagicMock(return_value=MagicMock())
    fake_modules["openbb_charting.charts"].relative_rotation = rr_module

    for name, mod in fake_modules.items():
        monkeypatch.setitem(sys.modules, name, mod)

    monkeypatch.delitem(sys.modules, "openbb_technical.technical_views", raising=False)


@pytest.fixture
def ta_accessor(monkeypatch):
    """Patch the pandas_ta DataFrame accessor used by _ta_ma."""

    class _FakeTa:
        def __init__(self, df):
            self._df = df

        def __getattr__(self, _name):
            def _runner(length=None, offset=None):
                values = np.arange(1, len(self._df) + 1, dtype="float64")
                return pd.Series(values, index=self._df.index)

            return _runner

    monkeypatch.setattr(
        pd.DataFrame,
        "ta",
        property(lambda self: _FakeTa(self)),
        raising=False,
    )


def _records_to_data(records):
    return [Data(**row) for row in records]


def _rr_obbject(empty=False):
    obb = MagicMock()
    if empty:
        obb.rs_ratios = []
        obb.rs_momentum = []
    else:
        obb.rs_ratios = [
            Data(date="2021-01-01", SPY=1.0, QQQ=1.1),
            Data(date="2021-01-02", SPY=1.2, QQQ=1.3),
        ]
        obb.rs_momentum = [
            Data(date="2021-01-01", SPY=0.5, QQQ=0.6),
            Data(date="2021-01-02", SPY=0.7, QQQ=0.8),
        ]
    obb.benchmark = "SPY"
    obb.study = "price"
    return obb


class TestTechnicalSma:
    def test_uses_dataframe_input(self, ohlcv_df, ta_accessor):
        from openbb_technical.technical_views import TechnicalViews

        fig, content = TechnicalViews.technical_sma(data=ohlcv_df.reset_index())
        assert fig is not None
        assert isinstance(content, dict)

    def test_existing_ma_type_kwarg_preserved(self, ohlcv_df, ta_accessor):
        from openbb_technical.technical_views import TechnicalViews

        fig, _ = TechnicalViews.technical_sma(data=ohlcv_df, ma_type="ema")
        assert fig is not None


class TestTechnicalEma:
    def test_default_ma_type_set(self, ohlcv_df, ta_accessor):
        from openbb_technical.technical_views import TechnicalViews

        fig, _ = TechnicalViews.technical_ema(data=ohlcv_df)
        assert fig is not None


class TestTechnicalHma:
    def test_default_ma_type_set(self, ohlcv_df, ta_accessor):
        from openbb_technical.technical_views import TechnicalViews

        fig, _ = TechnicalViews.technical_hma(data=ohlcv_df)
        assert fig is not None


class TestTechnicalWma:
    def test_default_ma_type_set(self, ohlcv_df, ta_accessor):
        from openbb_technical.technical_views import TechnicalViews

        fig, _ = TechnicalViews.technical_wma(data=ohlcv_df)
        assert fig is not None


class TestTechnicalZlma:
    def test_default_ma_type_set(self, ohlcv_df, ta_accessor):
        from openbb_technical.technical_views import TechnicalViews

        fig, _ = TechnicalViews.technical_zlma(data=ohlcv_df)
        assert fig is not None


class TestTaMaHelper:
    def test_from_obbject_item(self, ohlcv_records, ta_accessor):
        from openbb_technical.technical_views import _ta_ma

        fig, content = _ta_ma(obbject_item=_records_to_data(ohlcv_records))
        assert fig is not None
        assert isinstance(content, dict)

    def test_from_list_of_data(self, ohlcv_records, ta_accessor):
        from openbb_technical.technical_views import _ta_ma

        fig, _ = _ta_ma(data=_records_to_data(ohlcv_records))
        assert fig is not None

    def test_with_index_column_already_set(self, ohlcv_df, ta_accessor):
        from openbb_technical.technical_views import _ta_ma

        fig, _ = _ta_ma(data=ohlcv_df, index="date")
        assert fig is not None

    def test_multiple_ma_types_and_windows(self, ohlcv_df, ta_accessor):
        from openbb_technical.technical_views import _ta_ma

        fig, _ = _ta_ma(
            data=ohlcv_df.reset_index(),
            ma_type="sma,ema",
            length=[10, 20],
            offset=0,
            title="Custom",
        )
        assert fig is not None

    def test_target_fallback_to_close(self, ohlcv_df, ta_accessor):
        from openbb_technical.technical_views import _ta_ma

        fig, _ = _ta_ma(data=ohlcv_df.reset_index(), target="not_a_column")
        assert fig is not None

    def test_missing_target_and_close_raises(self, ta_accessor):
        from openbb_technical.technical_views import _ta_ma

        df = pd.DataFrame({"price": np.arange(1.0, 100.0)})
        with pytest.raises(ValueError, match="not found"):
            _ta_ma(data=df, target="missing")

    def test_dropnan_branch(self, ohlcv_df, ta_accessor):
        from openbb_technical.technical_views import _ta_ma

        fig, _ = _ta_ma(data=ohlcv_df.reset_index(), dropnan=True)
        assert fig is not None

    def test_candles_branch(self, ohlcv_df, ta_accessor):
        from openbb_technical.technical_views import _ta_ma

        fig, _ = _ta_ma(
            data=ohlcv_df.reset_index(),
            candles=True,
            volume=True,
        )
        assert fig is not None

    def test_ma_type_none_defaults_to_sma(self, ohlcv_df, ta_accessor):
        from openbb_technical.technical_views import _ta_ma

        fig, _ = _ta_ma(data=ohlcv_df, ma_type=None, length=None, target=None)
        assert fig is not None

    def test_dark_theme_branch(self, ohlcv_df, ta_accessor, monkeypatch):
        from openbb_technical import technical_views

        def _dark_style(*_a, **_k):
            style = MagicMock()
            style.plotly_template = {"layout": {}}
            style.plt_style = "dark"
            return style

        monkeypatch.setattr(
            sys.modules["openbb_charting.core.chart_style"],
            "ChartStyle",
            _dark_style,
        )
        fig, _ = technical_views._ta_ma(data=ohlcv_df)
        assert fig is not None

    def test_scalar_window_int(self, ohlcv_df, ta_accessor):
        from openbb_technical.technical_views import _ta_ma

        fig, _ = _ta_ma(data=ohlcv_df, length=10)
        assert fig is not None


class TestTechnicalAroon:
    def test_with_dataframe(self, ohlcv_df):
        from openbb_technical.technical_views import TechnicalViews

        fig, content = TechnicalViews.technical_aroon(
            data=ohlcv_df, symbol="SPY", volume=True
        )
        assert fig is not None
        assert isinstance(content, dict)

    def test_with_obbject_item(self, ohlcv_records):
        from openbb_technical.technical_views import TechnicalViews

        fig, _ = TechnicalViews.technical_aroon(
            obbject_item=_records_to_data(ohlcv_records)
        )
        assert fig is not None

    def test_date_column_reset(self, ohlcv_df):
        from openbb_technical.technical_views import TechnicalViews

        fig, _ = TechnicalViews.technical_aroon(data=ohlcv_df.reset_index())
        assert fig is not None

    def test_multi_symbol_raises(self, ohlcv_df):
        from openbb_technical.technical_views import TechnicalViews

        df = ohlcv_df.copy()
        df["symbol"] = ["A", "B"] * (len(df) // 2) + ["A"]
        with pytest.raises(ValueError, match="one symbol"):
            TechnicalViews.technical_aroon(data=df)


class TestTechnicalMacd:
    def test_with_dataframe(self, ohlcv_df):
        from openbb_technical.technical_views import TechnicalViews

        fig, content = TechnicalViews.technical_macd(
            data=ohlcv_df, symbol="spy", volume=True
        )
        assert fig is not None
        assert isinstance(content, dict)

    def test_with_obbject_item(self, ohlcv_records):
        from openbb_technical.technical_views import TechnicalViews

        fig, _ = TechnicalViews.technical_macd(
            obbject_item=_records_to_data(ohlcv_records)
        )
        assert fig is not None

    def test_date_column_reset(self, ohlcv_df):
        from openbb_technical.technical_views import TechnicalViews

        fig, _ = TechnicalViews.technical_macd(data=ohlcv_df.reset_index())
        assert fig is not None

    def test_multi_symbol_raises(self, ohlcv_df):
        from openbb_technical.technical_views import TechnicalViews

        df = ohlcv_df.copy()
        df["symbol"] = ["A", "B"] * (len(df) // 2) + ["A"]
        with pytest.raises(ValueError, match="one symbol"):
            TechnicalViews.technical_macd(data=df)


class TestTechnicalAdx:
    def test_with_dataframe(self, ohlcv_df):
        from openbb_technical.technical_views import TechnicalViews

        fig, content = TechnicalViews.technical_adx(data=ohlcv_df, symbol="SPY")
        assert fig is not None
        assert isinstance(content, dict)

    def test_with_obbject_item(self, ohlcv_records):
        from openbb_technical.technical_views import TechnicalViews

        fig, _ = TechnicalViews.technical_adx(
            obbject_item=_records_to_data(ohlcv_records)
        )
        assert fig is not None

    def test_date_column_reset(self, ohlcv_df):
        from openbb_technical.technical_views import TechnicalViews

        fig, _ = TechnicalViews.technical_adx(data=ohlcv_df.reset_index())
        assert fig is not None

    def test_multi_symbol_raises(self, ohlcv_df):
        from openbb_technical.technical_views import TechnicalViews

        df = ohlcv_df.copy()
        df["symbol"] = ["A", "B"] * (len(df) // 2) + ["A"]
        with pytest.raises(ValueError, match="one symbol"):
            TechnicalViews.technical_adx(data=df)


class TestTechnicalRsi:
    def test_with_dataframe(self, ohlcv_df):
        from openbb_technical.technical_views import TechnicalViews

        fig, content = TechnicalViews.technical_rsi(data=ohlcv_df, symbol="spy")
        assert fig is not None
        assert isinstance(content, dict)

    def test_with_obbject_item(self, ohlcv_records):
        from openbb_technical.technical_views import TechnicalViews

        fig, _ = TechnicalViews.technical_rsi(
            obbject_item=_records_to_data(ohlcv_records)
        )
        assert fig is not None

    def test_date_column_reset(self, ohlcv_df):
        from openbb_technical.technical_views import TechnicalViews

        fig, _ = TechnicalViews.technical_rsi(data=ohlcv_df.reset_index())
        assert fig is not None

    def test_multi_symbol_raises(self, ohlcv_df):
        from openbb_technical.technical_views import TechnicalViews

        df = ohlcv_df.copy()
        df["symbol"] = ["A", "B"] * (len(df) // 2) + ["A"]
        with pytest.raises(ValueError, match="one symbol"):
            TechnicalViews.technical_rsi(data=df)


class TestTechnicalCones:
    def _cones_df(self):
        return pd.DataFrame(
            {
                "window": [3, 10, 30, 60, 90],
                "realized": [0.1, 0.2, 0.3, 0.25, 0.2],
                "min": [0.05, 0.1, 0.15, 0.12, 0.1],
                "median": [0.1, 0.2, 0.25, 0.22, 0.18],
                "max": [0.2, 0.3, 0.4, 0.35, 0.3],
            }
        )

    def test_with_dataframe(self):
        from openbb_technical.technical_views import TechnicalViews

        fig, content = TechnicalViews.technical_cones(
            data=self._cones_df(), symbol="SPY", model="std", title="Cones"
        )
        assert fig is not None
        assert isinstance(content, dict)

    def test_with_obbject_item(self):
        from openbb_technical.technical_views import TechnicalViews

        records = self._cones_df().to_dict(orient="records")
        items = [Data(**row) for row in records]
        fig, _ = TechnicalViews.technical_cones(obbject_item=items)
        assert fig is not None

    def test_defaults_branch(self):
        from openbb_technical.technical_views import TechnicalViews

        fig, _ = TechnicalViews.technical_cones(data=self._cones_df())
        assert fig is not None

    def test_invalid_format_raises(self):
        from openbb_technical.technical_views import TechnicalViews

        df = pd.DataFrame({"window": [1, 2], "foo": [0.1, 0.2]})
        with pytest.raises(ValueError, match="expected format"):
            TechnicalViews.technical_cones(data=df)

    def test_dark_theme_branch(self, monkeypatch):
        from openbb_technical.technical_views import TechnicalViews

        def _dark_style(*_a, **_k):
            style = MagicMock()
            style.plotly_template = {"layout": {}}
            style.plt_style = "dark"
            return style

        monkeypatch.setattr(
            sys.modules["openbb_charting.core.chart_style"],
            "ChartStyle",
            _dark_style,
        )
        fig, _ = TechnicalViews.technical_cones(data=self._cones_df())
        assert fig is not None


class TestTechnicalRelativeRotation:
    def test_with_tails_default(self):
        from openbb_technical.technical_views import TechnicalViews

        fig, content = TechnicalViews.technical_relative_rotation(
            obbject_item=_rr_obbject(), title="RRG"
        )
        assert fig is not None
        assert isinstance(content, dict)

    def test_show_tails_false_with_date(self):
        from openbb_technical.technical_views import TechnicalViews

        fig, _ = TechnicalViews.technical_relative_rotation(
            obbject_item=_rr_obbject(),
            show_tails=False,
            date="2021-01-02",
            study="price",
        )
        assert fig is not None

    def test_date_forces_no_tails(self):
        from openbb_technical.technical_views import TechnicalViews

        fig, _ = TechnicalViews.technical_relative_rotation(
            obbject_item=_rr_obbject(),
            date="2021-01-02",
            tail_periods=8,
            tail_interval="day",
        )
        assert fig is not None

    def test_empty_data_raises(self):
        from openbb_technical.technical_views import TechnicalViews

        with pytest.raises(RuntimeError, match="No data"):
            TechnicalViews.technical_relative_rotation(
                obbject_item=_rr_obbject(empty=True)
            )

    def test_dark_theme_branch(self, monkeypatch):
        from openbb_technical.technical_views import TechnicalViews

        def _dark_style(*_a, **_k):
            style = MagicMock()
            style.plotly_template = {"layout": {}}
            style.plt_style = "dark"
            return style

        monkeypatch.setattr(
            sys.modules["openbb_charting.core.chart_style"],
            "ChartStyle",
            _dark_style,
        )
        fig, _ = TechnicalViews.technical_relative_rotation(obbject_item=_rr_obbject())
        assert fig is not None
