"""Cryptopanic view"""
__docformat__ = "numpy"

import logging
import os
from typing import Optional
import pandas as pd

from openbb_terminal.cryptocurrency.overview import cryptopanic_model
from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import export_data, print_rich_table
from openbb_terminal.rich_config import console
from openbb_terminal.decorators import check_api_key
from openbb_terminal.cryptocurrency.dataframe_helpers import prettify_column_names

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
@check_api_key(["API_CRYPTO_PANIC_KEY"])
def display_news(
    post_kind: str = "news",
    region: str = "en",
    filter_: Optional[str] = None,
    source: str = "cp",
    currency: Optional[str] = None,
    top: int = 25,
    descend: bool = False,
    export: str = "",
) -> None:
    """Display recent posts from CryptoPanic news aggregator platform. [Source: https://cryptopanic.com/]

    Parameters
    ----------
    top: int
        number of news to display
    post_kind: str
        Filter by category of news. Available values: news or media.
    filter_: Optional[str]
        Filter by kind of news. One from list: rising|hot|bullish|bearish|important|saved|lol
    region: str
        Filter news by regions. Available regions are: en (English), de (Deutsch), nl (Dutch), es (Español),
        fr (Français), it (Italiano), pt (Português), ru (Русский)
    descend: bool
        Sort in descending order.
    export : str
        Export dataframe data to csv,json,xlsx file
    """

    df = cryptopanic_model.get_news(
        limit=top,
        post_kind=post_kind,
        filter_=filter_,
        region=region,
        currency=currency,
        source=source,
    )

    if not df.empty:
        df = df.sort_values(by="published_at", ascending=descend)
        df["published_at"] = pd.to_datetime(df["published_at"]).dt.date
        df.drop(["negative_votes", "positive_votes", "domain"], axis=1, inplace=True)

        df.columns = prettify_column_names(df.columns)

        print_rich_table(
            df.head(top),
            headers=list(df.columns),
            show_index=False,
            title="Most Recent News",
        )
        console.print("")

        export_data(
            export,
            os.path.dirname(os.path.abspath(__file__)),
            "news",
            df,
        )
