"""AlphaQuery Model"""
__docformat__ = "numpy"

import logging
from datetime import datetime, timedelta
from typing import Optional

import pandas as pd

from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import request

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def get_put_call_ratio(
    symbol: str,
    window: int = 30,
    start_date: Optional[str] = None,
) -> pd.DataFrame:
    """Gets put call ratio over last time window [Source: AlphaQuery.com]

    Parameters
    ----------
    symbol: str
        Ticker symbol to look for
    window: int, optional
        Window to consider, by default 30
    start_date: Optional[str], optional
        Start date to plot  (e.g., 2021-10-01), by default last 366 days

    Returns
    -------
    pd.DataFrame
        Put call ratio

    Examples
    --------
    >>> from openbb_terminal.sdk import openbb
    >>> pcr_df = openbb.stocks.options.pcr("B")
    """

    if start_date is None:
        start_date = (datetime.now() - timedelta(days=366)).strftime("%Y-%m-%d")

    url = f"https://www.alphaquery.com/data/option-statistic-chart?ticker={symbol}\
        &perType={window}-Day&identifier=put-call-ratio-volume"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) \
            Chrome/70.0.3538.77 Safari/537.36"
    }

    r = request(url, headers=headers)
    if r.status_code != 200:
        return pd.DataFrame()

    pcr = pd.DataFrame.from_dict(r.json())
    pcr.rename(columns={"x": "Date", "value": "PCR"}, inplace=True)
    pcr.set_index("Date", inplace=True)
    pcr.index = pd.to_datetime(pcr.index).tz_localize(None)

    return pcr[pcr.index > start_date]
