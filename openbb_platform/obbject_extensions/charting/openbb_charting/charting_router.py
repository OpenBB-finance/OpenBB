"""Charting router."""

import json
from typing import Any, Dict, Optional, Tuple, Union

import pandas as pd
from openbb_core.app.model.charts.chart import ChartFormat
from openbb_core.app.utils import basemodel_to_df

from openbb_charting.core.chart_style import ChartStyle
from openbb_charting.core.openbb_figure import OpenBBFigure
from openbb_charting.core.plotly_ta.ta_class import PlotlyTA
from openbb_charting.query_params import (
    FredSeriesChartQueryParams,
    TechnicalConesChartQueryParams,
)

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


def technical_cones(
    **kwargs: TechnicalConesChartQueryParams,
) -> Tuple["OpenBBFigure", Dict[str, Any]]:
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


def economy_fred_series(
    **kwargs: Union[Any, FredSeriesChartQueryParams],
) -> Tuple["OpenBBFigure", Dict[str, Any]]:
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

    colors = [
        "#1f77b4",
        "#7f7f7f",
        "#ff7f0e",
        "#2ca02c",
        "#d62728",
        "#9467bd",
        "#8c564b",
        "#e377c2",
        "#7f7f7f",
        "#bcbd22",
        "#17becf",
    ]

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
            + " or use the `frequency` parameter on request ."
        )

    columns = df_ta.columns.to_list()

    def z_score_standardization(data: pd.Series) -> pd.Series:
        """Z-Score Standardization Method."""
        return (data - data.mean()) / data.std()

    if normalize:
        df_ta = df_ta.apply(z_score_standardization)

    # Extract the metadata from the warnings.
    warnings = kwargs.get("warnings")
    metadata = json.loads(warnings[0].message) if warnings else {}  # type: ignore

    # Check if the request was transformed by the FRED API.
    params = kwargs["extra_params"] if kwargs.get("extra_params") else {}
    has_params = hasattr(params, "transform") and params.transform is not None  # type: ignore

    # Get a unique list of all units of measurement in the DataFrame.
    y_units = list({metadata.get(col).get("units") for col in columns if col in metadata})  # type: ignore

    if len(y_units) > 2 and has_params is False and allow_unsafe is True:
        raise RuntimeError(
            "This method supports up to 2 y-axis units."
            + " Please use the 'transform' parameter, in the data request,"
            + " to compare all series on the same scale, or set `normalize = True`."
            + " Override this error by setting `allow_unsafe = True`."
        )

    y1_units = y_units[0] if y_units else None
    y1title = y1_units
    y2title = y_units[1] if len(y_units) > 1 else None
    xtitle = ""

    # If the request was transformed, the y-axis will be shared under these conditions.
    if has_params and any(
        i in params.transform for i in ["pc1", "pch", "pca", "cch", "cca", "log"]  # type: ignore
    ):
        y1title = "Log" if params.transform == "Log" else "Percent"  # type: ignore
        y2title = None

    # Set the title for the chart.
    title: str = ""
    if isinstance(kwargs, dict) and title in kwargs:
        title = kwargs["title"]
    else:
        if metadata.get(columns[0]):
            title = metadata.get(columns[0]).get("title") if len(columns) == 1 else "FRED Series"  # type: ignore
        else:
            title = "FRED Series"
        transform_title = ytitle_dict.get(params.transform) if has_params is True else ""  # type: ignore
        title = f"{title} - {transform_title}" if transform_title else title

    # Define this to use as a check.
    y3title: Optional[str] = ""

    # Create the figure object with subplots.
    fig = OpenBBFigure().create_subplots(
        rows=1, cols=1, shared_xaxes=True, shared_yaxes=False
    )
    fig.update_layout(ChartStyle().plotly_template.get("layout", {}))
    text_color = "black" if ChartStyle().plt_style == "light" else "white"

    # For each series in the DataFrame, add a scatter plot.
    for i, col in enumerate(df_ta.columns):

        # Check if the y-axis should be shared for this series.
        on_y1 = (
            (
                metadata.get(col).get("units") == y1_units
                or y2title is None  # type: ignore
            )
            if metadata.get(col)
            else False
        )
        if normalize:
            on_y1 = True
        yaxes = "y2" if not on_y1 else "y1"
        on_y3 = not metadata.get(col) and normalize is False
        if on_y3:
            yaxes = "y3"
            y3title = df_ta[col].name
        fig.add_scatter(
            x=df_ta.index,
            y=df_ta[col],
            name=df_ta[col].name,
            mode="lines",
            hovertemplate=f"{df_ta[col].name}: %{{y}}<extra></extra>",
            line=dict(width=1, color=colors[i % len(colors)]),
            yaxis=yaxes,
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
        font=dict(color=text_color),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            xanchor="right",
            y=1.02,
            x=1,
            bgcolor="rgba(0,0,0,0)",
        ),
        yaxis=(
            dict(
                ticklen=0,
                side="right",
                title=dict(text=y1title, standoff=30, font=dict(size=18)),
                tickfont=dict(size=14),
                anchor="x",
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
                    text=y2title if y2title else None, standoff=10, font=dict(size=18)
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
                tickfont=dict(size=12, color="rgba(128,128,128,0.75)"),
                anchor="free",
            )
            if y3title
            else None
        ),
        xaxis=dict(
            ticklen=0,
            showgrid=False,
            title=(
                dict(text=xtitle, standoff=30, font=dict(size=18)) if xtitle else None
            ),
            domain=[0.095, 0.95] if y3title else None,
        ),
        margin=dict(r=25, l=25) if normalize is False else None,
        autosize=True,
        dragmode="pan",
    )

    content = fig.to_plotly_json()

    return fig, content
