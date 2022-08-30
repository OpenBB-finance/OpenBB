""" News View """
__docformat__ = "numpy"

import os
import logging

from datetime import datetime, timedelta
import pandas as pd

from openbb_terminal.decorators import check_api_key
from openbb_terminal.common import newsapi_model
from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import export_data
from openbb_terminal.rich_config import console

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
@check_api_key(["API_NEWS_TOKEN"])
def display_news(
    query: str,
    start_date: str = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d"),
    limit: int = 3,
    show_newest: bool = True,
    sources: str = "",
    export: str = "",
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
    export : str
        Export dataframe data to csv,json,xlsx file
    """
    articles = newsapi_model.get_news(query, start_date, show_newest, sources)

    if articles:
        for idx, article in enumerate(articles):

            publishedat = article["publishedAt"].replace("T", " ").replace("Z", "")
            title = article["title"]

            console.print(f"> {publishedat} - {title}")
            console.print(article["url"])

            # The description section doesn't exist when this is invoked from UK
            if "description" in article:
                console.print(article["description"])

            console.print()

            if idx >= limit - 1:
                console.print()
                break

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        f"news_{query}_{'_'.join(sources)}",
        pd.DataFrame(articles),
    )
