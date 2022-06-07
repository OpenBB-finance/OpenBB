"""Business Insider Model"""
__docformat__ = "numpy"

import logging

import pandas as pd
import requests
from bs4 import BeautifulSoup
from rapidfuzz import fuzz

from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import get_user_agent
from openbb_terminal.rich_config import console

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def get_management(ticker: str) -> pd.DataFrame:
    """Get company managers from Business Insider

    Parameters
    ----------
    ticker : str
        Stock ticker

    Returns
    -------
    pd.DataFrame
        Dataframe of managers
    """
    url_market_business_insider = (
        f"https://markets.businessinsider.com/stocks/{ticker.lower()}-stock"
    )
    text_soup_market_business_insider = BeautifulSoup(
        requests.get(
            url_market_business_insider, headers={"User-Agent": get_user_agent()}
        ).text,
        "lxml",
    )

    found_h2s = {}

    for next_h2 in text_soup_market_business_insider.findAll(
        "h2", {"class": "header-underline"}
    ):
        next_table = next_h2.find_next_sibling("table", {"class": "table"})

        if next_table:
            found_h2s[next_h2.text] = next_table

    # Business Insider changed management display convention from 'Management' to
    # 'Ticker Management'. These next few lines simply find 'Ticker Management'
    # header key and copy it to a 'Management' key as to not alter the rest of
    # the function
    ticker_management_to_be_deleted = ""
    management_data_available = False
    for key in found_h2s:
        if "Management" in key:
            ticker_management_to_be_deleted = key
            management_data_available = True
    if management_data_available:
        found_h2s["Management"] = found_h2s[ticker_management_to_be_deleted]
        del found_h2s[ticker_management_to_be_deleted]

    if found_h2s.get("Management") is None:
        console.print(f"No management information in Business Insider for {ticker}")
        console.print("")
        return pd.DataFrame()

    l_titles = []
    for s_title in found_h2s["Management"].findAll(
        "td", {"class": "table__td text-right"}
    ):
        if any(c.isalpha() for c in s_title.text.strip()) and (
            "USD" not in s_title.text.strip()
        ):
            l_titles.append(s_title.text.strip())

    l_names = []
    for s_name in found_h2s["Management"].findAll(
        "td", {"class": "table__td table--allow-wrap"}
    ):
        l_names.append(s_name.text.strip())

    df_management = pd.DataFrame(
        {"Name": l_names[-len(l_titles) :], "Title": l_titles},  # noqa: E203
        columns=["Name", "Title"],
    )

    df_management["Info"] = "-"
    df_management["Insider Activity"] = "-"
    df_management = df_management.set_index("Name")

    for s_name in df_management.index:
        df_management.loc[s_name][
            "Info"
        ] = f"http://www.google.com/search?q={s_name} {ticker.upper()}".replace(
            " ", "%20"
        )

    s_url_base = "https://markets.businessinsider.com"
    for insider in text_soup_market_business_insider.findAll(
        "a", {"onclick": "silentTrackPI()"}
    ):
        for s_name in df_management.index:
            if fuzz.token_set_ratio(s_name, insider.text.strip()) > 70:  # type: ignore
                df_management.loc[s_name]["Insider Activity"] = (
                    s_url_base + insider.attrs["href"]
                )
    return df_management
