"""GitHub Model"""
__docformat__ = "numpy"
# pylint: disable=C0201,W1401

import logging
import math
from datetime import datetime
from typing import Any, Dict, Optional

import pandas as pd

from openbb_terminal.core.session.current_user import get_current_user
from openbb_terminal.decorators import check_api_key, log_start_end
from openbb_terminal.helper_funcs import get_user_agent, request
from openbb_terminal.rich_config import console

logger = logging.getLogger(__name__)


@check_api_key(["API_GITHUB_KEY"])
def get_github_data(url: str, **kwargs) -> Optional[Dict[str, Any]]:
    """Get repository stats.

    Parameters
    ----------
    url: str
        github api endpoint
    params: dict
        params to pass to api endpoint

    Returns
    -------
    Dict[str, Any]
        Dictionary with data
    """
    res = request(
        url,
        headers={
            "Authorization": f"token {get_current_user().credentials.API_GITHUB_KEY}",
            "User-Agent": get_user_agent(),
            "Accept": "application/vnd.github.v3.star+json",
        },
        **kwargs,
    )
    if res.status_code == 200:
        return res.json()
    if res.status_code in (401, 403):
        console.print("[red]Rate limit reached, please provide a GitHub API key.[/red]")
    elif res.status_code == 404:
        console.print("[red]Repo not found.[/red]")
    else:
        console.print(f"[red]Error occurred {res.json()}[/red]")
    return None


def search_repos(
    sortby: str = "stars", page: int = 1, categories: str = ""
) -> pd.DataFrame:
    """Get repos sorted by stars or forks. Can be filtered by categories.

    Parameters
    ----------
    sortby : str
        Sort repos by {stars, forks}
    categories : str
        Check for repo categories. If more than one separate with a comma: e.g., finance,investment. Default: None
    page : int
        Page number to get repos

    Returns
    -------
    pd.DataFrame
        Dataframe with repos
    """
    params: Dict[str, Any] = {"page": page}
    if categories:
        params["sort"] = sortby
        params["q"] = categories.replace(",", "+")
    else:
        params["q"] = f"{sortby}:>1"
    data = get_github_data("https://api.github.com/search/repositories", params=params)
    if data and "items" in data:
        return pd.DataFrame(data["items"])
    return pd.DataFrame()


@log_start_end(log=logger)
def get_stars_history(repo: str) -> pd.DataFrame:
    """Get repository star history.

    Parameters
    ----------
    repo : str
        Repo to search for Format: org/repo, e.g., openbb-finance/openbbterminal

    Returns
    -------
    pd.DataFrame
        Dataframe with star history - Columns: Date, Stars
    """
    data = get_github_data(f"https://api.github.com/repos/{repo}")
    if data and "stargazers_count" in data:
        stars_number = data["stargazers_count"]
        stars: Dict[str, int] = {}
        pages = math.ceil(stars_number / 100)
        for page in range(0, pages):
            data = get_github_data(
                f"https://api.github.com/repos/{repo}/stargazers",
                params={"per_page": 100, "page": page},
            )
            if data:
                for star in data:
                    day = star["starred_at"].split("T")[0]
                    if day in stars:
                        stars[day] += 1
                    else:
                        stars[day] = 1
        sorted_keys = sorted(stars.keys())
        for i in range(1, len(sorted_keys)):
            stars[sorted_keys[i]] += stars[sorted_keys[i - 1]]
        df = pd.DataFrame(
            {
                "Date": [datetime.strptime(date, "%Y-%m-%d").date() for date in stars],
                "Stars": stars.values(),
            }
        )
        df.set_index("Date")
        return df
    return pd.DataFrame()


@log_start_end(log=logger)
def get_top_repos(sortby: str, limit: int = 50, categories: str = "") -> pd.DataFrame:
    """Get repos sorted by stars or forks. Can be filtered by categories.

    Parameters
    ----------
    sortby : str
        Sort repos by {stars, forks}
    categories : str
        Check for repo categories. If more than one separate with a comma: e.g., finance,investment. Default: None
    limit : int
        Number of repos to search for

    Returns
    -------
    pd.DataFrame
        Dataframe with repos
    """
    initial_top = limit
    df = pd.DataFrame(
        columns=[
            "full_name",
            "open_issues",
            "stargazers_count",
            "forks_count",
            "language",
            "created_at",
            "updated_at",
            "html_url",
        ]
    )
    if limit <= 100:
        df2 = search_repos(sortby=sortby, page=1, categories=categories)
        df = pd.concat([df, df2], ignore_index=True)
    else:
        p = 2
        while limit > 0:
            df2 = search_repos(sortby=sortby, page=p, categories=categories)
            df = pd.concat([df, df2], ignore_index=True)
            limit -= 100
            p += 1
    return df.head(initial_top)


@log_start_end(log=logger)
def get_repo_summary(repo: str) -> pd.DataFrame:
    """Get repository summary.

    Parameters
    ----------
    repo : str
        Repo to search for Format: org/repo, e.g., openbb-finance/openbbterminal

    Returns
    -------
    pd.DataFrame
        Dataframe with repo summary - Columns: Metric, Value
    """
    data = get_github_data(f"https://api.github.com/repos/{repo}")
    if not data:
        return pd.DataFrame()
    release_data = get_github_data(f"https://api.github.com/repos/{repo}/releases")
    if not release_data:
        return pd.DataFrame()
    total_release_downloads: Any = "N/A"
    if len(release_data) > 0:
        total_release_downloads = 0
        for asset in release_data[0]["assets"]:
            total_release_downloads += asset["download_count"]
    obj: Dict[str, Any] = {
        "Metric": [
            "Name",
            "Owner",
            "Creation Date",
            "Last Update",
            "Topics",
            "Stars",
            "Forks",
            "Open Issues",
            "Language",
            "License",
            "Releases",
            "Last Release Downloads",
        ],
        "Value": [
            data["name"],
            data["owner"]["login"],
            data["created_at"].split("T")[0],
            data["updated_at"].split("T")[0],
            ", ".join(data["topics"]),
            data["stargazers_count"],
            data["forks"],
            data["open_issues"],
            data["language"],
            data["license"]["name"],
            len(release_data),
            total_release_downloads,
        ],
    }
    return pd.DataFrame(obj)
