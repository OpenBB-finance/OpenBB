""" Financial Modeling Prep Model """
__docformat__ = "numpy"

import pandas as pd
import FundamentalAnalysis as fa
from gamestonk_terminal import config_terminal as cfg


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
