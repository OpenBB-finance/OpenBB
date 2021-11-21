"""Cryptopanic model"""
__docformat__ = "numpy"

import time
import math
import textwrap
from typing import Optional, Any
import pandas as pd
import requests


import gamestonk_terminal.config_terminal as cfg


class ApiKeyException(Exception):
    """Api Key Exception object"""

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message

    def __str__(self) -> str:
        return "ApiKeyException: %s" % self.message


def make_request(**kwargs: Any) -> dict:
    """Helper methods for requests [Source: https://cryptopanic.com/developers/api/]

    Parameters
    ----------
    kwargs: Any
        Keyword arguments with parameters for GET request to cryptopanic api.
    Returns
    -------
    dict:
        response from api request
    """

    api_key = cfg.API_CRYPTO_PANIC_KEY
    crypto_panic_url = "https://cryptopanic.com/api/v1"

    post_kind = kwargs.get("post_kind")
    filter_ = kwargs.get("filter_")
    region = kwargs.get("region")

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

    if region and region in ["en", "de", "es", "fr", "nl", "it", "pt", "ru"]:
        url += f"&regions={region}"

    response = requests.get(url)

    if not 200 <= response.status_code < 300:
        raise ApiKeyException("Invalid Authentication: %s" % response.text)

    try:
        return response.json()
    except Exception as e:
        raise ValueError("Invalid Response: %s" % response.text) from e


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


def get_news(
    limit: int = 60,
    post_kind: str = "news",
    filter_: Optional[str] = None,
    region: str = "en",
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
        Filter news by regions. Available regions are: en (English), de (Deutsch), nl (Dutch), es (Español),
        fr (Français), it (Italiano), pt (Português), ru (Русский)

    Returns
    -------
    pd.DataFrame
        DataFrame with recent news from different sources filtered by provided parameters.
    """

    if post_kind not in ["news", "media"]:
        post_kind = "news"

    results = []

    response = make_request(post_kind=post_kind, filter_=filter_, region=region)

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
            res = requests.get(next_page).json()
            for post in res["results"]:
                results.append(_parse_post(post))
            next_page = res.get("next")
        except Exception as e:
            raise ValueError(
                "Something went wrong while fetching news from API\n"
            ) from e

    try:
        df = pd.DataFrame(results)
        df["title"] = df["title"].apply(
            lambda x: "\n".join(textwrap.wrap(x, width=66)) if isinstance(x, str) else x
        )
        return df
    except Exception as e:
        raise ValueError("Something went wrong with DataFrame creation\n") from e
