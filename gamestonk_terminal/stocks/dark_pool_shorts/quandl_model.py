""" Quandl Model """
__docformat__ = "numpy"

import logging

import pandas as pd
import quandl

from gamestonk_terminal import config_terminal as cfg
from gamestonk_terminal.decorators import log_start_end

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def get_short_interest(ticker: str, nyse: bool) -> pd.DataFrame:
    """Plots the short interest of a stock. This corresponds to the
    number of shares that have been sold short but have not yet been
    covered or closed out. Either NASDAQ or NYSE [Source: Quandl]

    Parameters
    ----------
    ticker : str
        ticker to get short interest from
    nyse : bool
        data from NYSE if true, otherwise NASDAQ

    Returns
    ----------
    pd.DataFrame
        short interest volume data
    """
    quandl.ApiConfig.api_key = cfg.API_KEY_QUANDL

    if nyse:
        return quandl.get(f"FINRA/FNYX_{ticker}")

    return quandl.get(f"FINRA/FNSQ_{ticker}")
