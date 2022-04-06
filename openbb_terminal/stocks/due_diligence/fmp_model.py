""" Financial Modeling Prep Model """
__docformat__ = "numpy"

import logging

import FundamentalAnalysis as fa
import pandas as pd

from openbb_terminal import config_terminal as cfg
from openbb_terminal.decorators import log_start_end

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
    if cfg.API_KEY_FINANCIALMODELINGPREP:
        try:
            df = fa.rating(ticker, cfg.API_KEY_FINANCIALMODELINGPREP)
        except ValueError as e:
            logger.exception(str(e))
            df = pd.DataFrame()
    else:
        df = pd.DataFrame()
    return df
