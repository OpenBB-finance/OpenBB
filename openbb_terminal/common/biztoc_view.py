""" BizToc View """
__docformat__ = "numpy"

import logging
import os
from typing import Optional

from openbb_terminal.common import biztoc_model
from openbb_terminal.decorators import check_api_key, log_start_end
from openbb_terminal.helper_funcs import export_data, print_rich_table

logger = logging.getLogger(__name__)


@check_api_key(["API_BIZTOC_TOKEN"])
@log_start_end(log=logger)
def display_news(
    term: str = "",
    tag: str = "",
    source: str = "",
    limit: int = 100,
    export: str = "",
    sheet_name: Optional[str] = None,
    sort: str = "created",
):
    """Plots news for a given term and source. [Source: Feedparser]

    Parameters
    ----------
    term : str
        term to search on the news articles
    tag : str
        display news articles for an individual tag
    source : str
        source to exclusively show news from
    limit : int
        number of articles to display
    export : str
        Export dataframe data to csv,json,xlsx file
    sort: str
        the column to sort by
    """
    df = biztoc_model.get_news(term, tag, source, sort, limit)

    if not df.empty:
        print_rich_table(df, title="BizToc News - articles", export=bool(export))

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        f"news_biztoc_{'_'.join(term)}_{'_'.join(source)}",
        df,
        sheet_name,
    )


@check_api_key(["API_BIZTOC_TOKEN"])
def display_sources(
    export: str = "",
    sheet_name: Optional[str] = None,
):
    """Plots available sources for news."""

    df = biztoc_model.get_sources()

    if not df.empty:
        print_rich_table(df, title="BizToc News - sources", export=bool(export))

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "news_biztoc_sources",
        df,
        sheet_name,
    )


@check_api_key(["API_BIZTOC_TOKEN"])
def display_tags(
    export: str = "",
    sheet_name: Optional[str] = None,
):
    """Plots currently trending tags."""

    df = biztoc_model.get_tags()

    if not df.empty:
        print_rich_table(
            df, title="BizToc News - list of trending tags", export=bool(export)
        )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "news_biztoc_tags",
        df,
        sheet_name,
    )
