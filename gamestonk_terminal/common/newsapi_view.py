""" News View """
__docformat__ = "numpy"

import logging

from gamestonk_terminal.common import newsapi_model
from gamestonk_terminal.decorators import log_start_end
from gamestonk_terminal.rich_config import console

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def display_news(
    term: str,
    s_from: str,
    num: int = 5,
    show_newest: bool = True,
    sources: str = "",
):
    """Display news for a given term. [Source: NewsAPI]

    Parameters
    ----------
    term : str
        term to search on the news articles
    s_from: str
        date to start searching articles from formatted YYYY-MM-DD
    num : int
        number of articles to display
    show_newest: bool
        flag to show newest articles first
    sources: str
        sources to exclusively show news from
    """
    articles = newsapi_model.get_news(term, s_from, show_newest, sources)

    if articles:
        for idx, article in enumerate(articles):
            console.print(
                article["publishedAt"].replace("T", " ").replace("Z", ""),
                " ",
                article["title"],
            )
            # Unnecessary to use name of the source because contained in link article["source"]["name"]
            console.print(article["url"], "\n")

            if idx >= num - 1:
                break
