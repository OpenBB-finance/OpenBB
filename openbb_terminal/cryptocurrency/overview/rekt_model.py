"""Rekt Model"""
import logging
from typing import List, Union

import pandas as pd
import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter, RetryError
from urllib3.util.retry import Retry

from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import get_user_agent
from openbb_terminal.rich_config import console

logger = logging.getLogger(__name__)

HACKS_COLUMNS = ["Platform", "Date", "Amount [$]", "Audit", "Slug", "URL"]


@log_start_end(log=logger)
def _retry_session(
    url: str, retries: int = 3, backoff_factor: float = 1.0
) -> requests.Session:
    """Helper methods that retries to make request


    Parameters
    ----------
    url: str
        Url to mount a session
    retries: int
        How many retries
    backoff_factor: float
        Backoff schema - time periods between retry

    Returns
    -------
    requests.Session
        Mounted session
    """

    session = requests.Session()
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        status_forcelist=[500, 502, 503, 504],
        backoff_factor=backoff_factor,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount(url, adapter)
    return session


@log_start_end(log=logger)
def _make_request(url: str) -> Union[BeautifulSoup, None]:
    """Helper method to scrap

    Parameters
    ----------
    url : str
        url to scrape

    Returns
    -------
    Union[BeautifulSoup, None]
        BeautifulSoup object or None
    """
    headers = {"User-Agent": get_user_agent()}
    session = _retry_session("https://www.coingecko.com")
    try:
        req = session.get(url, headers=headers)
    except Exception as error:
        logger.exception(str(error))
        console.print(error)
        raise RetryError(
            "Connection error. Couldn't connect to CoinGecko and scrape the data. "
            "Please visit CoinGecko site, and check if it's not under maintenance"
        ) from error

    if req.status_code == 404:
        return None

    if req.status_code >= 400:
        raise Exception(
            f"Couldn't connect to {url}. Status code: {req.status_code}. Reason: {req.reason}"
        )

    return BeautifulSoup(req.text, features="lxml")


@log_start_end(log=logger)
def get_crypto_hacks(sortby: str = "Platform", ascend: bool = False) -> pd.DataFrame:
    """Get major crypto-related hacks
    [Source: https://rekt.news]

    Parameters
    ----------
    sortby: str
        Key by which to sort data {Platform,Date,Amount [$],Audit,Slug,URL}
    ascend: bool
        Flag to sort data ascending

    Returns
    -------
    pd.DataFrame
        Hacks with columns {Platform,Date,Amount [$],Audited,Slug,URL}
    """
    soup = _make_request("https://rekt.news/leaderboard")
    if soup:
        rekt_list = soup.find("ol", {"class": "leaderboard-content"}).find_all("li")
        df = pd.DataFrame(columns=HACKS_COLUMNS)
        for item in rekt_list:
            a = item.find("a", href=True)
            audit = item.find("span", {"class": "leaderboard-audit"}).text
            details = item.find("div", {"class": "leaderboard-row-details"}).text.split(
                "|"
            )
            url = a["href"]
            title = a.text
            amount = int(details[0][1:].replace(",", ""))
            date = details[1].replace(" ", "")
            df.loc[len(df.index)] = [
                title,
                date,
                amount,
                audit,
                url.replace("/", ""),
                f"https://rekt.news{url}",
            ]
        df["Date"] = pd.to_datetime(df["Date"])
        if sortby in HACKS_COLUMNS:
            df = df.sort_values(by=sortby, ascending=ascend)
        return df
    return pd.DataFrame()


@log_start_end(log=logger)
def get_crypto_hack(slug: str) -> Union[str, None]:
    """Get crypto hack
    [Source: https://rekt.news]

    Parameters
    ----------
    slug: str
        slug of crypto hack

    Returns
    -------
    Union[str, None]
        Crypto hack
    """
    url = f"https://rekt.news/{slug}"
    soup = _make_request(url)
    if not soup:
        console.print(f'Slug "{slug}" not found\n')
        return None
    title = soup.find("h1", {"class": "post-title"}).text
    date = soup.find("time").text
    content = (
        soup.find("section", {"class": "post-content"})
        .get_text("\n")
        .replace("\r\n,", ", ")
        .replace("\n,", ", ")
        .replace("\r\n.", ".\n\t")
        .replace("\n.", ".\n\t")
        .replace("\r\n ", " ")
        .replace("\n ", " ")
    ).split("""SUBSCRIBE""")[0]
    final_str = f"""
    {title}
    {date}

    {content}

    Detailed history in {url}
    """
    return final_str


@log_start_end(log=logger)
def get_crypto_hack_slugs() -> List[str]:
    """Get all crypto hack slugs
    [Source: https://rekt.news]

    Returns
    -------
    List[str]
        List with slugs
    """
    soup = _make_request("https://rekt.news/leaderboard")
    href_list = []
    if soup:
        rekt_list = soup.find("ol", {"class": "leaderboard-content"}).find_all("li")
        for item in rekt_list:
            a = item.find("a", href=True)["href"].replace("/", "")
            href_list.append(a)
        return href_list
    return href_list
