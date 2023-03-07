""" Business Insider Model """
__docformat__ = "numpy"

import logging

import pandas as pd
from bs4 import BeautifulSoup

from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import get_user_agent, request

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def get_insider_activity(symbol: str) -> pd.DataFrame:
    """Get insider activity. [Source: Business Insider]

    Parameters
    ----------
    symbol : str
        Ticker symbol to get insider activity data from

    Returns
    -------
    df_insider : pd.DataFrame
        Insider activity data
    """
    url_market_business_insider = (
        f"https://markets.businessinsider.com/stocks/{symbol.lower()}-stock"
    )
    text_soup_market_business_insider = BeautifulSoup(
        request(
            url_market_business_insider, headers={"User-Agent": get_user_agent()}
        ).text,
        "lxml",
    )

    d_insider = dict()
    l_insider_vals = list()
    for idx, insider_val in enumerate(
        text_soup_market_business_insider.findAll(
            "td", {"class": "table__td text-center"}
        )
    ):
        l_insider_vals.append(insider_val.text.strip())

        # Add value to dictionary
        if (idx + 1) % 6 == 0:
            # Check if we are still parsing insider trading activity
            if "/" not in l_insider_vals[0]:
                break
            d_insider[(idx + 1) // 6] = l_insider_vals
            l_insider_vals = list()

    df_insider = pd.DataFrame.from_dict(
        d_insider,
        orient="index",
        columns=["Date", "Shares Traded", "Shares Held", "Price", "Type", "Option"],
    )

    df_insider["Date"] = pd.to_datetime(df_insider["Date"])

    l_names = list()
    for s_name in text_soup_market_business_insider.findAll(
        "a", {"onclick": "silentTrackPI()"}
    ):
        l_names.append(s_name.text.strip())
    df_insider["Insider"] = l_names
    df_insider = df_insider.set_index("Date")
    df_insider = df_insider.sort_index(ascending=True)
    return df_insider
