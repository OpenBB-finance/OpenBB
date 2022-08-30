""" News Model """
__docformat__ = "numpy"

import logging

from datetime import datetime, timedelta
from typing import List, Any
import requests
import pandas as pd
from openbb_terminal import config_terminal as cfg
from openbb_terminal.decorators import log_start_end
from openbb_terminal.rich_config import console

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def get_news(
    query: str,
    limit: int = 10,
    start_date: str = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d"),
    show_newest: bool = True,
    sources: str = "",
) -> List[Any]:
    """Get news for a given term. [Source: NewsAPI]

    Parameters
    ----------
    query : str
        term to search on the news articles
    start_date: str
        date to start searching articles from formatted YYYY-MM-DD
    show_newest: bool
        flag to show newest articles first
    sources: str
        sources to exclusively show news from

    Returns
    ----------
    tables : List[Any]
        List of tuples containing news df in first index and dict containing title of news df
    """
    link = (
        f"https://newsapi.org/v2/everything?q={query}&from={start_date}&sortBy=publishedAt&language=en"
        f"&apiKey={cfg.API_NEWS_TOKEN}"
    )

    if sources:
        link += f"&domain={sources}"

    response = requests.get(link)

    articles = {}

    # Check that the API response was successful
    if response.status_code == 200:
        response_json = response.json()
        console.print(
            f"{response_json['totalResults']} news articles for {query} were found since {start_date}\n"
        )

        if show_newest:
            articles = response_json["articles"]

        else:
            articles = response_json["articles"][::-1]

    elif response.status_code == 426:
        console.print(f"Error in request: {response.json()['message']}", "\n")

    elif response.status_code == 401:
        console.print("[red]Invalid API Key[/red]\n")

    elif response.status_code == 429:
        console.print("[red]Exceeded number of calls per minute[/red]\n")

    else:
        console.print(f"Error in request: {response.json()['message']}", "\n")

    if articles:
        tables = list()
        for idx, article in enumerate(articles):
            # Unnecessary to use name of the source because contained in link article["source"]["name"]
            data = [
                [article["publishedAt"].replace("T", " ").replace("Z", "")],
                [f"{article['description']}"],
                [article["url"]],
            ]

            table = pd.DataFrame(
                data, index=["published", "content", "link"], columns=["Content"]
            )
            tables.append((table, article))
            if idx >= limit - 1:
                break

    tables.columns = tables.columns.str.title()

    return tables
