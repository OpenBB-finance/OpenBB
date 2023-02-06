"""Token Terminal View"""
import logging
import os
from typing import List, Optional

from matplotlib import pyplot as plt

from openbb_terminal import config_terminal as cfg
from openbb_terminal.config_plot import PLOT_DPI
from openbb_terminal.config_terminal import theme
from openbb_terminal.cryptocurrency.overview.tokenterminal_model import (
    CATEGORIES,
    METRICS,
    TIMELINES,
    get_fundamental_metrics,
)
from openbb_terminal.decorators import check_api_key, log_start_end
from openbb_terminal.helper_funcs import (
    export_data,
    is_valid_axes_count,
    plot_autoscale,
)
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
    external_axes: Optional[List[plt.Axes]] = None,
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
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
    """
    if metric not in METRICS:
        console.print(
            "[red]Invalid metric selected. See available metrics with get_possible_metrics()[/red]\n"
        )
        return

    if category not in CATEGORIES and category != "":
        console.print(
            "[red]Invalid category selected. See available categories with get_possible_categories()[/red]\n"
        )
        return

    if timeline not in TIMELINES:
        console.print(
            "[red]Invalid timeline selected. See available timelines with get_possible_timelines()[/red]\n"
        )
        return

    metric_series = get_fundamental_metrics(
        metric=metric, category=category, timeline=timeline, ascend=ascend
    )

    if metric_series.empty:
        console.print("\n[/red]No data found[/red]\n")

    else:
        # This plot has 1 axis
        if external_axes is None:
            _, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
        elif is_valid_axes_count(external_axes, 1):
            (ax,) = external_axes
        else:
            return

        num = max(metric_series[:limit].values)
        magnitude = 0
        while abs(num) >= 1000:
            magnitude += 1
            num /= 1000.0

        ax.bar(
            metric_series[:limit].index,
            metric_series[:limit].values
            if magnitude == 0
            else metric_series[:limit].values / (1000.0**magnitude),
            color=cfg.theme.get_colors(reverse=True)[:limit],
        )

        if category:
            ax.set_xlabel(category)
        else:
            ax.set_xlabel("Dapps and Blockchains")

        if metric == "twitter_followers":
            if max(metric_series[:limit].values) < 10_000:
                labeltouse = "Followers"
            else:
                labeltouse = f"[1{' KMBTP'[magnitude]}] Followers"
        else:
            if max(metric_series[:limit].values) < 10_000:
                labeltouse = "[USD]"
            else:
                labeltouse = f"[1{' KMBTP'[magnitude]} USD]"

        ax.set_ylabel(f"{metric.replace('_', ' ').capitalize()} {labeltouse}")

        ax.set_title(f"{metric.replace('_', ' ').capitalize()} from past {timeline}")
        plt.xticks(rotation=45)

        theme.style_primary_axis(ax)

        if not external_axes:
            theme.visualize_output()

        export_data(
            export, os.path.dirname(os.path.abspath(__file__)), "fun", metric_series
        )
