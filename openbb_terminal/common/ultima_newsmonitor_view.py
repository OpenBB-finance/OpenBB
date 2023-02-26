""" News View """
__docformat__ = "numpy"

import logging
import os
from typing import Optional

from openbb_terminal.common import ultima_newsmonitor_model
from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import export_data
from openbb_terminal.rich_config import console

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def display_news(
    term: str,
    sources: str = "",
    limit: int = 5,
    export: str = "",
    sheet_name: Optional[str] = None,
    sort: str = "relevancyScore",
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
    articles = ultima_newsmonitor_model.get_news(term, sources, sort)

    console.print()
    for _, row in articles.head(limit).iterrows():
        console.print(f"> {row['articlePublishedDate']} - {row['articleHeadline']} -> {row['relevancyScore']}")
        console.print(row["articleURL"] + "\n")
    console.print()

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        f"news_{'_'.join(term)}_{'_'.join(sources)}",
        articles,
        sheet_name,
    )
