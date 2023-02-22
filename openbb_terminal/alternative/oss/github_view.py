"""GitHub View Module"""
__docformat__ = "numpy"

import logging
import os
from typing import Optional, Union

from openbb_terminal import OpenBBFigure
from openbb_terminal.alternative.oss import github_model
from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import export_data, print_rich_table

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def display_star_history(
    repo: str,
    export: str = "",
    sheet_name: Optional[str] = None,
    external_axes: bool = False,
) -> Union[None, OpenBBFigure]:
    """Plots repo summary [Source: https://api.github.com].

    Parameters
    ----------
    repo : str
        Repository to display star history. Format: org/repo, e.g., openbb-finance/openbbterminal
    export : str
        Export dataframe data to csv,json,xlsx file
    external_axes : bool, optional
        Whether to return the figure object or not, by default False
    """
    df = github_model.get_stars_history(repo)
    if not df.empty:
        fig = OpenBBFigure(xaxis_title="Date", yaxis_title="Stars")
        fig.set_title(f"Star History for {repo}")

        fig.add_scatter(
            x=df["Date"],
            y=df["Stars"],
            mode="lines",
        )

        export_data(
            export,
            os.path.dirname(os.path.abspath(__file__)),
            "sh",
            df,
            sheet_name,
            fig,
        )
        return fig.show(external=external_axes)

    return None


@log_start_end(log=logger)
def display_top_repos(
    sortby: str,
    categories: str = "",
    limit: int = 10,
    export: str = "",
    sheet_name: Optional[str] = None,
    external_axes: bool = False,
) -> Union[None, OpenBBFigure]:
    """Plots repo summary [Source: https://api.github.com].

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
    external_axes : bool, optional
        Whether to return the figure object or not, by default False
    """
    df = github_model.get_top_repos(categories=categories, sortby=sortby, limit=limit)
    if not df.empty:
        fig = OpenBBFigure(
            xaxis_title=sortby.capitalize(), yaxis_title="Repository Full Name"
        )

        fig.add_bar(
            x=df["stargazers_count" if sortby == "stars" else "forks_count"],
            y=df["full_name"],
            orientation="h",
        )

        category_substr = "ies" if "," in categories else "y"
        category_str = f"categor{category_substr} {categories} " if categories else ""
        fig.set_title(f"Top repos {category_str}sorted by {sortby}")

        export_data(
            export,
            os.path.dirname(os.path.abspath(__file__)),
            "tr",
            df,
            sheet_name,
            fig,
        )
        return fig.show(external=external_axes)

    return None


@log_start_end(log=logger)
def display_repo_summary(
    repo: str, export: str = "", sheet_name: Optional[str] = None
) -> None:
    """Prints table showing repo summary [Source: https://api.github.com].

    Parameters
    ----------
    repo : str
        Repository to display summary. Format: org/repo, e.g., openbb-finance/openbbterminal
    export : str
        Export dataframe data to csv,json,xlsx file
    """
    data = github_model.get_repo_summary(repo)
    if not data.empty:
        print_rich_table(
            data,
            headers=list(data.columns),
            show_index=False,
            title="Repo summary",
            export=bool(export),
        )

        export_data(
            export,
            os.path.dirname(os.path.abspath(__file__)),
            "rs",
            data,
            sheet_name,
        )
