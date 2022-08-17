""" News View """
__docformat__ = "numpy"

import logging

from datetime import datetime, timedelta
import pandas as pd

from openbb_terminal.decorators import check_api_key
from openbb_terminal.common import newsapi_model
from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import print_rich_table

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
@check_api_key(["API_NEWS_TOKEN"])
def display_news(
    query: str,
    start_date: str = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d"),
    limit: int = 3,
    show_newest: bool = True,
    sources: str = "",
):
    """Display news for a given term. [Source: NewsAPI]

    Parameters
    ----------
    query : str
        term to search on the news articles
    start_date: str
        date to start searching articles from formatted YYYY-MM-DD
    limit : int
        number of articles to display
    show_newest: bool
        flag to show newest articles first
    sources: str
        sources to exclusively show news from
    """
    articles = newsapi_model.get_news(query, start_date, show_newest, sources)

    if articles:
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
            print_rich_table(table, title=article["title"])

            if idx >= limit - 1:
                break
