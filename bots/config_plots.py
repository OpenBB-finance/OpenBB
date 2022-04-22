import os
from typing import Any, List, Optional, Tuple

BOT_PLOT_DPI = int(os.getenv("OPENBB_BOT_PLOT_DPI", "300"))
BOT_PLOT_HEIGHT = int(os.getenv("OPENBB_BOT_PLOT_HEIGHT", "2500"))
BOT_PLOT_WIDTH = int(os.getenv("OPENBB_BOT_PLOT_WIDTH", "3500"))


def bot_plot_scale():
    x = BOT_PLOT_WIDTH / (BOT_PLOT_DPI)
    y = BOT_PLOT_HEIGHT / (BOT_PLOT_DPI)
    return x, y


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
PLT_CANDLE_STYLE_TEMPLATE = "plotly_dark"
PLT_CANDLE_INCREASING = "#00ACFF"
PLT_CANDLE_DECREASING = "#e4003a"
PLT_CANDLE_VOLUME = "#fdc708"
PLT_CANDLE_NEWS_MARKER = "rgba(255, 215, 0, 0.9)"
PLT_CANDLE_NEWS_MARKER_LINE = "gold"
PLT_CANDLE_YAXIS_TEXT_COLOR = "#fdc708"
PLT_SCAT_STYLE_TEMPLATE = "plotly_dark"
PLT_SCAT_INCREASING = "#00ACFF"
PLT_SCAT_DECREASING = "#e4003a"
PLT_SCAT_PRICE = "#fdc708"
PLT_TA_STYLE_TEMPLATE = "plotly_dark"
PLT_FONT = dict(
    family="Fira Code",
    size=12,
)
PLT_TA_COLORWAY = [
    "#fdc708",
    "#d81aea",
    "#00e6c3",
    "#9467bd",
    "#e250c3",
    "#d1fa3d",
]
PLT_FIB_COLORWAY: List[Any] = [
    "rgba(195, 50, 69, 1)",  # 0
    "rgba(130, 38, 96, 1)",  # 0.235
    "rgba(72, 39, 124, 1)",  # 0.382
    "rgba(0, 93, 168, 1)",  # 0.5
    "rgba(173, 0, 95, 1)",  # 0.618
    "rgba(253, 199, 8, 1)",  # 0.65 Golden Pocket
    "rgba(147, 103, 188, 1)",  # 1
    dict(
        family="Fire Code",
        size=16,
    ),  # Fib's Text
    dict(color="rgba(0, 230, 195, 1)", width=2, dash="dash"),  # Fib Trendline
]
PLT_WATERMARK = dict(
    source=(
        "https://raw.githubusercontent.com/OpenBB-finance/OpenBBTerminal"
        "/main/images/openbb_logo.png"
    ),
    xref="paper",
    yref="paper",
    x=0.86,
    y=0.08,
    sizex=1.15,
    sizey=1.20,
    opacity=0.04,
    xanchor="right",
    yanchor="bottom",
    layer="below",
)

# Table Plots Settings
PLT_TBL_HEADER = dict(
    height=16,
    fill_color="rgb(30, 30, 30)",
    font_color="white",
    font_size=12,
    line_color="rgb(63, 63, 63)",
    line_width=2,
)
PLT_TBL_CELLS = dict(
    height=25,
    font_size=12,
    fill_color="rgb(50, 50, 50)",
    font_color="white",
    line_color="rgb(63, 63, 63)",
    line_width=2,
)
PLT_TBL_FONT = dict(family="Fira Code")
PLT_TBL_ROW_COLORS: Optional[Tuple[str, str]] = (
    "rgb(55, 55, 55)",
    "rgb(50, 50, 50)",
)
PLT_TBL_INCREASING = "#00ACFF"
PLT_TBL_DECREASING = "#e4003a"
