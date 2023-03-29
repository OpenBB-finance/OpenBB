"""Cryptopanic view"""
__docformat__ = "numpy"

import logging
import os
from typing import Optional

from openbb_terminal.cryptocurrency.overview import cryptopanic_model
from openbb_terminal.decorators import check_api_key, log_start_end
from openbb_terminal.helper_funcs import export_data, print_rich_table

logger = logging.getLogger(__name__)

# pylint: disable=too-many-arguments


@log_start_end(log=logger)
@check_api_key(["API_CRYPTO_PANIC_KEY"])
def display_news(
    post_kind: str = "news",
    region: str = "en",
    filter_: Optional[str] = None,
    limit: int = 25,
    sortby: str = "published_at",
    ascend: bool = False,
    links: bool = False,
    export: str = "",
    sheet_name: Optional[str] = None,
) -> None:
    """Display recent posts from CryptoPanic news aggregator platform.
    [Source: https://cryptopanic.com/]

    Parameters
    ----------
    limit: int
        number of news to display
    post_kind: str
        Filter by category of news. Available values: news or media.
    filter_: Optional[str]
        Filter by kind of news. One from list: rising|hot|bullish|bearish|important|saved|lol
    region: str
        Filter news by regions. Available regions are: en (English), de (Deutsch), nl (Dutch),
        es (Español), fr (Français), it (Italiano), pt (Português), ru (Русский)
    sortby: str
        Key to sort by.
    ascend: bool
        Sort in ascending order.
    links: bool
        Show urls for news
    export : str
        Export dataframe data to csv,json,xlsx file
    """

    df = cryptopanic_model.get_news(
        limit=limit,
        post_kind=post_kind,
        filter_=filter_,
        region=region,
        sortby=sortby,
        ascend=ascend,
    )
    if not df.empty:
        if not links:
            df.drop("link", axis=1, inplace=True)
        else:
            df = df[["title", "link"]]

        print_rich_table(
            df,
            headers=list(df.columns),
            show_index=False,
            title="Recent CryptoPanic Posts",
            export=bool(export),
            limit=limit,
        )

        export_data(
            export,
            os.path.dirname(os.path.abspath(__file__)),
            "news",
            df,
            sheet_name,
        )
