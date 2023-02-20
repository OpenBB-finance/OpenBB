"""Token Terminal View"""
import logging
import os
from typing import List, Optional

import pandas as pd
from matplotlib import pyplot as plt

from openbb_terminal.config_plot import PLOT_DPI
from openbb_terminal.config_terminal import theme
from openbb_terminal.cryptocurrency.due_diligence.tokenterminal_model import (
    METRICS,
    get_description,
    get_fundamental_metric_from_project,
    get_project_ids,
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
def display_fundamental_metric_from_project_over_time(
    metric: str,
    project: str,
    export: str = "",
    sheet_name: Optional[str] = None,
    external_axes: Optional[List[plt.Axes]] = None,
):
    """Plots fundamental metric from a project over time [Source: Token Terminal]

    Parameters
    ----------
    metric : str
        The metric of interest. See `get_possible_metrics()` for available metrics.
    project : str
        The project of interest. See `get_project_ids()` for available categories.
    export : str
        Export dataframe data to csv,json,xlsx file
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
    """
    if project not in get_project_ids():
        console.print(
            f"[red]'{project}' project selected is invalid. See available projects with def get_project_ids()[/red]\n"
        )
        return

    if metric not in METRICS:
        console.print(
            f"[red]'{metric}' metric selected is invalid.  See available metrics with get_possible_metrics()[/red]\n"
        )
        return

    metric_over_time = get_fundamental_metric_from_project(metric, project)

    if metric_over_time.empty:
        console.print("[red]No data found.[/red]\n")
        return

    # This plot has 1 axis
    if external_axes is None:
        _, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
    elif is_valid_axes_count(external_axes, 1):
        (ax,) = external_axes
    else:
        return

    ax.plot(
        metric_over_time.index,
        metric_over_time.values
        if max(metric_over_time.values) < 10000
        else metric_over_time.values / 1e6,
    )
    ax.set_xlabel("Time")
    if max(metric_over_time.values) < 10000:
        labeltouse = "[USD]"
    else:
        labeltouse = "[1M USD]"
    ax.set_ylabel(f"{metric.replace('_', ' ').capitalize()} {labeltouse}")
    ax.set_xlim([metric_over_time.index[0], metric_over_time.index[-1]])

    ax.set_title(
        f"{project.replace('_', ' ').capitalize()} {metric.replace('_', ' ').capitalize()}"
    )

    theme.style_primary_axis(ax)

    if external_axes is None:
        theme.visualize_output()

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "funot",
        metric_over_time,
        sheet_name,
    )


@log_start_end(log=logger)
@check_api_key(["API_TOKEN_TERMINAL_KEY"])
def display_description(
    project: str, export: str = "", sheet_name: Optional[str] = None
):
    """Prints description from a project [Source: Token Terminal]

    Parameters
    ----------
    project : str
        The project of interest. See `get_project_ids()` for available categories.
    export : str
        Export dataframe data to csv,json,xlsx file
    """
    if project not in get_project_ids():
        console.print(
            f"[red]'{project}' project selected is invalid. See available projects with def get_project_ids()[/red]\n"
        )
        return

    description = get_description(project)

    for k in description:
        console.print(f"{k.replace('_', ' ').upper()}\n   {description[k]}\n")

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "desc",
        pd.DataFrame(description.values(), index=description.keys()),
        sheet_name,
    )
