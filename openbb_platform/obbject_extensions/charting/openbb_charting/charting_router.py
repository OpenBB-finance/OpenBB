"""Charting router."""

from typing import Any, Dict, Tuple

import pandas as pd
from openbb_core.app.model.charts.chart import ChartFormat
from openbb_core.app.utils import basemodel_to_df

from openbb_charting.core.chart_style import ChartStyle
from openbb_charting.core.openbb_figure import OpenBBFigure
from openbb_charting.core.plotly_ta.ta_class import PlotlyTA

CHART_FORMAT = ChartFormat.plotly

# if TYPE_CHECKING:

# from .core.openbb_figure_table import OpenBBFigureTable


def equity_price_historical(**kwargs) -> Tuple["OpenBBFigure", Dict[str, Any]]:
    """Equity price chart."""

    def handle_indicators(ma):
        """Handle indicators."""
        k = {}
        if ma:
            k["rma"] = dict(length=ma)
        return k

    data = basemodel_to_df(kwargs["obbject_item"], index=kwargs.get("index", "date"))
    standard_params = kwargs["standard_params"]
    ma = standard_params.get("ma", None)
    prepost = standard_params.get("prepost", False)
    symbol = standard_params.get("symbol", "")

    ta = PlotlyTA()
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
    data = basemodel_to_df(kwargs["obbject_item"], index=kwargs.get("index", "date"))
    window = kwargs.get("window", 50)
    offset = kwargs.get("offset", 0)
    symbol = kwargs.get("symbol", "")

    ta = PlotlyTA()
    fig = ta.plot(
        data,
        {f"{ma_type.lower()}": dict(length=window, offset=offset)},
        f"{symbol.upper()} {ma_type.upper()}",
        False,
        volume=False,
    )
    fig.update_layout(ChartStyle().plotly_template.get("layout", {}))
    content = fig.show(external=True).to_plotly_json()

    return fig, content


def technical_zlma(**kwargs) -> Tuple["OpenBBFigure", Dict[str, Any]]:
    """Zero lag moving average chart."""
    ma_type = "zlma"
    return _ta_ma(ma_type, **kwargs)


def technical_aroon(**kwargs) -> Tuple["OpenBBFigure", Dict[str, Any]]:
    """Aroon chart."""
    data = basemodel_to_df(kwargs["obbject_item"], index=kwargs.get("index", "date"))
    length = kwargs.get("length", 25)
    scalar = kwargs.get("scalar", 100)
    symbol = kwargs.get("symbol", "")

    ta = PlotlyTA()
    fig = ta.plot(
        data,
        dict(aroon=dict(length=length, scalar=scalar)),
        f"Aroon on {symbol}",
        False,
        volume=False,
    )
    content = fig.show(external=True).to_plotly_json()

    return fig, content


def technical_sma(**kwargs) -> Tuple["OpenBBFigure", Dict[str, Any]]:
    """Plot simple moving average chart."""
    ma_type = "sma"
    return _ta_ma(ma_type, **kwargs)


def technical_macd(**kwargs) -> Tuple["OpenBBFigure", Dict[str, Any]]:
    """Plot moving average convergence divergence chart."""
    data = basemodel_to_df(kwargs["obbject_item"], index=kwargs.get("index", "date"))
    fast = kwargs.get("fast", 12)
    slow = kwargs.get("slow", 26)
    signal = kwargs.get("signal", 9)
    symbol = kwargs.get("symbol", "")

    ta = PlotlyTA()
    fig = ta.plot(
        data,
        dict(macd=dict(fast=fast, slow=slow, signal=signal)),
        f"{symbol.upper()} MACD",
        False,
        volume=False,
    )
    content = fig.show(external=True).to_plotly_json()

    return fig, content


def technical_hma(**kwargs) -> Tuple["OpenBBFigure", Dict[str, Any]]:
    """Hull moving average chart."""
    ma_type = "hma"
    return _ta_ma(ma_type, **kwargs)


