""" Financial Modeling Prep Model """
__docformat__ = "numpy"

import FundamentalAnalysis as fa
from gamestonk_terminal import config_terminal as cfg


def get_rating(ticker: str):
    """Get ratings for a given ticker. [Source: Financial Modeling Prep]

    Parameters
    ----------
    ticker : str
        Stock ticker
    """
    return fa.rating(ticker, cfg.API_KEY_FINANCIALMODELINGPREP)
