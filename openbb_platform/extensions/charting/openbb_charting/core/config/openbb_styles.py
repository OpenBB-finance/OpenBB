from typing import Any, List, Optional

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

# Chart Plots Settings
PLT_STYLE_TEMPLATE = "plotly_dark"
PLT_STYLE_INCREASING = "#00ACFF"
PLT_STYLE_DECREASING = "#e4003a"
PLT_CANDLESTICKS = dict(
    increasing=dict(line_color=PLT_STYLE_INCREASING, fillcolor=PLT_STYLE_INCREASING),
    decreasing=dict(line_color=PLT_STYLE_DECREASING, fillcolor=PLT_STYLE_DECREASING),
)
PLT_STYLE_INCREASING_GREEN = "#009600"
PLT_STYLE_DECREASING_RED = "#c80000"
PLT_FONT = dict(family="Fira Code", size=16)
PLOTLY_FONT = dict(family="Fira Code", size=18)

PLT_COLORWAY = [
    "#ffed00",
    "#ef7d00",
    "#e4003a",
    "#c13246",
    "#822661",
    "#48277c",
    "#005ca9",
    "#00aaff",
    "#9b30d9",
    "#af005f",
    "#5f00af",
    "#af87ff",
]

PLT_FIB_COLORWAY: List[Any] = [
    "rgb(195, 50, 69)",  # 0
    "rgb(130, 38, 96)",  # 0.235
    "rgb(120, 70, 200)",  # 0.382
    "rgb(0, 93, 168)",  # 0.5
    "rgb(173, 0, 95)",  # 0.618
    "rgb(235, 184, 0)",  # 0.65 Golden Pocket
    "rgb(162, 115, 206)",  # 1
    dict(family="Arial Black", size=10),  # Fib's Text
    dict(color="rgb(0, 230, 195)", width=0.9, dash="dash"),  # Fib Trendline
]

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


# Table Plots Settings
PLT_TBL_HEADER = dict(
    fill_color="rgb(30, 30, 30)",
    font_color="white",
    line_color="#6e6e6e",
    line_width=1,
)
PLT_TBL_CELLS = dict(
    font_color="white",
    line_color="#6e6e6e",
    line_width=0,
)
PLT_TBL_ROW_COLORS = (
    "#333333",
    "#242424",
)


def de_increasing_color_list(
    df_column: Optional[pd.DataFrame] = None,
    text: Optional[str] = None,
    contains_str: str = "-",
    increasing_color: str = PLT_STYLE_INCREASING,
    decreasing_color: str = PLT_STYLE_DECREASING,
) -> List[str]:
    """Makes a colorlist for decrease/increase if value in df_column
    contains "{contains_str}" default is "-"

    Parameters
    ----------
    df_column : pd.DataFrame, optional
        Dataframe column to create colorlist. by default None
    text : str, optional
        Search in a string, by default None
    contains_str : str, optional
        Decreasing String to search for in df_column. The default is "-".
    increasing_color : str, optional
        Color to use for increasing values. The default is PLT_STYLE_INCREASING.
    decreasing_color : str, optional
        Color to use for decreasing values. The default is PLT_STYLE_DECREASING.

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
    layout=dict(
        colorway=PLT_COLORWAY,
        font=PLOTLY_FONT,
        yaxis=dict(
            side="right",
            zeroline=True,
            fixedrange=False,
            title_standoff=20,
            nticks=15,
            showline=True,
            showgrid=True,
        ),
        yaxis2=dict(
            zeroline=False,
            fixedrange=False,
            anchor="x",
            layer="above traces",
            overlaying="y2",
            nticks=6,
            tick0=0.5,
            title_standoff=10,
            tickfont=dict(size=15),
            showline=True,
        ),
        yaxis3=dict(
            zeroline=False,
            fixedrange=False,
            anchor="x",
            layer="above traces",
            overlaying="y3",
            nticks=6,
            tick0=0.5,
            title_standoff=10,
            tickfont=dict(size=15),
            showline=True,
        ),
        yaxis4=dict(
            zeroline=False,
            fixedrange=False,
            anchor="x",
            layer="above traces",
            overlaying="y4",
            nticks=6,
            tick0=0.5,
            title_standoff=10,
            tickfont=dict(size=15),
            showline=True,
        ),
        xaxis=dict(
            showgrid=True,
            zeroline=True,
            showline=True,
            rangeslider=dict(visible=False),
            tickfont=dict(size=16),
            title_standoff=20,
        ),
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            font_size=15,
            bgcolor="rgba(0, 0, 0, 0)",
            x=0.01,
        ),
        dragmode="pan",
        hovermode="x",
        hoverlabel=dict(align="left"),
    ),
    data=dict(
        candlestick=[
            dict(
                increasing=dict(
                    line=dict(color=PLT_STYLE_INCREASING),
                    fillcolor=PLT_STYLE_INCREASING,
                ),
                decreasing=dict(
                    line=dict(color=PLT_STYLE_DECREASING),
                    fillcolor=PLT_STYLE_DECREASING,
                ),
            )
        ]
    ),
)