def technical_adx(**kwargs) -> Tuple["OpenBBFigure", Dict[str, Any]]:
    """Average directional movement index chart."""
    data = basemodel_to_df(kwargs["obbject_item"], index=kwargs.get("index", "date"))
    length = kwargs.get("length", 14)
    scalar = kwargs.get("scalar", 100.0)
    drift = kwargs.get("drift", 1)
    symbol = kwargs.get("symbol", "")

    ta = PlotlyTA()
    fig = ta.plot(
        data,
        dict(adx=dict(length=length, scalar=scalar, drift=drift)),
        f"Average Directional Movement Index (ADX) {symbol}",
        False,
        volume=False,
    )
    content = fig.show(external=True).to_plotly_json()

    return fig, content


def technical_wma(**kwargs) -> Tuple["OpenBBFigure", Dict[str, Any]]:
    """Weighted moving average chart."""
    ma_type = "wma"
    return _ta_ma(ma_type, **kwargs)


def technical_rsi(**kwargs) -> Tuple["OpenBBFigure", Dict[str, Any]]:
    """Relative strength index chart."""
    data = basemodel_to_df(kwargs["obbject_item"], index=kwargs.get("index", "date"))
    window = kwargs.get("window", 14)
    scalar = kwargs.get("scalar", 100.0)
    drift = kwargs.get("drift", 1)
    symbol = kwargs.get("symbol", "")

    ta = PlotlyTA()
    fig = ta.plot(
        data,
        dict(rsi=dict(length=window, scalar=scalar, drift=drift)),
        f"{symbol.upper()} RSI {window}",
        False,
        volume=False,
    )
    content = fig.show(external=True).to_plotly_json()

    return fig, content


def technical_ema(**kwargs) -> Tuple["OpenBBFigure", Dict[str, Any]]:
    """Exponential moving average chart."""
    ma_type = "ema"
    return _ta_ma(ma_type, **kwargs)


def technical_cones(**kwargs) -> Tuple["OpenBBFigure", Dict[str, Any]]:
    """Volatility Cones Chart."""

    data = kwargs.get("data")

    if isinstance(data, pd.DataFrame) and not data.empty and "window" in data.columns:
        df_ta = data.set_index("window")
    else:
        df_ta = basemodel_to_df(kwargs["obbject_item"], index="window")

    df_ta.columns = [col.title().replace("_", " ") for col in df_ta.columns]

    # Check if the data is formatted as expected.
    if not all(col in df_ta.columns for col in ["Realized", "Min", "Median", "Max"]):
        raise ValueError("Data supplied does not match the expected format.")

    model = (
        str(kwargs.get("model"))
        .replace("std", "Standard Deviation")
        .replace("_", "-")
        .title()
        if kwargs.get("model")
        else "Standard Deviation"
    )

    symbol = str(kwargs.get("symbol")) + " - " if kwargs.get("symbol") else ""

    title = (
        str(kwargs.get("title"))
        if kwargs.get("title")
        else f"{symbol}Realized Volatility Cones - {model} Model"
    )

    colors = [
        "green",
        "red",
        "burlywood",
        "grey",
        "orange",
        "blue",
    ]
    color = 0

    fig = OpenBBFigure()

    fig.update_layout(ChartStyle().plotly_template.get("layout", {}))

    text_color = "black" if ChartStyle().plt_style == "light" else "white"

    for col in df_ta.columns:
        fig.add_scatter(
            x=df_ta.index,
            y=df_ta[col],
            name=col,
            mode="lines+markers",
            hovertemplate=f"{col}: %{{y}}<extra></extra>",
            marker=dict(
                color=colors[color],
                size=11,
            ),
        )
        color += 1

    fig.set_title(title)

    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color=text_color),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            xanchor="right",
            y=1.02,
            x=1,
            bgcolor="rgba(0,0,0,0)",
        ),
        yaxis=dict(
            ticklen=0,
        ),
        xaxis=dict(
            type="category",
            tickmode="array",
            ticklen=0,
            tickvals=df_ta.index,
            ticktext=df_ta.index,
            title_text="Period",
            showgrid=False,
            zeroline=False,
        ),
        margin=dict(l=20, r=20, b=20),
        dragmode="pan",
    )

    content = fig.to_plotly_json()

    return fig, content
