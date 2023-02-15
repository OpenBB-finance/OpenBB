""" News Model """
__docformat__ = "numpy"

import logging
from datetime import datetime, timedelta
from typing import Any, List, Optional, Tuple

import pandas as pd

from openbb_terminal import config_terminal as cfg
from openbb_terminal.decorators import check_api_key, log_start_end
from openbb_terminal.helper_funcs import request
from openbb_terminal.rich_config import console

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
@check_api_key(["API_NEWS_TOKEN"])
def get_news(
    query: str,
    limit: int = 10,
    start_date: Optional[str] = None,
    show_newest: bool = True,
    sources: str = "",
) -> List[Tuple[pd.DataFrame, Any]]:
    """Get news for a given term. [Source: NewsAPI]

    Parameters
    ----------
    query : str
        term to search on the news articles
    start_date: Optional[str]
        date to start searching articles from formatted YYYY-MM-DD
    show_newest: bool
        flag to show newest articles first
    sources: str
        sources to exclusively show news from (comma separated)

    Returns
    -------
    tables : List[Tuple[pd.DataFrame, dict]]
        List of tuples containing news df in first index,
        dict containing title of news df.
    """

    if start_date is None:
        start_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")

    link = (
        f"https://newsapi.org/v2/everything?q={query}&from={start_date}&sortBy=publishedAt"
        "&language=en"
    )

    if sources:
        if "," in sources:
            sources = ".com,".join(sources.split(","))
        link += f"&domains={sources}.com"

    link += f"&apiKey={cfg.API_NEWS_TOKEN}"

    response = request(link)

    articles = {}

    # Check that the API response was successful
    if response.status_code == 200:
        response_json = response.json()
        console.print(
            f"{response_json['totalResults']} news articles for",
            f" {query} were found since {start_date}\n",
        )

        articles = (
            response_json["articles"]
            if show_newest
            else response_json["articles"][::-1]
        )

    elif response.status_code == 426:
        console.print(f"Error in request: {response.json()['message']}", "\n")

    elif response.status_code == 401:
        console.print("[red]Invalid API Key[/red]\n")

    elif response.status_code == 429:
        console.print("[red]Exceeded number of calls per minute[/red]\n")

    else:
        console.print(f"Error in request: {response.json()['message']}", "\n")

    tables: List[Tuple[pd.DataFrame, dict]] = []
    if articles:
        for idx, article in enumerate(articles):
            # Unnecessary to use source name because contained in link article["source"]["name"]
            if "description" in article:
                data = [
                    [article["publishedAt"].replace("T", " ").replace("Z", "")],
                    [f"{article['description']}"],
                    [article["url"]],
                ]
                table = pd.DataFrame(
                    data, index=["published", "content", "link"], columns=["Content"]
                )

            else:
                data = [
                    [article["publishedAt"].replace("T", " ").replace("Z", "")],
                    [article["url"]],
                ]

                table = pd.DataFrame(
                    data, index=["published", "link"], columns=["Content"]
                )

            table.columns = table.columns.str.title()
            tables.append((table, article))
            if idx >= limit - 1:
                break

    return tables
