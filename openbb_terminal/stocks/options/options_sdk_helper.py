"""Options Functions For OpenBB SDK"""

import logging

import pandas as pd

from openbb_terminal.stocks.options import yfinance_model, tradier_model, nasdaq_model

logger = logging.getLogger(__name__)


def get_full_option_chain(symbol: str, source: str = "Nasdaq"):
    """Get Option Chain For A Stock.  No greek data is returned

    Parameters
    ----------
    symbol : str
        Symbol to get chain for
    source : str, optional
        Source to get data from, by default "Nasdaq"

    Returns
    -------
    pd.DataFrame
        Dataframe of full option chain across all expirations

    Examples
    --------
    >>> from openbb_terminal.sdk import openbb
    >>> aapl_option_chain = openbb.stocks.options.chains("AAPL", source = "Nasdaq")
    """

    if source == "Tradier":
        return tradier_model.get_full_option_chain(symbol)
    if source == "YahooFinance":
        return yfinance_model.get_full_option_chain(symbol)
    if source == "Nasdaq":
        return nasdaq_model.get_full_option_chain(symbol)
    logger.info("Invalid Source")
    return pd.DataFrame()
