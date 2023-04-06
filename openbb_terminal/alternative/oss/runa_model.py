"""Runa Model"""
import logging
from typing import Union

import pandas as pd
import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter, RetryError
from urllib3.util.retry import Retry

from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import get_user_agent, request
from openbb_terminal.rich_config import console

logger = logging.getLogger(__name__)

SORT_COLUMNS = [
    "GitHub",
    "Company",
    "Country",
    "City",
    "Founded",
    "Raised [$M]",
    "Stars",
    "Forks",
    "Stars AGR [%]",
    "Forks AGR [%]",
]


@log_start_end(log=logger)
def _retry_session(
    url: str, retries: int = 3, backoff_factor: float = 1.0
) -> requests.Session:
    """Helper methods that retries to make request.


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
    """Helper method to scrap.

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
    session = _retry_session("https://runacap.com/")
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
def get_startups() -> pd.DataFrame:
    """Get startups from ROSS index [Source: https://runacap.com/].

    Returns
    -------
    pd.DataFrame
        list of startups
    """
    response = request("https://runacap.com/ross-index/annual-2022")
    soup = BeautifulSoup(response.content, "html.parser")
    startups = []
    if soup:
        table = soup.find("table", {"id": "table_1"})
        if table:
            rows = table.find_all("tr")
            for row in rows:
                td = row.find_all("td")
                startup = [tr.text for tr in td]
                if len(startup) > 0:
                    startups.append(startup)
            df = pd.DataFrame(
                startups,
                columns=[
                    "GitHub",
                    "Company",
                    "Country",
                    "City",
                    "Founded",
                    "Raised [$M]",
                    "REPO",
                    "Language",
                    "Stars",
                    "Forks",
                    "Stars AGR [%]",
                    "Forks AGR [%]",
                    "SG",
                    "FG",
                ],
            )
            df.drop("REPO", inplace=True, axis=1)
            df["SG"] = pd.to_numeric(df["SG"], errors="coerce")
            df["Stars"] = pd.to_numeric(
                df["Stars"].str.replace(",", ""), errors="coerce"
            )
            df["FG"] = pd.to_numeric(df["FG"], errors="coerce")
            df["Forks"] = pd.to_numeric(
                df["Forks"].str.replace(",", ""), errors="coerce"
            )
            df["Raised [$M]"] = pd.to_numeric(df["Raised [$M]"], errors="coerce")
            df["Stars AGR [%]"] = pd.to_numeric(
                df["Stars AGR [%]"].str.replace(",", ""), errors="coerce"
            )
            df["Forks AGR [%]"] = pd.to_numeric(
                df["Forks AGR [%]"].str.replace(",", ""), errors="coerce"
            )
            return df
    return pd.DataFrame()
