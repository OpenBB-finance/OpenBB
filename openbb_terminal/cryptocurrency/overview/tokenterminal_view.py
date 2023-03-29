"""Token Terminal View"""
import logging
import os

from openbb_terminal import OpenBBFigure, theme
from openbb_terminal.cryptocurrency.overview.tokenterminal_model import (
    CATEGORIES,
    METRICS,
    TIMELINES,
    get_fundamental_metrics,
)
from openbb_terminal.decorators import check_api_key, log_start_end
from openbb_terminal.helper_funcs import export_data
from openbb_terminal.rich_config import console

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
@check_api_key(["API_TOKEN_TERMINAL_KEY"])
def display_fundamental_metrics(
    metric: str,
    category: str = "",
    timeline: str = "24h",
    ascend: bool = False,
    limit: int = 10,
    export: str = "",
    external_axes: bool = False,
):
    """Display fundamental metrics [Source: Token Terminal]

    Parameters
    ----------
    metric : str
        The metric of interest. See `get_possible_metrics()` for available metrics.
    category : str
        The category of interest. See `get_possible_categories()` for available categories.
        The default value is an empty string which means that all categories are considered.
    timeline : str
        The category of interest. See `get_possible_timelines()` for available timelines.
    ascend : bool
        Direction of the sort. If True, the data is sorted in ascending order.
    limit : int
        The number of rows to display.
    export : str
        Export dataframe data to csv,json,xlsx file
    external_axes : bool, optional
        Whether to return the figure object or not, by default False
    """
    if metric not in METRICS:
        return console.print(
            "[red]Invalid metric selected. See available metrics with get_possible_metrics()[/red]\n"
        )

    if category not in CATEGORIES and category != "":
        return console.print(
            "[red]Invalid category selected. See available categories with get_possible_categories()[/red]\n"
        )

    if timeline not in TIMELINES:
        return console.print(
            "[red]Invalid timeline selected. See available timelines with get_possible_timelines()[/red]\n"
        )

    metric_series = get_fundamental_metrics(
        metric=metric, category=category, timeline=timeline, ascend=ascend
    )

    if metric_series.empty:
        return console.print("\n[/red]No data found[/red]\n")

    fig = OpenBBFigure()

    fig.add_bar(
        x=metric_series[:limit].index,
        y=metric_series[:limit].values,
        marker_color=theme.get_colors(reverse=True)[:limit],
    )

    if category:
        fig.set_xaxis_title(category, tickangle=-15)
    else:
        fig.set_xaxis_title("Dapps and Blockchains", tickangle=-15)

    labeltouse = "Followers" if metric == "twitter_followers" else "[USD]"

    fig.set_yaxis_title(f"{metric.replace('_', ' ').capitalize()} {labeltouse}")

    fig.set_title(f"{metric.replace('_', ' ').capitalize()} from past {timeline}")

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "fun",
        metric_series,
        figure=fig,
    )

    return fig.show(external=external_axes)
