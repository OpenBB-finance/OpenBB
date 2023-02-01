"""FDScanner model"""
__docformat__ = "numpy"

import logging
from typing import Tuple

import numpy as np
import pandas as pd

from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import get_user_agent, request
from openbb_terminal.rich_config import console

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def unusual_options(limit: int = 100) -> Tuple[pd.DataFrame, pd.Timestamp]:
    """Get unusual option activity from fdscanner.com

    Parameters
    ----------
    limit: int
        Number to show

    Returns
    -------
    Tuple[pd.DataFrame, pd.Timestamp]
        Dataframe containing options information, Timestamp indicated when data was updated from website

    Examples
    --------
    >>> from openbb_terminal.sdk import openbb
    >>> unu_df = openbb.stocks.options.unu()
    """
    pages = np.arange(0, limit // 20 + 1)
    data_list = []
    for page_num in pages:
        r = request(
            f"https://app.fdscanner.com/api2/unusualvolume?p=0&page_size=20&page={int(page_num)}",
            headers={"User-Agent": get_user_agent()},
        )

        if r.status_code != 200:
            console.print("Error in fdscanner request")
            return pd.DataFrame(), "request error"

        data_list.append(r.json())

    ticker, expiry, option_strike, option_type, ask, bid, oi, vol, voi = (
        [],
        [],
        [],
        [],
        [],
        [],
        [],
        [],
        [],
    )
    for data in data_list:
        for entry in data["data"]:
            ticker.append(entry["tk"])
            expiry.append(entry["expiry"])
            option_strike.append(float(entry["s"]))
            option_type.append("Put" if entry["t"] == "P" else "Call")
            ask.append(entry["a"])
            bid.append(entry["b"])
            oi.append(entry["oi"])
            vol.append(entry["v"])
            voi.append(entry["vol/oi"])

    # Subtract an hour to align with NYSE timezone
    last_updated = pd.to_datetime(
        data_list[-1]["last_updated"], unit="s"
    ) - pd.Timedelta(hours=5)

    df = pd.DataFrame(
        {
            "Ticker": ticker,
            "Exp": expiry,
            "Strike": option_strike,
            "Type": option_type,
            "Vol/OI": voi,
            "Vol": vol,
            "OI": oi,
            "Bid": bid,
            "Ask": ask,
        }
    )

    return df, last_updated
