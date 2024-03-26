"""Generic Charts Module."""

# pylint: disable=too-many-arguments,unused-argument,too-many-locals

from typing import List, Optional, Union

import numpy as np
import pandas as pd
from openbb_core.app.utils import basemodel_to_df, convert_to_basemodel
from openbb_core.provider.abstract.data import Data
from plotly.graph_objs import Figure

from openbb_charting.core.openbb_figure import OpenBBFigure
from openbb_charting.styles.colors import LARGE_CYCLER
from openbb_charting.utils.helpers import (
    calculate_returns,
    should_share_axis,
    z_score_standardization,
)


def line_chart(  # noqa: PLR0912
    data: Union[
        list,
        dict,
        pd.DataFrame,
        List[pd.DataFrame],
        pd.Series,
        List[pd.Series],
        np.ndarray,
        Data,
    ],
    index: Optional[str] = None,
    target: Optional[str] = None,
    title: Optional[str] = None,
    x: Optional[str] = None,
    xtitle: Optional[str] = None,
    y: Optional[Union[str, List[str]]] = None,
    ytitle: Optional[str] = None,
    y2: Optional[Union[str, List[str]]] = None,
    y2title: Optional[str] = None,
    layout_kwargs: Optional[dict] = None,
    scatter_kwargs: Optional[dict] = None,
    normalize: bool = False,
    returns: bool = False,
    same_axis: bool = False,
    **kwargs,
) -> Union[OpenBBFigure, Figure]:
    """Create a line chart."""

    if data is None:
        raise ValueError("Error: Data is a required field.")

    auto_layout = False
    index = (
        data.index.name
        if isinstance(data, (pd.DataFrame, pd.Series))
        else index if index is not None else x if x is not None else "date"
    )
    df: pd.DataFrame = (
        basemodel_to_df(convert_to_basemodel(data), index=index)
    ).dropna(how="all", axis=1)

    if df.index.name is None:
        if "date" in df.columns:
            df.date = df.date.apply(pd.to_datetime)
            df.set_index("date", inplace=True)
        else:
            found_index = False
            for col in df.columns:
                if df[col].dtype == "object":
                    try:
                        df[col] = df[col].apply(pd.to_datetime)
                        index = df[col].name  # type: ignore
                        df.set_index(col, inplace=True)
                        df.index.name = "date"
                        found_index = True
                    except Exception as _:  # noqa: S112
                        continue
                if found_index is True:
                    break
            if found_index is False:
                df.set_index(df.iloc[:, 0], inplace=True)

    if "symbol" in df.columns and len(df.symbol.unique()) > 1:
        df = df.pivot(columns="symbol", values=target if target else "close")

    if "symbol" not in df.columns and target in df.columns:
        df = df[[target]]

    y = y.split(",") if isinstance(y, str) else y

    if y is None or same_axis is True:
        y = df.columns.to_list()
        auto_layout = True

    if same_axis is True:
        auto_layout = False

    if returns is True:
        df = df.apply(calculate_returns)
        auto_layout = False

    if normalize is True:
        df = df.apply(z_score_standardization)
        auto_layout = False

    if layout_kwargs is None:
        layout_kwargs = {}

    if scatter_kwargs is None:
        scatter_kwargs = {}

    try:
        fig = OpenBBFigure()
    except Exception as _:
        fig = OpenBBFigure(create_backend=True)

    # fig.update_layout(ChartStyle().plotly_template.get("layout", {}))

    title = f"{title}" if title else ""
    xtitle = xtitle if xtitle else ""
    y1title = ytitle if ytitle else ""
    y2title = y2title if y2title else ""
    y2 = y2 if y2 else []
    yaxis_num = 1
    yaxis = f"y{yaxis_num}"
    first_y = y[0]
    second_y = None
    third_y = None
    add_scatter = False

    # Attempt to layout the chart automatically with multiple y-axis.
    mode = scatter_kwargs.pop("mode", "lines")
    hovertemplate = scatter_kwargs.pop("hovertemplate", None)

    if auto_layout is True:
        # Sort columns by the difference between the max and min values.
        # This is to help determine which columns should share the same y-axis.
        diff = df.max(numeric_only=True) - df.min(numeric_only=True)
        sorted_columns = diff.sort_values(ascending=False).index
        if sorted_columns is None or len(sorted_columns) == 0:
            raise ValueError("Error: expected data with numeric values.")
        df = df[sorted_columns]

        for i, col in enumerate(df.columns):

            if col in y:
                hovertemplate = (
                    hovertemplate
                    if hovertemplate
                    else f"{df[col].name}: %{{y}}<extra></extra>"
                )
                share_yaxis = should_share_axis(df, first_y, col, threshold=2.5)
                if share_yaxis is True:
                    add_scatter = True
                if share_yaxis is False:
                    yaxis_num = 2
                    yaxis = f"y{yaxis_num}"
                    if second_y is None:
                        second_y = col
                        add_scatter = True
                    if second_y is not None:
                        add_scatter = False
                        share_yaxis = should_share_axis(df, col, second_y, threshold=3)
                        if share_yaxis is True:
                            add_scatter = True
                    if share_yaxis is False:
                        yaxis_num = 3
                        yaxis = f"y{yaxis_num}"
                        third_y = col
                        add_scatter = True

                if add_scatter is True:
                    fig = fig.add_scatter(
                        x=df.index,
                        y=df[col],
                        name=col,
                        mode=mode,
                        line=dict(width=1, color=LARGE_CYCLER[i % len(LARGE_CYCLER)]),
                        hovertemplate=hovertemplate,
                        hoverlabel=dict(font_size=10),
                        yaxis=yaxis,
                        **scatter_kwargs,
                    )

    if auto_layout is False:
        color = 0
        for i, col in enumerate(y):
            hovertemplate = (
                hovertemplate
                if hovertemplate
                else f"{df[col].name}: %{{y}}<extra></extra>"
            )
            fig = fig.add_scatter(
                x=df.index,
                y=df[col],
                name=col,
                mode=mode,
                line=dict(width=1, color=LARGE_CYCLER[color]),
                hovertemplate=hovertemplate,
                hoverlabel=dict(font_size=10),
                yaxis="y1",
                **scatter_kwargs,
            )
            color += 1
        if y2:
            second_y = y2[0]
            for i, col in enumerate(y2):
                hovertemplate = (
                    hovertemplate
                    if hovertemplate
                    else f"{df[col].name}: %{{y}}<extra></extra>"
                )
                fig = fig.add_scatter(
                    x=df.index,
                    y=df[col],
                    name=col,
                    mode=mode,
                    line=dict(width=1, color=LARGE_CYCLER[color]),
                    hovertemplate=hovertemplate,
                    hoverlabel=dict(font_size=10),
                    yaxis="y2",
                    **scatter_kwargs,
                )
                color += 1

    if returns is True:
        y1title = "Percent"
        title = f"{title} - Cumulative Returns" if title else "Cumulative Returns"

    if normalize is True:
        y1title = "Z-Score"
        title = f"{title} - Z-Score" if title else "Z-Score"

    if not title and target is not None:
        title = f"{target.replace('_', ' ').title()}"

    fig.update_layout(
        title=dict(text=title if title else None, x=0.5, font=dict(size=16)),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            xanchor="right",
            y=1.02,
            x=0.95,
            bgcolor="rgba(0,0,0,0)",
        ),
        yaxis=(
            dict(
                ticklen=0,
                side="right",
                title=dict(
                    text=y1title if ytitle else None, standoff=30, font=dict(size=16)
                ),
                tickfont=dict(size=14),
                anchor="x",
                showgrid=True,
                mirror=True,
                showline=True,
                zeroline=False,
                gridcolor="rgba(128,128,128,0.25)",
            )
        ),
        yaxis2=(
            dict(
                overlaying="y",
                side="left",
                ticklen=0,
                showgrid=False,
                showline=True,
                zeroline=False,
                mirror=True,
                title=dict(
                    text=y2title if y2title else None, standoff=10, font=dict(size=16)
                ),
                tickfont=dict(size=14),
                anchor="x",
            )
        ),
        yaxis3=(
            dict(
                overlaying="y",
                side="left",
                ticklen=0,
                position=0,
                showgrid=False,
                showline=False,
                zeroline=False,
                showticklabels=True,
                mirror=False,
                tickfont=dict(size=12, color="rgba(128,128,128,0.75)"),
                anchor="free",
            )
        ),
        xaxis=dict(
            ticklen=0,
            showgrid=True,
            title=(
                dict(text=xtitle, standoff=30, font=dict(size=16)) if xtitle else None
            ),
            zeroline=False,
            showline=True,
            mirror=True,
            gridcolor="rgba(128,128,128,0.25)",
            domain=[0.095, 0.95] if third_y else None,
        ),
        margin=dict(r=25, l=25) if normalize is False else None,
        autosize=True,
        dragmode="pan",
        hovermode="x",
    )

    if df.index.name not in ("date", "timestamp"):
        fig.update_xaxes(type="category")

    if layout_kwargs:
        fig.update_layout(
            **layout_kwargs,
        )

    return fig
