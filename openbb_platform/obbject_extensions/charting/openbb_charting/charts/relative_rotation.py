"""Relative Rotation Chart Helpers."""

# pylint: disable=R0917

from datetime import date as dateType
from typing import TYPE_CHECKING, Literal
from warnings import warn

if TYPE_CHECKING:
    from pandas import DataFrame
    from plotly.graph_objects import Figure

color_sequence = [
    "burlywood",
    "orange",
    "grey",
    "magenta",
    "cyan",
    "yellowgreen",
    "#1f77b4",
    "#aec7e8",
    "#ff7f0e",
    "#ffbb78",
    "#d62728",
    "#ff9896",
    "#9467bd",
    "#c5b0d5",
    "#8c564b",
    "#c49c94",
    "#e377c2",
    "#f7b6d2",
    "#7f7f7f",
    "#c7c7c7",
    "#bcbd22",
    "#dbdb8d",
    "#17becf",
    "#9edae5",
    "#7e7e7e",
    "#1b9e77",
    "#d95f02",
    "#7570b3",
    "#e7298a",
    "#66a61e",
    "#e6ab02",
    "#a6761d",
    "#666666",
    "#f0027f",
    "#bf5b17",
    "#d9f202",
    "#8dd3c7",
    "#ffffb3",
    "#bebada",
    "#fb8072",
    "#80b1d3",
    "#fdb462",
    "#b3de69",
    "#fccde5",
    "#d9d9d9",
    "#bc80bd",
    "#ccebc5",
    "#ffed6f",
    "#6a3d9a",
    "#b15928",
    "#b2df8a",
    "#33a02c",
    "#fb9a99",
    "#e31a1c",
    "#fdbf6f",
    "#ff7f00",
    "#cab2d6",
    "#6a3d9a",
    "#ffff99",
    "#b15928",
]


