""" News View """
__docformat__ = "numpy"

import logging
import os
from typing import Optional

import pandas as pd

from openbb_terminal.common import feedparser_model
from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import export_data, print_rich_table

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def display_news(
    term: str,
    sources: str = "",
    limit: int = 5,
    export: str = "",
    sheet_name: Optional[str] = None,
    sort: str = "published",
):
    """Plots news for a given term and source. [Source: Feedparser]

    Parameters
    ----------
    term : str
        term to search on the news articles
    sources : str
        sources to exclusively show news from
    limit : int
        number of articles to display
    export : str
        Export dataframe data to csv,json,xlsx file
    sort: str
        the column to sort by
    """
    df = feedparser_model.get_news(term, sources, sort, limit)

    if not df.empty:
        # For table - convert from Timestamp to string
        df["Date"] = pd.to_datetime(df["Date"], utc=True)
        df["Date"] = df["Date"].dt.strftime("%Y-%m-%d %H:%M:%S")
        print_rich_table(df, title="News - articles", export=bool(export))

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        f"news_{'_'.join(term)}_{'_'.join(sources)}",
        df,
        sheet_name,
    )
