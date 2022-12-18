from typing import Any, List, Optional, Tuple

import pandas as pd

# Vsurf Plot Settings
PLT_3DMESH_COLORSCALE = "Jet"
PLT_3DMESH_SCENE = dict(
    xaxis=dict(
        backgroundcolor="rgb(94, 94, 94)",
        gridcolor="white",
        showbackground=True,
        zerolinecolor="white",
    ),
    yaxis=dict(
        backgroundcolor="rgb(94, 94, 94)",
        gridcolor="white",
        showbackground=True,
        zerolinecolor="white",
    ),
    zaxis=dict(
        backgroundcolor="rgb(94, 94, 94)",
        gridcolor="white",
        showbackground=True,
        zerolinecolor="white",
    ),
    aspectratio=dict(x=1.2, y=1.2, z=0.8),
)
PLT_3DMESH_HOVERLABEL = dict(bgcolor="gold")
PLT_3DMESH_STYLE_TEMPLATE = "plotly_dark"

# Chart Plots Settings
PLT_STYLE_TEMPLATE = "plotly_dark"
PLT_CANDLE_INCREASING = "#00ACFF"
PLT_CANDLE_DECREASING = "#e4003a"
PLT_CANDLESTICKS = dict(
    increasing_line_color=dict(
        line_color=PLT_CANDLE_INCREASING, fillcolor=PLT_CANDLE_INCREASING
    ),
    decreasing_line_color=dict(
        line_color=PLT_CANDLE_DECREASING, illcolor=PLT_CANDLE_DECREASING
    ),
)
PLT_CANDLE_INCREASING_GREEN = "#009600"
PLT_CANDLE_DECREASING_RED = "#c80000"
PLT_CANDLE_VOLUME = "#fdc708"
PLT_CANDLE_NEWS_MARKER = "rgba(255, 215, 0, 0.9)"
PLT_CANDLE_NEWS_MARKER_LINE = "gold"
PLT_CANDLE_YAXIS_TEXT_COLOR = "#fdc708"
PLT_SCAT_STYLE_TEMPLATE = "plotly_dark"
PLT_SCAT_INCREASING = "#00ACFF"
PLT_SCAT_DECREASING = "#e4003a"
PLT_SCAT_PRICE = "#fdc708"
PLT_TA_STYLE_TEMPLATE = "plotly_dark"
PLT_FONT = dict(family="Fira Code", size=16)
PLOTLY_FONT = dict(family="Fira Code", size=18)
PLT_COLORWAY = [
    "#fdc708",
    "#d81aea",
    "#00e6c3",
    "#9467bd",
    "#e250c3",
    "#d1fa3d",
    "#CCEEFF",
    "#66CCFF",
    "#CCDEEE",
    "#669DCB",
    "#DAD4E5",
    "#917DB0",
    "#E6D4DF",
    "#B47DA0",
    "#FACCD8",
    "#EF6689",
    "#FCE5CC",
    "#F5B166",
    "#FFFBCC",
    "#FFF466",
]
PLT_FIB_COLORWAY: List[Any] = [
    "rgba(195, 50, 69, 0.9)",  # 0
    "rgba(130, 38, 96, 0.9)",  # 0.235
    "rgb(120, 70, 200)",  # 0.382
    "rgba(0, 93, 168, 0.9)",  # 0.5
    "rgba(173, 0, 95, 0.9)",  # 0.618
    "rgb(235, 184, 0)",  # 0.65 Golden Pocket
    "rgb(162, 115, 206)",  # 1
    dict(family="Arial Black", size=14),  # Fib's Text
    dict(color="rgba(0, 230, 195, 0.9)", width=0.9, dash="dash"),  # Fib Trendline
]


# Table Plots Settings
PLT_TBL_HEADER = dict(
    height=32,
    fill_color="rgb(30, 30, 30)",
    font_color="white",
    font_size=28,
    line_color="#6e6e6e",
    line_width=1,
)
PLT_TBL_CELLS = dict(
    height=40,
    font_size=28,
    fill_color="rgb(50, 50, 50)",
    font_color="white",
    line_color="#6e6e6e",
    line_width=0,
)
PLT_TBL_FONT = dict(size=28)
PLT_TBL_FONT_COLOR = "white"
PLT_TBL_ROW_COLORS: Optional[Tuple[str, str]] = ("#333333", "#242424")
PLT_TBL_INCREASING = "#00ACFF"
PLT_TBL_DECREASING = "#FF312E"
PLT_TBL_INCREASING_GREEN = "#009600"
PLT_TBL_DECREASING_RED = "#FF312E"

