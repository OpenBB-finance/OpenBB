""" News View """
__docformat__ = "numpy"

import logging
import os
from typing import Optional

from openbb_terminal.common import newsapi_model
from openbb_terminal.decorators import check_api_key, log_start_end
from openbb_terminal.helper_funcs import export_data, print_rich_table

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
@check_api_key(["API_NEWS_TOKEN"])
def display_news(
    query: str,
    limit: int = 10,
    start_date: Optional[str] = None,
    show_newest: bool = True,
    sources: str = "",
    export: str = "",
    sheet_name: Optional[str] = None,
) -> None:
    """Prints table showing news for a given term. [Source: NewsAPI]

    Parameters
    ----------
    query : str
        term to search on the news articles
    start_date: Optional[str]
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
    df = newsapi_model.get_news(query, limit, start_date, show_newest, sources)
    if not df.empty:
        print_rich_table(df, title="News - articles", export=bool(export))

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        f"news_{query}_{'_'.join(sources)}",
        df,
        sheet_name,
    )
