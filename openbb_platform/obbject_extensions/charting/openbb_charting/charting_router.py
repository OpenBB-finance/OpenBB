"""Charting router."""

# pylint: disable=too-many-arguments, too-many-locals, too-many-branches, too-many-statements, unused-argument, too-many-lines

from typing import Any, Dict, Optional, Tuple, Union
from warnings import warn

import pandas as pd
from openbb_core.app.model.charts.chart import ChartFormat
from openbb_core.app.utils import basemodel_to_df
from plotly.graph_objs import Figure

from openbb_charting.core.chart_style import ChartStyle
from openbb_charting.core.openbb_figure import OpenBBFigure
from openbb_charting.core.plotly_ta.ta_class import PlotlyTA
from openbb_charting.core.to_chart import to_chart
from openbb_charting.styles.colors import LARGE_CYCLER
from openbb_charting.utils import relative_rotation
from openbb_charting.utils.generic_charts import bar_chart
from openbb_charting.utils.helpers import (
    calculate_returns,
    heikin_ashi,
    should_share_axis,
    z_score_standardization,
)

CHART_FORMAT = ChartFormat.plotly


def equity_price_performance(
    **kwargs,
) -> Tuple[Union[OpenBBFigure, Figure], Dict[str, Any]]:  # noqa: PLR0912
    """Equity Price Performance Chart."""

    if "data" in kwargs and isinstance(kwargs["data"], pd.DataFrame):
        data = kwargs["data"]
    elif "data" in kwargs and isinstance(kwargs["data"], list):
        data = basemodel_to_df(kwargs["data"], index=kwargs.get("index", "symbol"))  # type: ignore
    else:
        data = basemodel_to_df(
            kwargs["obbject_item"], index=kwargs.get("index", "symbol")  # type: ignore
        )

    cols = [
        "one_day",
        "one_week",
        "one_month",
        "three_month",
        "six_month",
        "ytd",
        "one_year",
        "two_year",
        "three_year",
        "four_year",
        "five_year",
    ]

    df = pd.DataFrame()
    chart_df = pd.DataFrame()

    if "symbol" in data.columns:
        data = data.set_index("symbol")
    chart_cols = []

    if len(data) == 0:
        raise ValueError("No data was found in the DataFrame.")

    data = data.drop_duplicates(keep="first")

    for col in cols:
        if col in data.columns and data[col].notnull().any():
            df[col.replace("_", " ").title() if col != "ytd" else col.upper()] = data[
                col
            ].apply(lambda x: round(x * 100, 4) if x is not None else None)

    if df.empty:
        raise ValueError(f"No columns matching, {cols}, were found in the data.")

    chart_df = df.T
    chart_cols = chart_df.columns.to_list()

    if "limit" in kwargs and isinstance(kwargs.get("limit"), int):
        limit = kwargs.pop("limit", 10)
        chart_df = chart_df.head(limit)  # type: ignore

    layout_kwargs: Dict[str, Any] = kwargs["layout_kwargs"] if "layout_kwargs" in kwargs else {}  # type: ignore

    title = (
        f"{kwargs.pop('title')}" if "title" in kwargs else "Equity Price Performance"
    )
    orientation = (
        kwargs.pop("orientation")
        if "orientation" in kwargs and kwargs.get("orientation") is not None
        else "v"
    )

    ytitle = "Performance (%)"
    xtitle = None

    if orientation == "h":
        xtitle = ytitle  # type: ignore
        ytitle = None  # type: ignore

    fig = bar_chart(
        chart_df.reset_index(),
        x="index",
        y=chart_cols,
        title=title,
        xtitle=xtitle,
        ytitle=ytitle,
        orientation=orientation,  # type: ignore
    )
    fig.update_traces(
        hovertemplate=(
            "%{fullData.name}:%{y:.2f}%<extra></extra>"
            if orientation == "v"
            else "%{fullData.name}:%{x:.2f}%<extra></extra>"
        )
    )

    fig.update_layout(**layout_kwargs)
    content = fig.show(external=True).to_plotly_json()  # type: ignore

    return fig, content


def etf_price_performance(
    **kwargs,
) -> Tuple[Union[OpenBBFigure, Figure], Dict[str, Any]]:
    """ETF Historical Chart."""
    fig, content = equity_price_performance(**kwargs)
    if "title" in kwargs and kwargs.get("title") is not None:
        fig.set_title(kwargs.get("title"))  # type: ignore
    else:
        fig.set_title("ETF Price Performance")  # type: ignore

    content = fig.show(external=True).to_plotly_json()  # type: ignore
    return fig, content


