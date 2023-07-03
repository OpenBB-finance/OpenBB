from datetime import datetime
from typing import List

from plotly import graph_objects as go
from pydantic import BaseModel


class YTimeSeries(BaseModel):
    data: List[float]
    name: str
    color: str


def plot_timeseries(
    x: List[datetime],
    y: List[YTimeSeries],
    title: str,
    xaxis_title: str,
    yaxis_title: str,
    legend_title: str,
) -> go.Figure:
    fig = go.Figure()
    for y_data in y:
        fig.add_trace(
            go.Scatter(
                x=x,
                y=y_data.data,
                name=y_data.name,
                line=dict(color=y_data.color, width=1),
            )
        )
    fig.update_layout(
        title=title,
        xaxis_title=xaxis_title,
        yaxis_title=yaxis_title,
        legend_title=legend_title,
    )
    return fig
