"""GitHub View Module"""
__docformat__ = "numpy"

import logging
import os
from typing import Optional, List

from matplotlib import pyplot as plt
from matplotlib import ticker
from openbb_terminal.config_terminal import theme
from openbb_terminal.config_plot import PLOT_DPI
from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import (
    export_data,
    plot_autoscale,
    print_rich_table,
)
from openbb_terminal.alternative.oss import github_model
from openbb_terminal.cryptocurrency.dataframe_helpers import (
    lambda_long_number_format_with_type_check,
)
from openbb_terminal.rich_config import console

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def display_star_history(
    repo: str, export: str = "", external_axes: Optional[List[plt.Axes]] = None
) -> None:
    """Display repo summary [Source: https://api.github.com]

    Parameters
    ----------
    repo : str
            Repository to display star history. Format: org/repo, e.g., openbb-finance/openbbterminal
    export : str
            Export dataframe data to csv,json,xlsx file
    external_axes : Optional[List[plt.Axes]], optional
            External axes (1 axis is expected in the list), by default None
    """
    df = github_model.get_stars_history(repo)
    if not df.empty:
        if external_axes is None:
            _, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
        else:
            if len(external_axes) != 1:
                logger.error("Expected list of one axis item.")
                console.print("[red]Expected list of one axis item./n[/red]")
                return
            (ax,) = external_axes
        ax.plot(df["Date"], df["Stars"])

        ax.set_xlabel("Date")
        ax.set_ylabel("Stars")
        ax.set_title(f"Star History for {repo}")

        theme.style_primary_axis(ax)

        if external_axes is None:
            theme.visualize_output()

        export_data(export, os.path.dirname(os.path.abspath(__file__)), "sh", df)


@log_start_end(log=logger)
def display_top_repos(
    sortby: str,
    categories: str,
    limit: int,
    export: str = "",
    external_axes: Optional[List[plt.Axes]] = None,
) -> None:
    """Display repo summary [Source: https://api.github.com]

    Parameters
    ----------
    sortby : str
            Sort repos by {stars, forks}
    categories : str
            Check for repo categories. If more than one separate with a comma: e.g., finance,investment. Default: None
    limit : int
    Number of repos to look at
    export : str
    Export dataframe data to csv,json,xlsx file
    external_axes : Optional[List[plt.Axes]], optional
    External axes (1 axis is expected in the list), by default None
    """
    df = github_model.get_top_repos(categories=categories, sortby=sortby, top=limit)
    if not df.empty:
        if sortby == "forks":
            df = df.sort_values(by="forks_count")
        elif sortby == "stars":
            df = df.sort_values(by="stargazers_count")
        if external_axes is None:
            _, ax = plt.subplots(figsize=(14, 8), dpi=PLOT_DPI)
        else:
            if len(external_axes) != 1:
                logger.error("Expected list of one axis item.")
                console.print("[red]Expected list of one axis item./n[/red]")
                return
            (ax, _) = external_axes
        for _, row in df.iterrows():
            ax.barh(
                y=row["full_name"],
                width=row["stargazers_count" if sortby == "stars" else "forks_count"],
                height=0.5,
            )

        ax.set_xlabel(sortby.capitalize())
        ax.get_xaxis().set_major_formatter(
            ticker.FuncFormatter(
                lambda x, _: lambda_long_number_format_with_type_check(x)
            )
        )
        ax.yaxis.set_label_position("left")
        ax.yaxis.set_ticks_position("left")
        ax.set_ylabel("Repository Full Name")
        category_substr = "ies" if "," in categories else "y"
        category_str = f"categor{category_substr} {categories} " if categories else ""
        ax.set_title(f"Top repos {category_str}sorted by {sortby}")
        theme.style_primary_axis(ax)

        if external_axes is None:
            theme.visualize_output()

        export_data(export, os.path.dirname(os.path.abspath(__file__)), "tr", df)


@log_start_end(log=logger)
def display_repo_summary(repo: str, export: str = "") -> None:
    """Display repo summary [Source: https://api.github.com]

    Parameters
    ----------
    repo : str
            Repository to display summary. Format: org/repo, e.g., openbb-finance/openbbterminal
    export : str
    Export dataframe data to csv,json,xlsx file
    """
    df = github_model.get_repo_summary(repo)
    if not df.empty:
        print_rich_table(
            df, headers=list(df.columns), show_index=False, title="Repo summary"
        )
        console.print("")

        export_data(
            export,
            os.path.dirname(os.path.abspath(__file__)),
            "rs",
            df,
        )
