""" News Model """
__docformat__ = "numpy"

import logging

from typing import Dict
import requests
from gamestonk_terminal import config_terminal as cfg
from gamestonk_terminal.decorators import log_start_end
from gamestonk_terminal.rich_config import console

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def get_news(
    term: str,
    s_from: str,
    show_newest: bool = True,
    sources: str = "",
) -> Dict:
    """Get news for a given term. [Source: NewsAPI]

    Parameters
    ----------
    term : str
        term to search on the news articles
    s_from: str
        date to start searching articles from formatted YYYY-MM-DD
    show_newest: bool
        flag to show newest articles first
    sources: str
        sources to exclusively show news from

    Returns
    ----------
    articles : dict
        term to search on the news articles
    """
    link = (
        f"https://newsapi.org/v2/everything?q={term}&from={s_from}&sortBy=publishedAt&language=en"
        f"&apiKey={cfg.API_NEWS_TOKEN}"
    )

    if sources:
        link += f"&domain={sources}"

    response = requests.get(link)

    # Check that the API response was successful
    if response.status_code == 426:
        console.print(f"Error in request: {response.json()['message']}", "\n")
        return {}

    if response.status_code != 200:
        console.print(
            f"Error in request {response.status_code}. Check News API token", "\n"
        )
        return {}

    console.print(
        f"{response.json()['totalResults']} news articles for {term} were found since {s_from}\n"
    )

    if show_newest:
        articles = response.json()["articles"]

    else:
        articles = response.json()["articles"][::-1]

    return articles
