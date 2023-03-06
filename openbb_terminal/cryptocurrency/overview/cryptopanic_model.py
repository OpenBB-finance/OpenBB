"""Cryptopanic model"""
__docformat__ = "numpy"

import logging
import math
import textwrap
import time
from typing import Any, Optional

import pandas as pd

from openbb_terminal.core.session.current_user import get_current_user
from openbb_terminal.cryptocurrency.cryptocurrency_helpers import prepare_all_coins_df
from openbb_terminal.decorators import check_api_key, log_start_end
from openbb_terminal.helper_funcs import request
from openbb_terminal.parent_classes import CRYPTO_SOURCES
from openbb_terminal.rich_config import console

logger = logging.getLogger(__name__)

CATEGORIES = ["news", "media"]

SORT_FILTERS = [
    "published_at",
    "domain",
    "title",
    "negative_votes",
    "positive_votes",
]

FILTERS = [
    "rising",
    "hot",
    "bullish",
    "bearish",
    "important",
    "saved",
    "lol",
]

REGIONS = ["en", "de", "es", "fr", "nl", "it", "pt", "ru"]


class ApiKeyException(Exception):
    """Api Key Exception object"""

    @log_start_end(log=logger)
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message

    @log_start_end(log=logger)
    def __str__(self) -> str:
        return f"ApiKeyException: {self.message}"


@log_start_end(log=logger)
@check_api_key(["API_CRYPTO_PANIC_KEY"])
def make_request(**kwargs: Any) -> Optional[dict]:
    """Helper methods for requests [Source: https://cryptopanic.com/developers/api/]

    Parameters
    ----------
    kwargs: Any
        Keyword arguments with parameters for GET request to cryptopanic api.

    Returns
    -------
    Optional[dict]
        response from api request
    """

    api_key = get_current_user().credentials.API_CRYPTO_PANIC_KEY
    crypto_panic_url = "https://cryptopanic.com/api/v1"

    post_kind = kwargs.get("post_kind")
    filter_ = kwargs.get("filter_")
    region = kwargs.get("region")
    currency = kwargs.get("currency")
    source = kwargs.get("source")

    if post_kind not in ["news", "media", "all"]:
        post_kind = "all"

    url = f"{crypto_panic_url}/posts/?auth_token={api_key}" + f"&kind={post_kind}"

    if filter_ and filter_ in [
        "rising",
        "hot",
        "bullish",
        "bearish",
        "important",
        "saved",
        "lol",
    ]:
        url += f"&filter={filter_}"

    if region and region in REGIONS:
        url += f"&regions={region}"

    if currency and source:
        source_full = CRYPTO_SOURCES[source]
        df_mapp = prepare_all_coins_df()

        try:
            mapped_coin = df_mapp.loc[df_mapp[source_full] == currency][
                "Symbol"
            ].values[0]
            url += f"&currency={mapped_coin.upper()}"
        except IndexError:
            console.print(f"Cannot find news for {currency}.\n")
            return {}

    response = request(url)
    response_json = response.json()
    result = None

    if response.status_code == 200:
        result = response_json
    else:
        if "Token not found" in response_json["info"]:
            console.print("[red]Invalid API Key[/red]\n")
        else:
            console.print(response_json["info"])

        logger.warning("Invalid authentication: %s", response.text)

    return result


@log_start_end(log=logger)
def _parse_post(post: dict) -> dict:
    """Helper method - parse news response object to dictionary with target structure.
    [Source: https://cryptopanic.com/]

    Parameters
    ----------
    post: dict
        Response object from cryptopanic api.

    Returns
    -------
    dict
        Parsed dictionary with target data structure.

    """
    return {
        "published_at": post.get("published_at"),
        "domain": post.get("domain"),
        "title": post.get("title"),
        "negative_votes": post["votes"].get("negative"),
        "positive_votes": post["votes"].get("positive"),
        "link": post["url"],
    }


@log_start_end(log=logger)
def get_news(
    limit: int = 60,
    post_kind: str = "news",
    filter_: Optional[str] = None,
    region: str = "en",
    source: Optional[str] = None,
    symbol: Optional[str] = None,
    sortby: str = "published_at",
    ascend: bool = True,
) -> pd.DataFrame:
    """Get recent posts from CryptoPanic news aggregator platform. [Source: https://cryptopanic.com/]

    Parameters
    ----------
    limit: int
        number of news to fetch
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
        Sort in ascend order.

    Returns
    -------
    pd.DataFrame
        DataFrame with recent news from different sources filtered by provided parameters.
    """

    if post_kind not in CATEGORIES:
        post_kind = "news"

    results = []

    kwargs = {}
    if source:
        kwargs["source"] = source
    response = make_request(
        post_kind=post_kind, filter_=filter_, region=region, currency=symbol, **kwargs
    )

    if response:
        data, next_page, _ = (
            response["results"],
            response.get("next"),
            response.get("count"),
        )

        for post in data:
            results.append(_parse_post(post))

        number_of_pages = math.ceil(limit // 20)
        counter = 0
        while counter < number_of_pages and next_page:
            counter += 1
            try:
                time.sleep(0.2)
                res = request(next_page).json()
                for post in res["results"]:
                    results.append(_parse_post(post))
                next_page = res.get("next")
            except Exception as e:  # noqa: F841
                logger.exception(str(e))
                console.print(
                    "[red]Something went wrong while fetching news from API[/red]\n"
                )
                return pd.DataFrame()

        try:
            df = pd.DataFrame(results)
            df["title"] = df["title"].apply(
                lambda x: "\n".join(textwrap.wrap(x, width=66))
                if isinstance(x, str)
                else x
            )
            df["published_at"] = pd.to_datetime(df["published_at"]).dt.date
            df = df.sort_values(by=sortby, ascending=ascend)
            return df
        except Exception as e:  # noqa: F841
            logger.exception(str(e))
            console.print("[red]Something went wrong with DataFrame creation[/red]\n")
            return pd.DataFrame()
    return pd.DataFrame()