def etf_holdings(**kwargs) -> Tuple[Union[OpenBBFigure, Figure], Dict[str, Any]]:
    """Equity Compare Groups Chart."""

    if "data" in kwargs and isinstance(kwargs["data"], pd.DataFrame):
        data = kwargs["data"]
    elif "data" in kwargs and isinstance(kwargs["data"], list):
        data = basemodel_to_df(kwargs["data"], index=None)  # type: ignore
    else:
        data = basemodel_to_df(kwargs["obbject_item"], index=None)  # type: ignore

    if "weight" not in data.columns:
        raise ValueError("No 'weight' column found in the data.")

    orientation = kwargs.get("orientation", "h")
    limit = kwargs.get("limit", 20)
    symbol = kwargs["standard_params"].get("symbol")  # type: ignore
    title = kwargs.get("title", f"Top {limit} {symbol} Holdings")
    layout_kwargs = kwargs.get("layout_kwargs", {})

    data = data.sort_values("weight", ascending=False)
    limit = min(limit, len(data))  # type: ignore
    target = data.head(limit)[["symbol", "weight"]].set_index("symbol")
    target = target.multiply(100)
    axis_title = "Weight (%)"

    fig = bar_chart(
        target.reset_index(),
        "symbol",
        ["weight"],
        title=title,  # type: ignore
        xtitle=axis_title if orientation == "h" else None,
        ytitle=axis_title if orientation == "v" else None,
        orientation=orientation,  # type: ignore
    )

    fig.update_layout(
        hovermode="x" if orientation == "v" else "y",
        margin=dict(r=0, l=50) if orientation == "h" else None,
    )

    fig.update_traces(
        hovertemplate=(
            "%{y:.3f}%<extra></extra>"
            if orientation == "v"
            else "%{x:.3f}%<extra></extra>"
        )
    )

    if layout_kwargs:
        fig.update_layout(**layout_kwargs)  # type: ignore

    content = fig.show(external=True).to_plotly_json()  # type: ignore

    return fig, content


