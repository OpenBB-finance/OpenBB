"""Charting router."""
from typing import Any, Dict, Tuple

from openbb_core.app.model.charts.chart import ChartFormat
from openbb_core.app.router import Router
from openbb_core.app.utils import basemodel_to_df

from .core.openbb_figure import OpenBBFigure
from .core.openbb_figure_table import OpenBBFigureTable
from .core.plotly_ta.ta_class import PlotlyTA

router = Router(prefix="")

CHART_FORMAT = ChartFormat.plotly


def equity_price_historical(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    """Equity price chart."""

    def handle_indicators(ma):
        """Handle indicators."""
        k = {}
        if ma:
            k["rma"] = dict(length=ma)
        return k

    data = basemodel_to_df(kwargs["obbject_item"], index=kwargs.get("index", "date"))
    standard_params = kwargs["standard_params"].__dict__
    ma = standard_params.get("ma", None)
    prepost = standard_params.get("prepost", False)
    symbol = standard_params.get("symbol", "")

    ta = PlotlyTA(charting_settings=kwargs["charting_settings"])
    fig = ta.plot(
        data,
        indicators=dict(**handle_indicators(ma)),
        symbol=f"{symbol} historical data",
        prepost=prepost,
    )
    content = fig.show(external=True).to_plotly_json()

    return fig, content


def _ta_ma(ma_type: str, **kwargs):
    """Plot moving average helper."""
    data = basemodel_to_df(kwargs["data"], index=kwargs.get("index", "date"))
    window = kwargs.get("window", 50)
    offset = kwargs.get("offset", 0)
    symbol = kwargs.get("symbol", "")

    ta = PlotlyTA(charting_settings=kwargs["charting_settings"])
    fig = ta.plot(
        data,
        {f"{ma_type.lower()}": dict(length=window, offset=offset)},
        f"{symbol.upper()} {ma_type.upper()}",
        False,
        volume=False,
    )
    content = fig.show(external=True).to_plotly_json()

    return fig, content


def technical_zlma(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    """Zero lag moving average chart."""
    ma_type = "zlma"
    return _ta_ma(ma_type, **kwargs)


def technical_aroon(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    """Aroon chart."""
    data = basemodel_to_df(kwargs["data"], index=kwargs.get("index", "date"))
    length = kwargs.get("length", 25)
    scalar = kwargs.get("scalar", 100)
    symbol = kwargs.get("symbol", "")

    ta = PlotlyTA(charting_settings=kwargs["charting_settings"])
    fig = ta.plot(
        data,
        dict(aroon=dict(length=length, scalar=scalar)),
        f"Aroon on {symbol}",
        False,
        volume=False,
    )
    content = fig.show(external=True).to_plotly_json()

    return fig, content


def technical_sma(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    """Plot simple moving average chart."""
    ma_type = "sma"
    return _ta_ma(ma_type, **kwargs)


def technical_macd(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    """Plot moving average convergence divergence chart."""
    data = basemodel_to_df(kwargs["data"], index=kwargs.get("index", "date"))
    fast = kwargs.get("fast", 12)
    slow = kwargs.get("slow", 26)
    signal = kwargs.get("signal", 9)
    symbol = kwargs.get("symbol", "")

    ta = PlotlyTA(charting_settings=kwargs["charting_settings"])
    fig = ta.plot(
        data,
        dict(macd=dict(fast=fast, slow=slow, signal=signal)),
        f"{symbol.upper()} MACD",
        False,
        volume=False,
    )
    content = fig.show(external=True).to_plotly_json()

    return fig, content


def technical_hma(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    """Hull moving average chart."""
    ma_type = "hma"
    return _ta_ma(ma_type, **kwargs)


def technical_adx(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    """Average directional movement index chart."""
    data = basemodel_to_df(kwargs["data"], index=kwargs.get("index", "date"))
    length = kwargs.get("length", 14)
    scalar = kwargs.get("scalar", 100.0)
    drift = kwargs.get("drift", 1)
    symbol = kwargs.get("symbol", "")

    ta = PlotlyTA(charting_settings=kwargs["charting_settings"])
    fig = ta.plot(
        data,
        dict(adx=dict(length=length, scalar=scalar, drift=drift)),
        f"Average Directional Movement Index (ADX) {symbol}",
        False,
        volume=False,
    )
    content = fig.show(external=True).to_plotly_json()

    return fig, content


def technical_wma(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    """Weighted moving average chart."""
    ma_type = "wma"
    return _ta_ma(ma_type, **kwargs)


def technical_rsi(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    """Relative strength index chart."""
    data = basemodel_to_df(kwargs["data"], index=kwargs.get("index", "date"))
    window = kwargs.get("window", 14)
    scalar = kwargs.get("scalar", 100.0)
    drift = kwargs.get("drift", 1)
    symbol = kwargs.get("symbol", "")

    ta = PlotlyTA(charting_settings=kwargs["charting_settings"])
    fig = ta.plot(
        data,
        dict(rsi=dict(length=window, scalar=scalar, drift=drift)),
        f"{symbol.upper()} RSI {window}",
        False,
        volume=False,
    )
    content = fig.show(external=True).to_plotly_json()

    return fig, content


def technical_ema(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    """Exponential moving average chart."""
    ma_type = "ema"
    return _ta_ma(ma_type, **kwargs)


def equity_fundamental_multiples(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    """Equity multiples chart."""
    data = basemodel_to_df(kwargs["obbject_item"], index=kwargs.get("index", "date"))
    standard_params = kwargs["standard_params"].__dict__
    columnwidth = standard_params.get("columnwidth", None)

    tbl_fig = OpenBBFigureTable(tabular_data=data, columnwidth=columnwidth)
    content = tbl_fig.to_table().show(external=True).to_plotly_json()

    return tbl_fig, content