def create_rrg_with_tails(
    ratios_data: "DataFrame",
    momentum_data: "DataFrame",
    study: str,
    benchmark_symbol: str,
    tail_periods: int,
    tail_interval: Literal["day", "week", "month"],
) -> "Figure":
    """Create The Relative Rotation Graph With Tails.

    Parameters
    ----------
    ratios_data : DataFrame
        The DataFrame containing the RS-Ratio values.
    momentum_data : DataFrame
        The DataFrame containing the RS-Momentum values.
    study : str
        The study that was selected when loading the raw data.
        If custom data is supplied, this will override the study for the chart titles.
    benchmark_symbol : str
        The symbol of the benchmark.
    tail_periods : int
        The number of periods to display in the tails.
    tail_interval : Literal["day", "week", "month"]

    Returns
    -------
    Figure
        Plotly GraphObjects Figure.
    """
    # pylint: disable=import-outside-toplevel
    from pandas import to_datetime
    from plotly import graph_objects as go

    symbols = ratios_data.columns.to_list()

    tail_dict = {"week": "W", "month": "ME"}
    ratios_data.index = to_datetime(ratios_data.index)
    momentum_data.index = to_datetime(momentum_data.index)

    if tail_interval != "day":
        ratios_data = ratios_data.resample(tail_dict[tail_interval]).last()
        momentum_data = momentum_data.resample(tail_dict[tail_interval]).last()
    ratios_data = ratios_data.iloc[-tail_periods:]
    momentum_data = momentum_data.iloc[-tail_periods:]
    _tail_periods = len(ratios_data)
    tail_title = (
        f"The Previous {_tail_periods} {tail_interval.capitalize()}s "
        f"Ending {ratios_data.index[-1].strftime('%Y-%m-%d')}"
    )
    x_min = ratios_data.min().min()
    x_max = ratios_data.max().max()
    y_min = momentum_data.min().min()
    y_max = momentum_data.max().max()
    # Create an empty list to store the scatter traces
    frames: list = []
    x_data = ratios_data
    y_data = momentum_data
    for i, date in enumerate(ratios_data.index):  # pylint: disable=unused-variable
        frame_data: list = []

        for j, symbol in enumerate(symbols):
            x_frame_data = x_data[symbol].iloc[: i + 1]
            y_frame_data = y_data[symbol].iloc[: i + 1]
            name = symbol.upper().replace("^", "").replace(":US", "")
            special_name = "-" in name or len(name) > 7
            marker_size = 34 if special_name else 30
            line_frame_trace = go.Scatter(
                x=x_frame_data,
                y=y_frame_data,
                mode="markers+lines",
                line=dict(color=color_sequence[j], width=2, dash="dash"),
                marker=dict(
                    size=5, color=color_sequence[j], line=dict(color="black", width=1)
                ),
                showlegend=False,
                opacity=0.3,
                name=name,
                text=name,
                hovertemplate="<b>%{fullData.name}</b>: "
                + "RS-Ratio: %{x:.4f}, "
                + "RS-Momentum: %{y:.4f}"
                + "<extra></extra>",
                hoverlabel=dict(font_size=10),
            )

            marker_frame_trace = go.Scatter(
                x=[x_frame_data.iloc[-1]],
                y=[y_frame_data.iloc[-1]],
                mode="markers+text",
                name=name,
                text=name,
                textposition="middle center",
                textfont=(
                    dict(size=10, color="black")
                    if len(symbol) < 4
                    else dict(size=7, color="black")
                ),
                line=dict(color=color_sequence[j], width=2, dash="dash"),
                marker=dict(
                    size=marker_size,
                    color=color_sequence[j],
                    line=dict(color="black", width=1),
                ),
                opacity=0.9,
                showlegend=False,
                hovertemplate="<b>%{fullData.name}</b>: RS-Ratio: %{x:.4f}, RS-Momentum: %{y:.4f}<extra></extra>",
            )

            frame_data.extend([line_frame_trace, marker_frame_trace])

        frames.append(go.Frame(data=frame_data, name=f"Frame {i}"))

    # Define the initial trace for the figure
    initial_trace = frames[0]["data"]

    padding = 0.1
    y_range = [y_min - padding * abs(y_min) - 0.3, y_max + padding * abs(y_max) + 0.3]
    x_range = [x_min - padding * abs(x_min) - 0.3, x_max + padding * abs(x_max) + 0.3]

    # Create the layout for the figure
    layout = go.Layout(
        title={
            "text": (
                f"Relative Rotation Against {benchmark_symbol.replace('^', '')} {study.capitalize()} For {tail_title}"
            ),
            "x": 0.5,
            "xanchor": "center",
            "font": dict(size=18),
        },
        xaxis=dict(
            title=dict(text="RS-Ratio", font=dict(size=16)),
            showgrid=True,
            zeroline=True,
            showline=True,
            mirror=True,
            ticklen=0,
            zerolinecolor="black",
            range=x_range,
            gridcolor="lightgrey",
            showspikes=False,
        ),
        yaxis=dict(
            title=dict(text="RS-Momentum", font=dict(size=16)),
            showgrid=True,
            zeroline=True,
            showline=True,
            mirror=True,
            ticklen=0,
            zerolinecolor="black",
            range=y_range,
            gridcolor="lightgrey",
            side="left",
            title_standoff=5,
        ),
        plot_bgcolor="rgba(255,255,255,1)",
        shapes=[
            go.layout.Shape(
                type="rect",
                xref="x",
                yref="y",
                x0=0,
                y0=0,
                x1=x_range[1],
                y1=y_range[1],
                fillcolor="lightgreen",
                opacity=0.3,
                layer="below",
                line_width=0,
            ),
            go.layout.Shape(
                type="rect",
                xref="x",
                yref="y",
                x0=x_range[0],
                y0=0,
                x1=0,
                y1=y_range[1],
                fillcolor="lightblue",
                opacity=0.3,
                layer="below",
                line_width=0,
            ),
            go.layout.Shape(
                type="rect",
                xref="x",
                yref="y",
                x0=x_range[0],
                y0=y_range[0],
                x1=0,
                y1=0,
                fillcolor="lightpink",
                opacity=0.3,
                layer="below",
                line_width=0,
            ),
            go.layout.Shape(
                type="rect",
                xref="x",
                yref="y",
                x0=0,
                y0=y_range[0],
                x1=x_range[1],
                y1=0,
                fillcolor="lightyellow",
                opacity=0.3,
                layer="below",
                line_width=0,
            ),
            go.layout.Shape(
                type="rect",
                xref="x",
                yref="y",
                x0=x_range[0],
                y0=y_range[0],
                x1=x_range[1],
                y1=y_range[1],
                line=dict(
                    color="Black",
                    width=1,
                ),
                fillcolor="rgba(0,0,0,0)",
                layer="above",
            ),
        ],
        annotations=[
            go.layout.Annotation(
                x=1,
                xref="paper",
                y=1,
                yref="paper",
                text="Leading",
                showarrow=False,
                font=dict(
                    size=18,
                    color="darkgreen",
                ),
            ),
            go.layout.Annotation(
                x=1,
                xref="paper",
                y=0,
                yref="paper",
                text="Weakening",
                showarrow=False,
                font=dict(
                    size=18,
                    color="goldenrod",
                ),
            ),
            go.layout.Annotation(
                x=0,
                xref="paper",
                y=0,
                yref="paper",
                text="Lagging",
                showarrow=False,
                font=dict(
                    size=18,
                    color="red",
                ),
            ),
            go.layout.Annotation(
                x=0,
                xref="paper",
                yref="paper",
                y=1,
                text="Improving",
                showarrow=False,
                font=dict(
                    size=18,
                    color="blue",
                ),
            ),
        ],
        autosize=True,
        margin=dict(
            l=30,
            r=50,
            b=50,
            t=50,
            pad=0,
        ),
        dragmode="pan",
        hovermode="closest",
        updatemenus=[
            {
                "buttons": [
                    {
                        "args": [
                            None,
                            {
                                "frame": {"duration": 500, "redraw": False},
                                "fromcurrent": True,
                                "transition": {"duration": 500, "easing": "linear"},
                            },
                        ],
                        "label": "Play",
                        "method": "animate",
                    }
                ],
                "direction": "left",
                "pad": {"r": 0, "t": 75},
                "showactive": False,
                "type": "buttons",
                "x": -0.025,
                "xanchor": "left",
                "y": 0,
                "yanchor": "top",
                "bgcolor": "rgba(150, 150, 150, 0.8)",
                "bordercolor": "rgba(100, 100, 100, 0.5)",
                "borderwidth": 1,
                "font": {"color": "black"},
            }
        ],
        sliders=[
            {
                "active": 0,
                "yanchor": "top",
                "xanchor": "center",
                "currentvalue": {
                    "font": {"size": 16},
                    "prefix": "Date: ",
                    "visible": True,
                    "xanchor": "right",
                },
                "transition": {"duration": 300, "easing": "cubic-in-out"},
                "pad": {"b": 10, "t": 50},
                "len": 0.9,
                "x": 0.5,
                "y": 0,
                "steps": [
                    {
                        "label": f"{x_data.index[i].strftime('%Y-%m-%d')}",
                        "method": "animate",
                        "args": [
                            [f"Frame {i}"],
                            {
                                "mode": "immediate",
                                "transition": {"duration": 300},
                                "frame": {"duration": 300, "redraw": False},
                            },
                        ],
                    }
                    for i in range(len(x_data.index))
                ],
            }
        ],
    )

    # Create the figure and add the initial trace
    fig = go.Figure(data=initial_trace, layout=layout, frames=frames)

    return fig


