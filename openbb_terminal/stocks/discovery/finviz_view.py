"""Finviz View"""
__docformat__ = "numpy"

import os
from typing import Optional, Union

import pandas as pd
import plotly.express as px

from openbb_terminal import OpenBBFigure
from openbb_terminal.helper_funcs import export_data
from openbb_terminal.stocks.discovery import finviz_model


def display_heatmap(
    timeframe: str,
    export: str = "",
    sheet_name: Optional[str] = "",
    external_axes: bool = False,
) -> Union[None, OpenBBFigure]:
    """Display heatmap from finviz

    Parameters
    ----------
    timeframe: str
        Timeframe for performance
    sheet_name: str
        Optionally specify the name of the sheet the data is exported to.
    export: str
        Format to export data
    external_axes : bool, optional
        Whether to return the figure object or not, by default False
    """

    dfs = finviz_model.get_heatmap_data(timeframe)
    if dfs.empty:
        return None

    color_bin = [-100, -2, -1, -0.001, 0.001, 1, 2, 100]
    dfs["colors"] = pd.cut(
        dfs["Change"],
        bins=color_bin,
        labels=[
            "rgb(246, 53, 56)",
            "rgb(191, 64, 69)",
            "rgb(139, 68, 78)",
            "grey",
            "rgb(53, 118, 78)",
            "rgb(47, 158, 79)",
            "rgb(48, 204, 90)",
        ],
    )

    fig = OpenBBFigure.create_subplots(
        print_grid=False,
        vertical_spacing=0,
        horizontal_spacing=-0,
        specs=[[{"type": "domain"}]],
        rows=1,
        cols=1,
    )

    path_tree = [px.Constant("SP 500"), "Sector", "Ticker"]
    treemap = px.treemap(
        dfs,
        path=path_tree,
        values="value",
        custom_data=["Change"],
        color="colors",
        color_discrete_map={
            "(?)": "#262931",
            "grey": "grey",
            "rgb(246, 53, 56)": "rgb(246, 53, 56)",
            "rgb(191, 64, 69)": "rgb(191, 64, 69)",
            "rgb(139, 68, 78)": "rgb(139, 68, 78)",
            "rgb(53, 118, 78)": "rgb(53, 118, 78)",
            "rgb(47, 158, 79)": "rgb(47, 158, 79)",
            "rgb(48, 204, 90)": "rgb(48, 204, 90)",
        },
    )
    fig.add_trace(treemap["data"][0], row=1, col=1)

    fig.data[
        0
    ].texttemplate = (
        "<br> <br> <b>%{label}<br>    %{customdata[0]:.2f}% <br> <br> <br><br><b>"
    )
    fig.data[0].insidetextfont = dict(family="Arial Black", size=20, color="white")

    fig.update_traces(
        textinfo="label+text+value",
        textposition="middle center",
        selector=dict(type="treemap"),
        marker_line_width=0.3,
        marker_pad_b=10,
        marker_pad_l=0,
        marker_pad_r=0,
        marker_pad_t=25,
        tiling_pad=2,
    )
    fig.update_layout(
        margin=dict(t=0, l=0, r=0, b=0),
        hovermode=False,
        font=dict(family="Arial Black", size=20, color="white"),
    )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "heatmap",
        dfs,
        sheet_name,
        fig,
        margin=False,
    )

    return fig.show(margin=False, external=external_axes)
