""" Market Watch Model """
__docformat__ = "numpy"

import logging

import pandas as pd
import requests
from bs4 import BeautifulSoup

from gamestonk_terminal.decorators import log_start_end
from gamestonk_terminal.helper_funcs import get_user_agent

# pylint: disable=too-many-branches


logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def get_sec_filings(ticker: str) -> pd.DataFrame:
    """Get SEC filings for a given stock ticker. [Source: Market Watch]

    Parameters
    ----------
    ticker : str
        Stock ticker

    Returns
    -------
    df_financials : pd.DataFrame
        SEC filings data
    """

    pd.set_option("display.max_colwidth", None)

    url_financials = (
        f"https://www.marketwatch.com/investing/stock/{ticker}/financials/secfilings"
    )

    text_soup_financials = BeautifulSoup(
        requests.get(url_financials, headers={"User-Agent": get_user_agent()}).text,
        "lxml",
    )

    # a_financials_header = list()
    df_financials = None
    b_ready_to_process_info = False
    soup_financials = text_soup_financials.findAll("tr", {"class": "table__row"})
    for financials_info in soup_financials:
        a_financials = financials_info.text.split("\n")

        # If header has been processed and dataframe created ready to populate the SEC information
        if b_ready_to_process_info:
            l_financials_info = [a_financials[2]]
            l_financials_info.extend(a_financials[5:-1])
            l_financials_info.append(financials_info.a["href"])
            # Append data values to financials
            df_financials.loc[len(df_financials.index)] = l_financials_info  # type: ignore

        if "Filing Date" in a_financials:
            l_financials_header = [a_financials[2]]
            l_financials_header.extend(a_financials[5:-1])
            l_financials_header.append("Link")

            df_financials = pd.DataFrame(columns=l_financials_header)
            df_financials.set_index("Filing Date")
            b_ready_to_process_info = True

    # Set Filing Date as index
    df_financials = df_financials.set_index("Filing Date")  # type: ignore

    return df_financials