def create_rrg_without_tails(
    ratios_data: "DataFrame",
    momentum_data: "DataFrame",
    benchmark_symbol: str,
    study: str,
    date: dateType | None = None,
) -> "Figure":
    """Create the Plotly Figure Object without Tails.

    Parameters
    ----------
    ratios_data : DataFrame
        The DataFrame containing the RS-Ratio values.
    momentum_data : DataFrame
        The DataFrame containing the RS-Momentum values.
    benchmark_symbol : str
        The symbol of the benchmark.
    study: str
        The study that was selected when loading the raw data.
        If custom data is supplied, this will override the study for the chart titles.
    date : Optional[dateType], optional
        A specific date within the data to target for display, by default None.

    Returns
    -------
    Figure
        Plotly GraphObjects Figure.
    """
    # pylint: disable=import-outside-toplevel
    from plotly import graph_objects as go  # noqa
    from pandas import to_datetime  # noqa

    if date is not None and date not in ratios_data.index.astype(str):
        warn(f"Date {str(date)} not found in data, using the last available date.")
        date = ratios_data.index[-1]
    if date is None:
        date = ratios_data.index[-1]

    # Select a single row from each dataframe
    row_x = ratios_data.loc[to_datetime(date).date()]  # type: ignore
    row_y = momentum_data.loc[to_datetime(date).date()]  # type: ignore

    x_max = row_x.max() + 0.5
    x_min = row_x.min() - 0.5
    y_max = row_y.max() + 0.5
    y_min = row_y.min() - 0.5

    # Create an empty list to store the scatter traces
    traces = []

    # Loop through each column in the row_x dataframe
    for i, (column_name, value_x) in enumerate(row_x.items()):
        # Retrieve the corresponding value from the row_y dataframe
        value_y = row_y[column_name]  # type: ignore
        marker_name = column_name.upper().replace("^", "").replace(":US", "")  # type: ignore
        special_name = "-" in marker_name or len(marker_name) > 5
        marker_size = 38 if special_name else 30
        # Create a scatter trace for each column
        trace = go.Scatter(
            x=[value_x],
            y=[value_y],
            mode="markers+text",
            text=[marker_name],
            textposition="middle center",
            textfont=dict(size=10 if len(marker_name) < 4 else 8, color="black"),
            marker=dict(
                size=marker_size,
                color=color_sequence[i % len(color_sequence)],
                line=dict(color="black", width=1),
            ),
            name=column_name,
            showlegend=False,
            hovertemplate="<b>%{fullData.name}</b>"
            + "<br>RS-Ratio: %{x:.4f}</br>"
            + "RS-Momentum: %{y:.4f}"
            + "<extra></extra>",
        )
        # Add the trace to the list
        traces.append(trace)

    padding = 0.1
    y_range = [y_min - padding * abs(y_min) - 0.3, y_max + padding * abs(y_max)]
    x_range = [x_min - padding * abs(x_min), x_max + padding * abs(x_max)]

    layout = go.Layout(
        title={
            "text": (
                f"RS-Ratio vs RS-Momentum of {study.capitalize()} "
                f"Against {benchmark_symbol.replace('^', '')} - {to_datetime(row_x.name).strftime('%Y-%m-%d')}"  # type: ignore
            ),
            "x": 0.5,
            "xanchor": "center",
            "font": dict(size=20),
        },
        xaxis=dict(
            title="RS-Ratio",
            zerolinecolor="black",
            range=x_range,
            showspikes=False,
        ),
        yaxis=dict(
            title="<br>RS-Momentum",
            zerolinecolor="black",
            range=y_range,
            side="left",
            title_standoff=5,
            showspikes=False,
        ),
        shapes=[
            go.layout.Shape(
                type="rect",
                xref="x",
                yref="y",
                x0=0,
                y0=0,
                x1=x_range[1],
                y1=y_range[1],
                fillcolor="lightgreen",
                opacity=0.3,
                layer="below",
                line_width=0,
            ),
            go.layout.Shape(
                type="rect",
                xref="x",
                yref="y",
                x0=x_range[0],
                y0=0,
                x1=0,
                y1=y_range[1],
                fillcolor="lightblue",
                opacity=0.3,
                layer="below",
                line_width=0,
            ),
            go.layout.Shape(
                type="rect",
                xref="x",
                yref="y",
                x0=x_range[0],
                y0=y_range[0],
                x1=0,
                y1=0,
                fillcolor="lightpink",
                opacity=0.3,
                layer="below",
                line_width=0,
            ),
            go.layout.Shape(
                type="rect",
                xref="x",
                yref="y",
                x0=0,
                y0=y_range[0],
                x1=x_range[1],
                y1=0,
                fillcolor="lightyellow",
                opacity=0.3,
                layer="below",
                line_width=0,
            ),
            go.layout.Shape(
                type="rect",
                xref="x",
                yref="y",
                x0=x_range[0],
                y0=y_range[0],
                x1=x_range[1],
                y1=y_range[1],
                line=dict(
                    color="Black",
                    width=1,
                ),
                fillcolor="rgba(0,0,0,0)",
                layer="above",
            ),
        ],
        annotations=[
            go.layout.Annotation(
                x=1,
                xref="paper",
                y=1,
                yref="paper",
                text="Leading",
                showarrow=False,
                font=dict(
                    size=18,
                    color="darkgreen",
                ),
            ),
            go.layout.Annotation(
                x=1,
                xref="paper",
                y=0,
                yref="paper",
                text="Weakening",
                showarrow=False,
                font=dict(
                    size=18,
                    color="goldenrod",
                ),
            ),
            go.layout.Annotation(
                x=0,
                xref="paper",
                y=0,
                yref="paper",
                text="Lagging",
                showarrow=False,
                font=dict(
                    size=18,
                    color="red",
                ),
            ),
            go.layout.Annotation(
                x=0,
                xref="paper",
                yref="paper",
                y=1,
                text="Improving",
                showarrow=False,
                font=dict(
                    size=18,
                    color="blue",
                ),
            ),
        ],
        autosize=True,
        margin=dict(
            l=30,
            r=50,
            b=50,
            t=50,
            pad=0,
        ),
        dragmode="pan",
    )

    fig = go.Figure(data=traces, layout=layout)

    return fig
