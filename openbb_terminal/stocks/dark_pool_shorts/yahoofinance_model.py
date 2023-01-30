""" Yahoo Finance Model """
__docformat__ = "numpy"

import logging

import pandas as pd

from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import get_user_agent, request

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def get_most_shorted() -> pd.DataFrame:
    """Get most shorted stock screener [Source: Yahoo Finance]

    Returns
    -------
    pd.DataFrame
        Most Shorted Stocks
    """
    url = "https://finance.yahoo.com/screener/predefined/most_shorted_stocks"

    data = pd.read_html(request(url, headers={"User-Agent": get_user_agent()}).text)[0]
    data = data.iloc[:, :-1]
    return data
