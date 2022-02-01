""" Financial Modeling Prep Model """
__docformat__ = "numpy"

import logging

import FundamentalAnalysis as fa
import pandas as pd

from gamestonk_terminal import config_terminal as cfg
from gamestonk_terminal.decorators import log_start_end

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def get_rating(ticker: str) -> pd.DataFrame:
    """Get ratings for a given ticker. [Source: Financial Modeling Prep]

    Parameters
    ----------
    ticker : str
        Stock ticker

    Returns
    -------
    pd.DataFrame
        Rating data
    """
    return fa.rating(ticker, cfg.API_KEY_FINANCIALMODELINGPREP)
