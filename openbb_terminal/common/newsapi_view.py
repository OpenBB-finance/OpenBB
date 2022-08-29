""" News View """
__docformat__ = "numpy"

import logging

from datetime import datetime, timedelta

from openbb_terminal.decorators import check_api_key
from openbb_terminal.common import newsapi_model
from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import print_rich_table

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
@check_api_key(["API_NEWS_TOKEN"])
def display_news(
    query: str,
    limit: int = 3,
    start_date: str = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d"),
    show_newest: bool = True,
    sources: str = "",
) -> None:
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
    tables = newsapi_model.get_news(query, limit, start_date, show_newest, sources)
    if tables:
        for table in tables:
            print_rich_table(table[0], title=table[1]["title"])