def equity_price_historical(  # noqa: PLR0912
    **kwargs,
) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    """Equity Price Historical Chart."""

    if "data" in kwargs and isinstance(kwargs["data"], pd.DataFrame):
        data = kwargs["data"]
    elif "data" in kwargs and isinstance(kwargs["data"], list):
        data = basemodel_to_df(kwargs["data"], index=kwargs.get("index", "date"))  # type: ignore
    else:
        data = basemodel_to_df(
            kwargs["obbject_item"], index=kwargs.get("index", "date")  # type: ignore
        )

    if "date" in data.columns:
        data = data.set_index("date")

    target = str(kwargs.get("target"))
    normalize = kwargs.get("normalize") is True
    returns = kwargs.get("returns") is True
    same_axis = kwargs.get("same_axis") is True
    text_color = "black" if ChartStyle().plt_style == "light" else "white"
    title = f"{kwargs.get('title')}" if "title" in kwargs else "Historical Prices"
    y1title = ""
    y2title = ""
    candles = True
    multi_symbol = (
        bool(kwargs.get("multi_symbol") is True)
        or (
            "symbol" in data.columns
            and target in data.columns
            and len(data.symbol.unique()) > 1
        )
        or ("target" in kwargs and kwargs.get("target") is not None)
        or "symbol" in data.columns
        or (
            "symbol" not in data.columns
            and bool(data.columns.isin(["open", "high", "low", "close"]).all())
        )
    )
    target = "close" if target is None or target == "None" or target == "" else target

    if multi_symbol is True:
        if "symbol" not in data.columns and target in data.columns:
            data = data[[target]]
            y1title = target.title()
        if "symbol" in data.columns and target in data.columns:
            data = data.pivot(columns="symbol", values=target)
            y1title = target
            title = f"Historical {target.title()}"

    indicators = kwargs.get("indicators", {})
    candles = bool(~data.columns.isin(["open", "high", "low", "close"]).all())
    candles = candles if kwargs.get("candles", True) else False
    volume = kwargs.get("volume", True) if "volume" in data.columns else False

    if normalize is True:
        if "symbol" not in data.columns and target in data.columns:
            data = data[[target]]
        multi_symbol = True
        candles = False
        volume = False

    if returns is True:
        if "symbol" not in data.columns and target in data.columns:
            data = data[[target]]
        multi_symbol = True
        candles = False
        volume = False
    if (  # pylint: disable = R0916
        multi_symbol is False
        and normalize is False
        and returns is False
        and candles is True
    ) or (indicators and multi_symbol is False):
        if (
            "heikin_ashi" in kwargs
            and kwargs["heikin_ashi"] is True
            and candles is True
        ):
            data = heikin_ashi(data)
            title = f"{title} - Heikin Ashi"
        _volume = False
        if "atr" in indicators:  # type: ignore
            _volume = volume
            volume = False
        ta = PlotlyTA()
        fig = ta.plot(  # type: ignore
            data,
            indicators=indicators if indicators else {},  # type: ignore
            symbol=target if candles is False else "",
            candles=candles,
            volume=volume,  # type: ignore
        )
        if _volume is True and "atr" in indicators:  # type: ignore
            fig.add_inchart_volume(data)
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color=text_color),
            showlegend=True,
            legend=dict(
                orientation="v",
                yanchor="top",
                xanchor="right",
                y=0.95,
                x=-0.01,
                xref="paper",
                font=dict(size=12),
                bgcolor="rgba(0,0,0,0)",
            ),
            xaxis=dict(
                ticklen=0,
                showgrid=True,
                gridcolor="rgba(128,128,128,0.3)",
                zeroline=True,
                mirror=True,
                showline=True,
            ),
            xaxis2=dict(
                ticklen=0,
                showgrid=True,
                gridcolor="rgba(128,128,128,0.3)",
                zeroline=True,
                mirror=True,
                showline=True,
            ),
            yaxis=dict(
                ticklen=0,
                showgrid=True,
                gridcolor="rgba(128,128,128,0.3)",
                zeroline=True,
                mirror=True,
                showline=True,
                tickfont=dict(size=14),
            ),
            yaxis2=dict(
                ticklen=0,
                gridcolor="rgba(128,128,128,0.3)",
            ),
            yaxis3=dict(
                ticklen=0,
                gridcolor="rgba(128,128,128,0.3)",
            ),
            dragmode="pan",
            hovermode="x",
        )

        if kwargs.get("title"):
            title = kwargs["title"]
        fig.update_layout(title=dict(text=title, x=0.5))

        content = fig.to_plotly_json()

        return fig, content

    if multi_symbol is True or candles is False:

        if "symbol" not in data.columns and target in data.columns:
            data = data[[target]]

        if "symbol" in data.columns:
            data = data.pivot(columns="symbol", values=target)

        title: str = kwargs.get("title", "Historical Prices")  # type: ignore

        y1title = data.iloc[:, 0].name
        y2title = ""

        if len(data.columns) > 2 or normalize is True or returns is True:
            if returns is True or (len(data.columns) > 2 and normalize is False):
                data = data.apply(calculate_returns)
                title = f"{title} - Cumulative Returns"
                y1title = "Percent"
            if normalize is True:
                if returns is True:
                    title = f"{title.replace(' - Cumulative Returns', '')} - Normalized Cumulative Returns"
                else:
                    title = title + " - Normalized"
                data = data.apply(z_score_standardization)
                y1title = None  # type: ignore
                y2title = None  # type: ignore

        fig = OpenBBFigure()

        for i, col in enumerate(data.columns):

            hovertemplate = f"{data[col].name}: %{{y}}<extra></extra>"
            yaxis = "y1"
            if y1title and y1title != "Percent":
                yaxis = (
                    (
                        "y1"
                        if should_share_axis(data, col, y1title)  # type: ignore
                        or col == y1title
                        or normalize is True
                        or returns is True
                        else "y2"
                    )
                    if same_axis is False
                    else "y1"
                )

            if yaxis == "y2":
                y2title = data[col].name

            fig.add_scatter(
                x=data.index,
                y=data[col],
                name=data[col].name,
                mode="lines",
                hovertemplate=hovertemplate,
                line=dict(width=1, color=LARGE_CYCLER[i % len(LARGE_CYCLER)]),
                yaxis=yaxis,
            )

    if normalize is True or returns is True:
        y1title = "Percent" if returns is True else None  # type: ignore
        y2title = None  # type: ignore

    if same_axis is True:
        y1title = None  # type: ignore
        y2title = None  # type: ignore

    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        legend=(
            dict(
                orientation="v",
                yanchor="top",
                xanchor="right",
                y=0.95,
                x=-0.01,
                bgcolor="rgba(0,0,0,0)",
            )
            if len(data.columns) > 2
            else dict(
                orientation="h",
                yanchor="bottom",
                xanchor="right",
                y=1.02,
                x=0.98,
                bgcolor="rgba(0,0,0,0)",
            )
        ),
        yaxis1=(
            dict(
                side="right",
                ticklen=0,
                showgrid=True,
                showline=True,
                mirror=True,
                gridcolor="rgba(128,128,128,0.3)",
                title=dict(
                    text=y1title if y1title else None, standoff=20, font=dict(size=20)
                ),
                tickfont=dict(size=14),
                anchor="x",
            )
        ),
        yaxis2=(
            dict(
                overlaying="y",
                side="left",
                ticklen=0,
                showgrid=False,
                title=dict(
                    text=y2title if y2title else None, standoff=10, font=dict(size=20)
                ),
                tickfont=dict(size=14),
                anchor="x",
            )
            if y2title
            else None
        ),
        xaxis=dict(
            ticklen=0,
            showgrid=True,
            gridcolor="rgba(128,128,128,0.3)",
            showline=True,
            mirror=True,
        ),
        margin=dict(l=20, r=20, b=20, t=20),
        dragmode="pan",
        hovermode="x",
    )
    if kwargs.get("title"):
        title = kwargs["title"]
    fig.update_layout(title=dict(text=title, x=0.5))

    content = fig.show(external=True).to_plotly_json()

    return fig, content