# Premium Plots Settings
PLT_INCREASING_COLORWAY = [
    "rgba(0, 150, 255, 1)",
    "rgba(0, 170, 255, 0.92)",
    "rgba(0, 170, 255, 0.90)",
    "rgba(0, 170, 255, 0.80)",
    "rgba(0, 170, 255, 0.70)",
    "rgba(0, 170, 255, 0.60)",
    "rgba(0, 170, 255, 0.50)",
    "rgba(0, 170, 255, 0.40)",
    "rgba(0, 170, 255, 0.34)",
    "rgba(0, 170, 255, 0.22)",
    "rgba(0, 170, 255, 0.10)",
    "rgba(0, 170, 255, 0.05)",
]

PLT_DECREASING_COLORWAY = [
    "rgba(230, 0, 57, 1)",
    "rgba(230, 0, 57, 0.92)",
    "rgba(230, 0, 57, 0.90)",
    "rgba(230, 0, 57, 0.80)",
    "rgba(230, 0, 57, 0.70)",
    "rgba(230, 0, 57, 0.60)",
    "rgba(230, 0, 57, 0.50)",
    "rgba(230, 0, 57, 0.40)",
    "rgba(230, 0, 57, 0.34)",
    "rgba(230, 0, 57, 0.22)",
    "rgba(230, 0, 57, 0.10)",
    "rgba(230, 0, 57, 0.05)",
]

PLT_INCREASING_COLORWAY_GREEN = [
    "rgba(0, 150, 0, 1)",
    "rgba(0, 150, 0, 0.92)",
    "rgba(0, 150, 0, 0.90)",
    "rgba(0, 150, 0, 0.80)",
    "rgba(0, 150, 0, 0.70)",
    "rgba(0, 150, 0, 0.60)",
    "rgba(0, 150, 0, 0.50)",
    "rgba(0, 150, 0, 0.40)",
    "rgba(0, 150, 0, 0.34)",
    "rgba(0, 150, 0, 0.22)",
    "rgba(0, 150, 0, 0.10)",
    "rgba(0, 150, 0, 0.05)",
]

PLT_DECREASING_COLORWAY_RED = [
    "rgba(200, 0, 0, 1)",
    "rgba(200, 0, 0, 0.92)",
    "rgba(200, 0, 0, 0.90)",
    "rgba(200, 0, 0, 0.80)",
    "rgba(200, 0, 0, 0.70)",
    "rgba(200, 0, 0, 0.60)",
    "rgba(200, 0, 0, 0.50)",
    "rgba(200, 0, 0, 0.40)",
    "rgba(200, 0, 0, 0.34)",
    "rgba(200, 0, 0, 0.22)",
    "rgba(200, 0, 0, 0.10)",
    "rgba(200, 0, 0, 0.05)",
]


def de_increasing_color_list(
    df_column: pd.DataFrame.columns = None,
    text: str = None,
    contains_str: str = "-",
    increasing_color: str = PLT_TBL_INCREASING,
    decreasing_color: str = PLT_TBL_DECREASING,
) -> List[str]:
    """Makes a colorlist for decrease/increase if value in df_column
    contains "{contains_str}" default is "-"

    Parameters
    ----------
    df_column : pd.DataFrame.columns, optional
        Dataframe column to create colorlist. by default None
    text : str, optional
        Search in a string, by default None
    contains_str : str, optional
        Decreasing String to search for in df_column. The default is "-".
    increasing_color : str, optional
        Color to use for increasing values. The default is PLT_CANDLE_INCREASING.
    decreasing_color : str, optional
        Color to use for decreasing values. The default is PLT_CANDLE_DECREASING.

    Returns
    -------
    List[str]
        List of colors for df_column
    """
    if df_column is None:
        colorlist = [decreasing_color if contains_str in text else increasing_color]  # type: ignore
    else:
        colorlist = [
            decreasing_color if boolv else increasing_color
            for boolv in df_column.astype(str).str.contains(contains_str)
        ]
    return colorlist


PLOTLY_THEME = dict(
    # Layout
    margin=dict(l=10, r=10, t=40, b=20),
    height=762,
    width=1400,
    template=PLT_STYLE_TEMPLATE,
    colorway=PLT_COLORWAY,
    font=PLOTLY_FONT,
    yaxis=dict(
        zeroline=False,
        fixedrange=True,
        title_standoff=20,
        nticks=10,
        showline=False,
        showgrid=False,
    ),
    yaxis2=dict(
        zeroline=False,
        fixedrange=False,
        anchor="x",
        layer="above traces",
        overlaying="y",
        nticks=12,
        tick0=0.5,
        title_standoff=20,
        tickfont=dict(size=18),
        showline=True,
    ),
    xaxis=dict(
        showgrid=True,
        zeroline=True,
        rangeslider=dict(visible=False),
        tickfont=dict(size=18),
    ),
    legend=dict(
        yanchor="top",
        y=0.99,
        xanchor="left",
        font_size=8,
        bgcolor="rgba(0, 0, 0, 0)",
        x=0.01,
    ),
    dragmode="pan",
    hovermode="x",
    hoverlabel=dict(align="left"),
)
