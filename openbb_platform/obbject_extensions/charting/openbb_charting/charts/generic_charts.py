"""Generic Charts Module."""

# pylint: disable=too-many-arguments,unused-argument,too-many-locals, too-many-branches, too-many-lines, too-many-statements, use-dict-literal, broad-exception-caught, too-many-nested-blocks, too-many-positional-arguments

from typing import TYPE_CHECKING, Any, Literal, Union

from openbb_core.app.utils import basemodel_to_df, convert_to_basemodel
from openbb_core.provider.abstract.data import Data

from openbb_charting.charts.helpers import (
    calculate_returns,
    should_share_axis,
    z_score_standardization,
)
from openbb_charting.core.chart_style import ChartStyle
from openbb_charting.styles.colors import LARGE_CYCLER

if TYPE_CHECKING:
    from numpy import ndarray  # noqa
    from pandas import DataFrame, Series  # noqa
    from plotly.graph_objs import Figure  # noqa
    from openbb_charting.core.openbb_figure import OpenBBFigure  # noqa


def line_chart(  # noqa: PLR0912
    data: Union[
        list,
        dict,
        "DataFrame",
        list["DataFrame"],
        "Series",
        list["Series"],
        "ndarray",
        Data,
    ],
    index: str | None = None,
    target: str | None = None,
    title: str | None = None,
    x: str | None = None,
    xtitle: str | None = None,
    y: str | list[str] | None = None,
    ytitle: str | None = None,
    y2: str | list[str] | None = None,
    y2title: str | None = None,
    layout_kwargs: dict | None = None,
    scatter_kwargs: dict | None = None,
    normalize: bool = False,
    returns: bool = False,
    same_axis: bool = False,
    **kwargs,
) -> Union["OpenBBFigure", "Figure"]:
    """Create a line chart."""
    # pylint: disable=import-outside-toplevel
    from pandas import DataFrame, Series, to_datetime  # noqa
    from openbb_charting.core.openbb_figure import OpenBBFigure

    if data is None:
        raise ValueError("Error: Data is a required field.")

    auto_layout = False
    index = (  # type: ignore
        data.index.name
        if isinstance(data, (DataFrame, Series))
        else index if index is not None else x if x is not None else "date"
    )
    df: DataFrame = (basemodel_to_df(convert_to_basemodel(data), index=index)).dropna(
        how="all", axis=1
    )

    if df.index.name is None:
        if "date" in df.columns:
            df.date = df.date.apply(to_datetime)
            df.set_index("date", inplace=True)
        else:
            found_index = False
            for col in df.columns:
                if df[col].dtype == "object":
                    try:
                        df[col] = df[col].apply(to_datetime)
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

    target = target if target else "close"

    if "symbol" in df.columns and len(df.symbol.unique()) > 1:
        df = df.pivot(columns="symbol", values=target)

    if "symbol" not in df.columns and target in df.columns:
        df = df[[target]]  # type: ignore

    y = y.split(",") if isinstance(y, str) else y

    if y is None or same_axis is True:
        y = df.columns.to_list()
        auto_layout = True

    if same_axis is True:
        auto_layout = False

    if returns is True:
        df = df.apply(calculate_returns)  # type: ignore
        auto_layout = False

    if normalize is True:
        df = df.apply(z_score_standardization)  # type: ignore
        auto_layout = False

    if layout_kwargs is None:
        layout_kwargs = {}

    if scatter_kwargs is None:
        scatter_kwargs = {}

    try:
        fig = OpenBBFigure()
    except Exception as _:
        fig = OpenBBFigure(create_backend=True)

    fig.update_layout(ChartStyle().plotly_template.get("layout", {}))
    text_color = "white" if ChartStyle().plt_style == "dark" else "black"
    title = f"{title}" if title else ""
    xtitle = xtitle if xtitle else ""
    y1title = ytitle if ytitle else ""
    y2title = y2title if y2title else ""
    y2 = y2 if y2 else []
    yaxis_num = 1
    yaxis = f"y{yaxis_num}"
    first_y = y[0]  # type: ignore[index]
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
        df = df[sorted_columns]  # type: ignore

        for i, col in enumerate(df.columns):
            if col in y:  # type: ignore[operator]
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
        for i, col in enumerate(y):  # type: ignore[arg-type]
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
        font=dict(color=text_color),
        legend=dict(
            orientation="v",
            yanchor="top",
            xanchor="right",
            y=0.95,
            x=-0.01,
            xref="paper",
            font=dict(size=12),
            bgcolor=(
                "rgba(0,0,0,0)" if text_color == "white" else "rgba(255,255,255,0)"
            ),
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


def bar_chart(  # noqa: PLR0912
    data: Union[
        list,
        dict,
        "DataFrame",
        list["DataFrame"],
        "Series",
        list["Series"],
        "ndarray",
        Data,
    ],
    x: str,
    y: str | list[str],
    barmode: Literal["group", "stack", "relative", "overlay"] = "group",
    xtype: Literal["category", "multicategory", "date", "log", "linear"] = "category",
    title: str | None = None,
    xtitle: str | None = None,
    ytitle: str | None = None,
    orientation: Literal["h", "v"] = "v",
    colors: list[str] | None = None,
    bar_kwargs: dict[str, Any] | None = None,
    layout_kwargs: dict[str, Any] | None = None,
    **kwargs,
) -> Union["OpenBBFigure", "Figure"]:
    """Create a vertical bar chart on a single x-axis with one or more values for the y-axis.

    Parameters
    ----------
    data : Union[
        list, dict, "DataFrame", List["DataFrame"], "Series", List["Series"], "ndarray", Data
    ]
        Data to plot.
    x : str
        The x-axis column name.
    y : Union[str, List[str]]
        The y-axis column name(s).
    barmode : Literal["group", "stack", "relative", "overlay"], optional
        The bar mode, by default "group".
    xtype : Literal["category", "multicategory", "date", "log", "linear"], optional
        The x-axis type, by default "category".
    title : str, optional
        The title of the chart, by default None.
    xtitle : str, optional
        The x-axis title, by default None.
    ytitle : str, optional
        The y-axis title, by default None.
    colors: List[str], optional
        Manually set the colors to cycle through for each column in 'y', by default None.
    bar_kwargs : Dict[str, Any], optional
        Additional keyword arguments to apply with figure.add_bar(), by default None.
    layout_kwargs : Dict[str, Any], optional
        Additional keyword arguments to apply with figure.update_layout(), by default None.

    Returns
    -------
    OpenBBFigure
        The OpenBBFigure object.
    """
    # pylint: disable=import-outside-toplevel
    from openbb_charting.core.openbb_figure import OpenBBFigure

    try:
        figure = OpenBBFigure()
    except Exception as _:
        figure = OpenBBFigure(create_backend=True)

    figure = figure.create_subplots(
        1,
        1,
        shared_xaxes=True,
        vertical_spacing=0.06,
        horizontal_spacing=0.01,
        row_width=[1],
        specs=[[{"secondary_y": True}]],
    )

    figure.update_layout(ChartStyle().plotly_template.get("layout", {}))
    text_color = "white" if ChartStyle().plt_style == "dark" else "black"
    if colors is not None:
        figure.update_layout(colorway=colors)
    if bar_kwargs is None:
        bar_kwargs = {}
    if isinstance(data, (Data, list, dict)):
        data = basemodel_to_df(convert_to_basemodel(data), index=None)

    bar_df = data.copy().set_index(x)  # type: ignore
    y = y.split(",") if isinstance(y, str) else y
    hovertemplate = bar_kwargs.pop("hovertemplate", None)
    width = bar_kwargs.pop("width", None)
    for item in y:
        figure.add_bar(
            x=bar_df.index if orientation == "v" else bar_df[item],
            y=bar_df[item] if orientation == "v" else bar_df.index,
            name=bar_df[item].name,
            showlegend=len(y) > 1,
            legendgroup=bar_df[item].name,
            orientation=orientation,
            hovertemplate=(
                hovertemplate
                if hovertemplate
                else (
                    "%{fullData.name}:%{y}<extra></extra>"
                    if orientation == "v"
                    else "%{fullData.name}:%{x}<extra></extra>"
                )
            ),
            width=(
                width
                if width
                else 0.95 / len(y) * 0.75 if barmode == "group" and len(y) > 1 else 0.95
            ),
            **bar_kwargs,
        )

    figure.update_layout(
        title=dict(text=title if title else None, x=0.5, font=dict(size=16)),
        legend=dict(
            orientation="v",
            yanchor="top",
            xanchor="right",
            y=0.95,
            x=-0.01 if orientation == "v" else 1.01,
            xref="paper",
            font=dict(size=12),
            bgcolor=(
                "rgba(0,0,0,0)" if text_color == "white" else "rgba(255,255,255,0)"
            ),
        ),
        xaxis=dict(
            type=xtype,
            title=dict(
                text=xtitle if xtitle else None, standoff=30, font=dict(size=16)
            ),
            ticklen=0,
            showgrid=orientation == "h",
            tickfont=dict(size=12, family="sans-serif"),
            categoryorder="array" if orientation == "v" else None,
            categoryarray=bar_df.index if orientation == "v" else None,
        ),
        yaxis=dict(
            title=dict(
                text=ytitle if ytitle else None, standoff=30, font=dict(size=16)
            ),
            ticklen=0,
            showgrid=orientation == "v",
            tickfont=dict(size=12),
            side="left" if orientation == "h" else "right",
            categoryorder="array" if orientation == "h" else None,
            categoryarray=bar_df.index if orientation == "h" else None,
        ),
        margin=dict(pad=5),
        barmode=barmode,
        font=dict(color=text_color),
    )
    if orientation == "h":
        figure.update_layout(
            xaxis=dict(
                type="linear",
                showspikes=False,
            ),
            yaxis=dict(
                type="category",
                showspikes=False,
            ),
            hoverlabel=dict(
                font=dict(size=12),
            ),
            hovermode="y unified",
        )
    if layout_kwargs:
        figure.update_layout(
            **layout_kwargs,
        )
    return figure


def bar_increasing_decreasing(  # pylint: disable=W0102
    keys: list[str],
    values: list[int | float],
    title: str | None = None,
    xtitle: str | None = None,
    ytitle: str | None = None,
    colors: list[str] = ["blue", "red"],
    orientation: Literal["h", "v"] = "h",
    barmode: Literal["group", "stack", "relative", "overlay"] = "relative",
    layout_kwargs: dict[str, Any] | None = None,
) -> Union["OpenBBFigure", "Figure"]:
    """Create a bar chart with increasing and decreasing values represented by two colors.

    Parameters
    ----------
    keys : List[str]
        The x-axis keys.
    values : List[Any]
        The y-axis values.
    title : Optional[str], optional
        The title of the chart, by default None.
    xtitle : Optional[str], optional
        The x-axis title, by default None.
    ytitle : Optional[str], optional
        The y-axis title, by default None.
    colors : List[str], optional
        The colors to use for increasing and decreasing values, by default ["blue", "red"].
    orientation : Literal["h", "v"], optional
        The orientation of the bars, by default "h".
    barmode : Literal["group", "stack", "relative", "overlay"], optional
        The bar mode, by default "relative".
    layout_kwargs : Optional[Dict[str, Any]], optional
        Additional keyword arguments to apply with figure.update_layout(), by default None.

    Returns
    -------
    OpenBBFigure
        The OpenBBFigure object.
    """
    # pylint: disable=import-outside-toplevel
    from openbb_charting.core.openbb_figure import OpenBBFigure  # noqa
    from pandas import Series

    try:
        figure = OpenBBFigure()
    except Exception as _:
        figure = OpenBBFigure(create_backend=True)

    figure = figure.create_subplots(
        1,
        1,
        shared_xaxes=False,
        vertical_spacing=0.06,
        horizontal_spacing=0.01,
        row_width=[1],
        specs=[[{"secondary_y": True}]],
    )
    figure.update_layout(ChartStyle().plotly_template.get("layout", {}))
    text_color = "white" if ChartStyle().plt_style == "dark" else "black"

    try:
        data = Series(data=values, index=keys)
        increasing_data = data[data > 0]  # type: ignore
        decreasing_data = data[data < 0]  # type: ignore
    except Exception as e:
        raise ValueError(f"Error: {e}") from e

    if not increasing_data.empty:  # type: ignore
        figure.add_bar(
            x=increasing_data.index if orientation == "v" else increasing_data,  # type: ignore
            y=increasing_data if orientation == "v" else increasing_data.index,  # type: ignore
            marker=dict(color=colors[0]),
            orientation=orientation,
            showlegend=False,
            width=0.95 / len(keys) * 0.75 if barmode == "group" else 0.95,
            hoverinfo="y" if orientation == "v" else "x",
        )
    if not decreasing_data.empty:  # type: ignore
        figure.add_bar(
            x=decreasing_data.index if orientation == "v" else decreasing_data,  # type: ignore
            y=decreasing_data if orientation == "v" else decreasing_data.index,  # type: ignore
            marker=dict(color=colors[1]),
            orientation=orientation,
            showlegend=False,
            width=0.95 / len(keys) * 0.75 if barmode == "group" else 0.95,
            hoverinfo="y" if orientation == "v" else "x",
        )

    figure.update_layout(
        title=dict(text=title if title else None, x=0.5, font=dict(size=20)),
        hovermode="x" if orientation == "v" else "y",
        hoverlabel=dict(align="left" if orientation == "h" else "auto"),
        yaxis=dict(
            title=dict(
                text=ytitle if ytitle else None, standoff=30, font=dict(size=16)
            ),
            side="left" if orientation == "h" else "right",
            showgrid=orientation == "v",
            gridcolor="rgba(128,128,128,0.25)",
            tickfont=dict(size=12),
            ticklen=0,
            categoryorder="array" if orientation == "h" else None,
            categoryarray=keys if orientation == "h" else None,
        ),
        xaxis=dict(
            title=dict(
                text=xtitle if xtitle else None, standoff=30, font=dict(size=16)
            ),
            showgrid=orientation == "h",
            gridcolor="rgba(128,128,128,0.25)",
            tickfont=dict(size=12),
            ticklen=0,
            categoryorder="array" if orientation == "v" else None,
            categoryarray=keys if orientation == "v" else None,
        ),
        font=dict(color="white" if text_color == "white" else "black"),
        margin=dict(pad=5),
    )

    if layout_kwargs:
        figure.update_layout(
            **layout_kwargs,
        )

    return figure


def surface3d(
    X: "Series",
    Y: "Series",
    Z: "Series",
    xtitle: str | None = "DTE",
    ytitle: str | None = "Strike",
    ztitle: str | None = "IV",
    colorscale: str | list | None = None,
    title: str | None = None,
    layout_kwargs: dict[str, Any] | None = None,
    theme: Literal["dark", "light"] | None = None,
) -> Union["OpenBBFigure", "Figure"]:
    """Create a 3D surface chart.

    Parameters
    ----------
    X : pd.Series
        The x-axis data.
    Y : pd.Series
        The y-axis data.
    Z : pd.Series
        The z-axis data.
    xtitle : str, optional
        The title for the x-axis, by default "DTE".
    ytitle : str, optional
        The title for the y-axis, by default "Strike".
    ztitle : str, optional
        The title for the z-axis, by default "IV".
    colorscale : Union[str, list], optional
        The colorscale to use for the surface, by default None.
    title : str, optional
        The title of the chart, by default None.
    layout_kwargs : Optional[dict[str, Any]], optional
        Additional keyword arguments to apply with figure.update_layout(), by default None.

    Returns
    -------
    OpenBBFigure
        The OpenBBFigure object.
    """
    # pylint: disable=import-outside-toplevel
    from openbb_core.app.model.abstract.error import OpenBBError  # noqa
    from openbb_charting.core.openbb_figure import OpenBBFigure
    from numpy import vstack
    from scipy.spatial import Delaunay
    import numpy as np

    try:
        points3D = vstack((X, Y, Z)).T
        points2D = points3D[:, :2]
        tri = Delaunay(points2D)
        II, J, K = tri.simplices.T
    except Exception as e:
        raise OpenBBError(f"Not enough points to render 3D: {e}") from e

    fig = OpenBBFigure(create_backend=False)
    chart_style = ChartStyle()
    if theme:
        chart_style.plt_style = theme
    fig.update_layout(chart_style.plotly_template.get("layout", {}))
    text_color = "white" if chart_style.plt_style == "dark" else "black"
    fig.set_title(f"{title if title and title != 'OpenBB Platform' else ''}")
    fig_kwargs = dict(z=Z, x=X, y=Y, i=II, j=J, k=K, intensity=Z)
    customdata = np.array([[xtitle, ytitle, ztitle]] * len(X))

    fig.add_mesh3d(
        **fig_kwargs,
        alphahull=0,
        opacity=1,
        contour=dict(color="black", show=True, width=15),
        colorscale=(
            colorscale
            if colorscale
            else [
                [0, "darkred"],
                [0.001, "crimson"],
                [0.005, "red"],
                [0.0075, "orangered"],
                [0.015, "darkorange"],
                [0.025, "orange"],
                [0.04, "goldenrod"],
                [0.055, "gold"],
                [0.11, "magenta"],
                [0.15, "plum"],
                [0.4, "lightblue"],
                [0.7, "royalblue"],
                [0.9, "blue"],
                [1, "darkblue"],
            ]
        ),
        colorbar=dict(
            len=0.66,
            y=0.5,
            thickness=15,
        ),
        customdata=customdata,
        hovertemplate="<b>%{customdata[0]}</b>: %{x} <br>"
        "<b>%{customdata[1]}</b>: %{y} <br>"
        "<b>%{customdata[2]}</b>: %{z}<extra></extra>",
        showscale=True,
        flatshading=True,
        lighting=dict(
            ambient=0.95,
            diffuse=0.9,
            roughness=0.8,
            specular=0.9,
            fresnel=0.001,
            vertexnormalsepsilon=0.0001,
            facenormalsepsilon=0.0001,
        ),
    )
    fig.update_layout(
        scene=dict(
            xaxis=dict(
                backgroundcolor="rgb(94, 94, 94)",
                gridcolor="white",
                showbackground=True,
                zerolinecolor="white",
                title=dict(text=xtitle if xtitle else "DTE", font=dict(size=18)),
                autorange="reversed",
                tickfont=dict(size=12),
            ),
            yaxis=dict(
                backgroundcolor="rgb(94, 94, 94)",
                gridcolor="white",
                showbackground=True,
                zerolinecolor="white",
                title=dict(text=ytitle if ytitle else "Strike", font=dict(size=18)),
                tickfont=dict(size=12),
            ),
            zaxis=dict(
                backgroundcolor="rgb(94, 94, 94)",
                gridcolor="white",
                showbackground=True,
                zerolinecolor="white",
                title=dict(text=ztitle if ztitle else "IV", font=dict(size=18)),
                tickfont=dict(size=12),
            ),
            domain=dict(y=[0.0125, 0.95], x=[0.0125, 1]),
        ),
        title_x=0.5,
        title_y=0.98,
        scene_camera=dict(
            up=dict(x=0, y=0, z=0.75),
            center=dict(x=-0.01, y=0, z=-0.3),
            eye=dict(x=1.75, y=1.75, z=0.69),
        ),
        font=dict(color=text_color),
    )

    fig.update_scenes(
        aspectmode="manual",
        aspectratio=dict(x=1.5, y=2.0, z=0.75),
        dragmode="turntable",
    )

    if layout_kwargs:
        fig.update_layout(layout_kwargs, overwrite=False)

    return fig