def etf_historical(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    """ETF Historical Chart."""
    return equity_price_historical(**kwargs)


def index_price_historical(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    """Index Price Historical Chart."""
    return equity_price_historical(**kwargs)


def currency_price_historical(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    """Currency Price Historical Chart."""
    return equity_price_historical(**kwargs)


def crypto_price_historical(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    """Crypto Price Historical Chart."""
    return equity_price_historical(**kwargs)


def _ta_ma(**kwargs):
    """Plot moving average helper."""

    index = (
        kwargs.get("index")
        if "index" in kwargs and kwargs.get("index") is not None
        else "date"
    )
    data = kwargs.get("data")
    ma_type = (
        kwargs["ma_type"]
        if "ma_type" in kwargs and kwargs.get("ma_type") is not None
        else "sma"
    )
    ma_types = ma_type.split(",") if isinstance(ma_type, str) else ma_type

    if isinstance(data, pd.DataFrame) and not data.empty:
        data = data.set_index(index) if index in data.columns else data

    if data is None:
        data = basemodel_to_df(kwargs["obbject_item"], index=index)

    if isinstance(data, list):
        data = basemodel_to_df(data, index=index)

    window = (
        kwargs.get("length", [])
        if "length" in kwargs and kwargs.get("length") is not None
        else [50]
    )
    offset = kwargs.get("offset", 0)
    target = (
        kwargs.get("target")
        if "target" in kwargs and kwargs.get("target") is not None
        else "close"
    )

    if target not in data.columns and "close" in data.columns:
        target = "close"

    if target not in data.columns and "close" not in data.columns:
        raise ValueError(f"Column '{target}', or 'close', not found in the data.")

    df = data.copy()
    if target in data.columns:
        df = df[[target]]
        df.columns = ["close"]
    title = (
        kwargs.get("title")
        if "title" in kwargs and kwargs.get("title") is not None
        else f"{ma_type.upper()}"
    )

    fig = OpenBBFigure()
    fig = fig.create_subplots(
        1,
        1,
        shared_xaxes=True,
        vertical_spacing=0.06,
        horizontal_spacing=0.01,
        row_width=[1],
        specs=[[{"secondary_y": True}]],
    )
    fig.update_layout(ChartStyle().plotly_template.get("layout", {}))

    ma_df = pd.DataFrame()
    window = [window] if isinstance(window, int) else window
    for w in window:
        for ma_type in ma_types:
            ma_df[f"{ma_type.upper()} {w}"] = getattr(df.ta, ma_type)(
                length=w, offset=offset
            )

    if kwargs.get("dropnan") is True:
        ma_df = ma_df.dropna()
        data = data.iloc[-len(ma_df) :]

    color = 0

    if (
        "candles" in kwargs
        and kwargs.get("candles") is True
        and kwargs.get("target") is None
    ):
        volume = kwargs.get("volume") is True
        fig, _ = to_chart(data, candles=True, volume=volume)

    else:
        ma_df[f"{target}".title()] = data[target]

    for col in ma_df.columns:
        name = col.replace("_", " ")
        fig.add_scatter(
            x=ma_df.index,
            y=ma_df[col],
            name=name,
            mode="lines",
            hovertemplate=f"{name}: %{{y}}<extra></extra>",
            line=dict(width=1, color=LARGE_CYCLER[color]),
            showlegend=True,
        )
        color += 1

    fig.update_layout(
        title=dict(text=title, x=0.5, font=dict(size=16)),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            xanchor="right",
            y=1.02,
            x=0.95,
            bgcolor="rgba(0,0,0,0)",
        ),
        xaxis=dict(
            ticklen=0,
            showgrid=True,
            gridcolor="rgba(128,128,128,0.3)",
            zeroline=True,
            mirror=True,
        ),
        yaxis=dict(
            ticklen=0,
            showgrid=True,
            gridcolor="rgba(128,128,128,0.3)",
            zeroline=True,
            mirror=True,
            autorange=True,
        ),
    )

    content = fig.show(external=True).to_plotly_json()

    return fig, content


def technical_sma(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    """Plot simple moving average chart."""
    if "ma_type" not in kwargs:
        kwargs["ma_type"] = "sma"
    return _ta_ma(**kwargs)


def technical_ema(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    """Exponential moving average chart."""
    if "ma_type" not in kwargs:
        kwargs["ma_type"] = "ema"
    return _ta_ma(**kwargs)


def technical_hma(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    """Hull moving average chart."""
    if "ma_type" not in kwargs:
        kwargs["ma_type"] = "hma"
    return _ta_ma(**kwargs)


def technical_wma(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    """Weighted moving average chart."""
    if "ma_type" not in kwargs:
        kwargs["ma_type"] = "wma"
    return _ta_ma(**kwargs)


def technical_zlma(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    """Zero lag moving average chart."""
    if "ma_type" not in kwargs:
        kwargs["ma_type"] = "zlma"
    return _ta_ma(**kwargs)


def technical_aroon(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    """Technical Aroon Chart."""

    if "data" in kwargs and isinstance(kwargs["data"], pd.DataFrame):
        data = kwargs["data"]
    else:
        data = basemodel_to_df(
            kwargs["obbject_item"], index=kwargs.get("index", "date")
        )

    if "date" in data.columns:
        data = data.set_index("date")

    if "symbol" in data.columns and len(data.symbol.unique()) > 1:
        raise ValueError(
            "Please provide data with only one symbol and columns for OHLC."
        )

    symbol = kwargs.get("symbol", "")

    volume = kwargs.get("volume") is True
    title = f"Aroon Indicator & Oscillator {symbol}"

    length = kwargs.get("length", 25)
    scalar = kwargs.get("scalar", 100)
    symbol = kwargs.get("symbol", "")

    ta = PlotlyTA()
    fig = ta.plot(  # type: ignore
        data,
        dict(aroon=dict(length=length, scalar=scalar)),
        title,
        False,
        volume=volume,
    )

    content = fig.show(external=True).to_plotly_json()

    return fig, content


def technical_macd(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    """Plot moving average convergence divergence chart."""

    if "data" in kwargs and isinstance(kwargs["data"], pd.DataFrame):
        data = kwargs["data"]
    else:
        data = basemodel_to_df(
            kwargs["obbject_item"], index=kwargs.get("index", "date")
        )

    if "date" in data.columns:
        data = data.set_index("date")

    if "symbol" in data.columns and len(data.symbol.unique()) > 1:
        raise ValueError(
            "Please provide data with only one symbol and columns for OHLC."
        )

    fast = kwargs.get("fast", 12)
    slow = kwargs.get("slow", 26)
    signal = kwargs.get("signal", 9)
    symbol = kwargs.get("symbol", "")

    title = f"{symbol.upper()} MACD"
    volume = kwargs.get("volume") is True

    ta = PlotlyTA()
    fig = ta.plot(  # type: ignore
        data,
        dict(macd=dict(fast=fast, slow=slow, signal=signal)),
        title,
        False,
        volume=volume,
    )
    content = fig.show(external=True).to_plotly_json()

    return fig, content


def technical_adx(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    """Average directional movement index chart."""

    if "data" in kwargs and isinstance(kwargs["data"], pd.DataFrame):
        data = kwargs["data"]
    else:
        data = basemodel_to_df(
            kwargs["obbject_item"], index=kwargs.get("index", "date")
        )

    if "date" in data.columns:
        data = data.set_index("date")

    if "symbol" in data.columns and len(data.symbol.unique()) > 1:
        raise ValueError(
            "Please provide data with only one symbol and columns for OHLC."
        )

    length = kwargs.get("length", 14)
    scalar = kwargs.get("scalar", 100.0)
    drift = kwargs.get("drift", 1)
    symbol = kwargs.get("symbol", "")

    ta = PlotlyTA()
    fig = ta.plot(  # type: ignore
        data,
        dict(adx=dict(length=length, scalar=scalar, drift=drift)),
        f"Average Directional Movement Index (ADX) {symbol}",
        False,
        volume=False,
    )
    content = fig.show(external=True).to_plotly_json()

    return fig, content


def technical_rsi(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    """Relative strength index chart."""

    if "data" in kwargs and isinstance(kwargs["data"], pd.DataFrame):
        data = kwargs["data"]
    else:
        data = basemodel_to_df(
            kwargs["obbject_item"], index=kwargs.get("index", "date")
        )

    if "date" in data.columns:
        data = data.set_index("date")

    if "symbol" in data.columns and len(data.symbol.unique()) > 1:
        raise ValueError(
            "Please provide data with only one symbol and columns for OHLC."
        )

    window = kwargs.get("window", 14)
    scalar = kwargs.get("scalar", 100.0)
    drift = kwargs.get("drift", 1)
    symbol = kwargs.get("symbol", "")

    ta = PlotlyTA()
    fig = ta.plot(  # type: ignore
        data,
        dict(rsi=dict(length=window, scalar=scalar, drift=drift)),
        f"{symbol.upper()} RSI {window}",
        False,
        volume=False,
    )
    content = fig.show(external=True).to_plotly_json()

    return fig, content


def technical_cones(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    """Volatility Cones Chart."""
    data = kwargs.get("data")

    if isinstance(data, pd.DataFrame) and not data.empty and "window" in data.columns:
        df_ta = data.set_index("window")
    else:
        df_ta = basemodel_to_df(kwargs["obbject_item"], index="window")  # type: ignore

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
            showgrid=True,
            showline=True,
            mirror=True,
            zeroline=False,
            gridcolor="rgba(128,128,128,0.3)",
        ),
        xaxis=dict(
            type="category",
            tickmode="array",
            ticklen=0,
            tickvals=df_ta.index,
            ticktext=df_ta.index,
            title_text="Period",
            showgrid=False,
            showline=True,
            mirror=True,
            zeroline=False,
        ),
        margin=dict(l=20, r=20, b=20),
        dragmode="pan",
    )

    content = fig.to_plotly_json()

    return fig, content


def economy_fred_series(  # noqa: PLR0912
    **kwargs,
) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    """FRED Series Chart."""
    ytitle_dict = {
        "chg": "Change",
        "ch1": "Change From Year Ago",
        "pch": "Percent Change",
        "pc1": "Percent Change From Year Ago",
        "pca": "Compounded Annual Rate Of Change",
        "cch": "Continuously Compounded Rate Of Change",
        "cca": "Continuously Compounded Annual Rate Of Change",
        "log": "Natural Log",
    }

    provider = kwargs.get("provider")

    if provider != "fred":
        raise RuntimeError(
            f"This charting method does not support {provider}. Supported providers: fred."
        )

    columns = basemodel_to_df(kwargs["obbject_item"], index=None).columns.to_list()  # type: ignore

    allow_unsafe = kwargs.get("allow_unsafe", False)
    dropnan = kwargs.get("dropna", True)
    normalize = kwargs.get("normalize", False)

    data_cols = []
    data = kwargs.get("data")

    if isinstance(data, pd.DataFrame) and not data.empty:
        data_cols = data.columns.to_list()
        df_ta = data

    else:
        df_ta = basemodel_to_df(kwargs["obbject_item"], index="date")  # type: ignore

    # Check for unsupported external data injection.
    if allow_unsafe is False and data_cols:
        for data_col in data_cols:
            if data_col not in columns:
                raise RuntimeError(
                    f"Column '{data_col}' was not found in the original data."
                    + " External data injection is not supported unless `allow_unsafe = True`."
                )

    # Align the data so each column has the same index and length.
    if dropnan:
        df_ta = df_ta.dropna(how="any")

    if df_ta.empty or len(df_ta) < 2:
        raise ValueError(
            "No data is left after dropping NaN values. Try setting `dropnan = False`,"
            + " or use the `frequency` parameter on request."
        )

    columns = df_ta.columns.to_list()

    metadata = kwargs["extra"].get("results_metadata", {})  # type: ignore

    # Check if the request was transformed by the FRED API.
    params = kwargs["extra_params"] if kwargs.get("extra_params") else {}
    has_params = hasattr(params, "transform") and params.transform is not None  # type: ignore

    # Get a unique list of all units of measurement in the DataFrame.
    y_units = list({metadata.get(col).get("units") for col in columns if col in metadata})  # type: ignore
    if has_params is True and not y_units:
        y_units = [ytitle_dict.get(params.transform)]  # type: ignore

    if normalize or (
        kwargs.get("bar") is True
        and len(y_units) > 1
        and (
            has_params is False
            or not any(
                i in params.transform for i in ["pc1", "pch", "pca", "cch", "cca", "log"]  # type: ignore
            )
        )
    ):
        normalize = True
        df_ta = df_ta.apply(z_score_standardization)

    if len(y_units) > 2 and has_params is False and allow_unsafe is False:
        raise RuntimeError(
            "This method supports up to 2 y-axis units."
            + " Please use the 'transform' parameter, in the data request,"
            + " to compare all series on the same scale, or set `normalize = True`."
            + " Override this error by setting `allow_unsafe = True`."
        )

    y1_units = y_units[0] if y_units else None
    y1title = y1_units
    y2title = y_units[1] if len(y_units) > 1 else None
    xtitle = str(kwargs.get("xtitle", ""))

    # If the request was transformed, the y-axis will be shared under these conditions.
    if has_params and any(
        i in params.transform for i in ["pc1", "pch", "pca", "cch", "cca", "log"]  # type: ignore
    ):
        y1title = "Log" if params.transform == "Log" else "Percent"  # type: ignore
        y2title = None

    # Set the title for the chart.
    title: str = ""
    if isinstance(kwargs, dict) and title in kwargs:
        title = kwargs["title"]  # type: ignore
    else:
        if metadata.get(columns[0]):  # type: ignore
            title = metadata.get(columns[0]).get("title") if len(columns) == 1 else "FRED Series"  # type: ignore
        else:
            title = "FRED Series"
        transform_title = ytitle_dict.get(params.transform) if has_params is True else ""  # type: ignore
        title = f"{title} - {transform_title}" if transform_title else title

    # Define this to use as a check.
    y3title: Optional[str] = ""

    if kwargs.get("plot_bar") is True or len(df_ta.index) < 100:
        margin = dict(l=10, r=5, b=75 if xtitle else 30)
        try:
            if normalize:
                y1title = None
                title = f"{title} - Normalized" if title else "Normalized"
            bar_mode = kwargs["barmode"] if "barmode" in kwargs else "group"
            fig = bar_chart(
                df_ta.reset_index(),
                "date",
                df_ta.columns.to_list(),
                title=title,
                xtitle=xtitle,
                ytitle=y1title,
                barmode=bar_mode,  # type: ignore
                layout_kwargs=dict(margin=margin),  # type: ignore
            )
            if kwargs.get("layout_kwargs"):
                fig.update_layout(kwargs.get("layout_kwargs"))

            if kwargs.get("title"):
                fig.set_title(str(kwargs.get("title")))  # type: ignore

            content = fig.to_plotly_json()

            return fig, content  # type: ignore
        except Exception as _:
            warn("Bar chart failed. Attempting line chart.")

    # Create the figure object with subplots.
    fig = OpenBBFigure().create_subplots(
        rows=1, cols=1, shared_xaxes=True, shared_yaxes=False
    )

    # For each series in the DataFrame, add a scatter plot.
    for i, col in enumerate(df_ta.columns):

        # Check if the y-axis should be shared for this series.
        on_y1 = (
            (
                metadata.get(col).get("units") == y1_units  # type: ignore
                or y2title is None  # type: ignore
                or kwargs.get("same_axis") is True
            )
            if metadata.get(col)  # type: ignore
            else False
        )
        if normalize:
            on_y1 = True

        yaxes = "y2" if not on_y1 else "y1"
        on_y3 = not metadata.get(col) and normalize is False  # type: ignore
        if on_y3:
            yaxes = "y3"
            y3title = df_ta[col].name  # type: ignore
        fig.add_scatter(
            x=df_ta.index,
            y=df_ta[col],
            name=df_ta[col].name,
            mode="lines",
            hovertemplate=f"{df_ta[col].name}: %{{y}}<extra></extra>",
            line=dict(width=1, color=LARGE_CYCLER[i % len(LARGE_CYCLER)]),
            yaxis="y1" if kwargs.get("same_axis") is True else yaxes,
        )

    # Set the y-axis titles, if supplied.
    if kwargs.get("y1title"):
        y1title = kwargs.get("y1title")
    if kwargs.get("y2title") and y2title is not None:
        y2title = kwargs.get("y2title")
    # Set the x-axis title, if suppiled.
    if isinstance(kwargs, dict) and "xtitle" in kwargs:
        xtitle = kwargs["xtitle"]
    # If the data was normalized, set the title to reflect this.
    if normalize:
        y1title = None
        y2title = None
        y3title = None
        title = f"{title} - Normalized" if title else "Normalized"

    # Now update the layout of the complete figure.
    fig.update_layout(
        title=dict(text=title, x=0.5, font=dict(size=16)),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            xanchor="right",
            y=1.02,
            x=0.95,
            bgcolor="rgba(0,0,0,0)",
            font=dict(size=12),
        ),
        yaxis=(
            dict(
                ticklen=0,
                side="right",
                showline=True,
                mirror=True,
                title=dict(text=y1title, standoff=30, font=dict(size=16)),
                tickfont=dict(size=14),
                anchor="x",
                gridcolor="rgba(128,128,128,0.3)",
            )
            if y1title
            else None
        ),
        yaxis2=(
            dict(
                overlaying="y",
                side="left",
                ticklen=0,
                showgrid=False,
                title=dict(
                    text=y2title if y2title else None, standoff=10, font=dict(size=16)
                ),
                tickfont=dict(size=14),
                anchor="x",
            )
            if y2title
            else None
        ),
        yaxis3=(
            dict(
                overlaying="y",
                side="left",
                ticklen=0,
                position=0,
                showgrid=False,
                showticklabels=True,
                title=(
                    dict(text=y3title, standoff=10, font=dict(size=16))
                    if y3title
                    else None
                ),
                tickfont=dict(size=12, color="rgba(128,128,128,0.9)"),
                anchor="free",
            )
            if y3title
            else None
        ),
        xaxis=dict(
            ticklen=0,
            showgrid=True,
            showline=True,
            mirror=True,
            title=(
                dict(text=xtitle, standoff=30, font=dict(size=16)) if xtitle else None
            ),
            gridcolor="rgba(128,128,128,0.3)",
            domain=[0.095, 0.95] if y3title else None,
        ),
        margin=dict(r=25, l=25, b=75 if xtitle else 30) if normalize is False else None,
        autosize=True,
        dragmode="pan",
    )
    if kwargs.get("layout_kwargs"):
        fig.update_layout(kwargs.get("layout_kwargs"))
    if kwargs.get("title"):
        fig.set_title(str(kwargs.get("title")))
    content = fig.to_plotly_json()

    return fig, content


def technical_relative_rotation(
    **kwargs: Any,
) -> Tuple["OpenBBFigure", Dict[str, Any]]:
    """Relative Rotation Chart."""

    ratios_df = basemodel_to_df(kwargs["obbject_item"].rs_ratios, index="date")  # type: ignore
    momentum_df = basemodel_to_df(kwargs["obbject_item"].rs_momentum, index="date")  # type: ignore
    benchmark_symbol = kwargs["obbject_item"].benchmark  # type: ignore
    study = kwargs.get("study", None)
    study = str(kwargs["obbject_item"].study) if study is None else str(study)
    show_tails = kwargs.get("show_tails")
    show_tails = True if show_tails is None else show_tails
    tail_periods = int(kwargs.get("tail_periods")) if "tail_periods" in kwargs else 16  # type: ignore
    tail_interval = str(kwargs.get("tail_interval")) if "tail_interval" in kwargs else "week"  # type: ignore
    date = kwargs.get("date") if "date" in kwargs else None  # type: ignore
    show_tails = False if date is not None else show_tails
    if ratios_df.empty or momentum_df.empty:
        raise RuntimeError("Error: No data to plot.")

    if show_tails is True:
        fig = relative_rotation.create_rrg_with_tails(
            ratios_df, momentum_df, study, benchmark_symbol, tail_periods, tail_interval  # type: ignore
        )

    if show_tails is False:
        fig = relative_rotation.create_rrg_without_tails(
            ratios_df, momentum_df, benchmark_symbol, study, date  # type: ignore
        )

    figure = OpenBBFigure(fig)
    font_color = "black" if ChartStyle().plt_style == "light" else "white"
    figure.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(255,255,255,1)",
        font=dict(color=font_color),
        yaxis=dict(
            showgrid=True,
            gridcolor="rgba(128,128,128,0.3)",
            side="left",
            showline=True,
            zeroline=True,
            mirror=True,
            ticklen=0,
            tickfont=dict(size=14),
            titlefont=dict(size=16),
        ),
        xaxis=dict(
            showgrid=True,
            gridcolor="rgba(128,128,128,0.3)",
            showline=True,
            zeroline=True,
            mirror=True,
            ticklen=0,
            tickfont=dict(size=14),
            titlefont=dict(size=16),
            hoverformat="",
        ),
        hoverlabel=dict(
            font_size=12,
        ),
        hovermode="x",
        hoverdistance=50,
    )
    if kwargs.get("title") is not None:
        figure.set_title(str(kwargs.get("title")))
    content = figure.to_plotly_json()

    return figure, content
