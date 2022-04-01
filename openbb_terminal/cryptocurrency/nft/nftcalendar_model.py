""" nftcalendar.io Model """
__docformat__ = "numpy"

import logging

import pandas as pd
import requests
from bs4 import BeautifulSoup

from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import get_user_agent

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def get_nft_drops(url: str) -> pd.DataFrame:
    """Get NFT drops [Source: nftcalendar.io]

    Parameters
    -------
    url : str
        url to get NFT drops from

    Returns
    -------
    pd.DataFrame
        NFT drops
    """
    nft_calendar = BeautifulSoup(
        requests.get(
            url,
            headers={"User-Agent": get_user_agent()},
        ).text,
        "lxml",
    )
    drop_titles = list()
    for droptitle in nft_calendar.find_all("h2", {"class": "text-2xl"}):
        drop_titles.append(droptitle.text.strip())

    drop_descriptions = list()
    for dropdesc in nft_calendar.find_all(
        "div", {"class": "pb-0 md:pb-2 text-normal text-black dark:text-yellow-50"}
    ):
        drop_descriptions.append(dropdesc.text.strip())

    drop_dates = list()
    for dropdate in nft_calendar.find_all(
        "div", {"class": "py-2 text-normal text-black dark:text-yellow-50 md:text-lg"}
    ):
        drop_dates.append(dropdate.text.strip().replace("\n", " "))

    base_url = "https://nftcalendar.io"
    drop_readmores = list()
    for readmore in nft_calendar.find_all(
        "div", {"class": "pt-4 pb-0 md:pt-2 md:pb-2 text-right md:text-left"}
    ):
        drop_readmores.append(base_url + readmore.find("a")["href"])

    return pd.DataFrame(
        list(zip(drop_titles, drop_dates, drop_readmores, drop_descriptions)),
        columns=["Title", "Dates", "Link", "Description"],
    )


@log_start_end(log=logger)
def get_nft_today_drops() -> pd.DataFrame:
    """Get NFT today drops [Source: nftcalendar.io]

    Returns
    -------
    pd.DataFrame
        NFT drops
    """
    return get_nft_drops("https://nftcalendar.io/")


@log_start_end(log=logger)
def get_nft_upcoming_drops() -> pd.DataFrame:
    """Get NFT upcoming drops [Source: nftcalendar.io]

    Returns
    -------
    pd.DataFrame
        NFT drops
    """
    return get_nft_drops("https://nftcalendar.io/events")


@log_start_end(log=logger)
def get_nft_ongoing_drops() -> pd.DataFrame:
    """Get NFT ongoing drops [Source: nftcalendar.io]

    Returns
    -------
    pd.DataFrame
        NFT drops
    """
    return get_nft_drops("https://nftcalendar.io/events/ongoing/")


@log_start_end(log=logger)
def get_nft_newest_drops() -> pd.DataFrame:
    """Get NFT newest drops [Source: nftcalendar.io]

    Returns
    -------
    pd.DataFrame
        NFT drops
    """
    return get_nft_drops("https://nftcalendar.io/events/newest/")
