"""Token Terminal View"""
import logging
import os
from typing import Optional, Union

import pandas as pd

from openbb_terminal import OpenBBFigure
from openbb_terminal.cryptocurrency.due_diligence.tokenterminal_model import (
    METRICS,
    get_description,
    get_fundamental_metric_from_project,
    get_project_ids,
)
from openbb_terminal.decorators import check_api_key, log_start_end
from openbb_terminal.helper_funcs import export_data
from openbb_terminal.rich_config import console

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
@check_api_key(["API_TOKEN_TERMINAL_KEY"])
def display_fundamental_metric_from_project_over_time(
    metric: str,
    project: str,
    export: str = "",
    sheet_name: Optional[str] = None,
    external_axes: bool = False,
) -> Union[None, OpenBBFigure]:
    """Plots fundamental metric from a project over time [Source: Token Terminal]

    Parameters
    ----------
    metric : str
        The metric of interest. See `get_possible_metrics()` for available metrics.
    project : str
        The project of interest. See `get_project_ids()` for available categories.
    export : str
        Export dataframe data to csv,json,xlsx file
    external_axes : bool, optional
        Whether to return the figure object or not, by default False
    """
    if project not in get_project_ids():
        return console.print(
            f"[red]'{project}' project selected is invalid. See available projects with def get_project_ids()[/red]\n"
        )

    if metric not in METRICS:
        return console.print(
            f"[red]'{metric}' metric selected is invalid.  See available metrics with get_possible_metrics()[/red]\n"
        )

    metric_over_time = get_fundamental_metric_from_project(metric, project)

    if metric_over_time.empty:
        return console.print("[red]No data found.[/red]\n")

    fig = OpenBBFigure(
        xaxis_title="Date", yaxis_title=f"{metric.replace('_', ' ').capitalize()} [USD]"
    )
    fig.set_title(
        f"{project.replace('_', ' ').capitalize()} {metric.replace('_', ' ').capitalize()}"
    )

    fig.add_scatter(
        x=metric_over_time.index,
        y=metric_over_time.values,
        name=f"{project.replace('_', ' ').title()}",
    )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "funot",
        metric_over_time,
        sheet_name,
        fig,
    )

    return fig.show(external=external_axes)


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
