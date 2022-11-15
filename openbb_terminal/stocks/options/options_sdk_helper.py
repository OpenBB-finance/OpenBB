"""Options Functions For OpenBB SDK"""

import logging
from typing import List, Optional
import pandas as pd

from openbb_terminal.stocks.options import nasdaq_model, tradier_model, yfinance_model
from openbb_terminal.decorators import log_start_end

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def get_full_option_chain(
    symbol: str, source: str = "Nasdaq", expiration: Optional[str] = None
) -> pd.DataFrame:
    """Get Option Chain For A Stock.  No greek data is returned

    Parameters
    ----------
    symbol : str
        Symbol to get chain for
    source : str, optional
        Source to get data from, by default "Nasdaq"
    expiration : str, optional
        Date to get chain for.  By default returns all dates

    Returns
    -------
    pd.DataFrame
        Dataframe of full option chain.

    Examples
    --------
    >>> from openbb_terminal.sdk import openbb
    >>> aapl_option_chain = openbb.stocks.options.chains("AAPL", source = "Nasdaq")

    To get a specific expiration date, use the expiration parameter

    >>> aapl_chain_date = openbb.stocks.options.chains("AAPL", expiration="2023-07-21", source="Nasdaq")
    """

    if source == "Tradier":
        df = tradier_model.get_full_option_chain(symbol)
        if expiration:
            return df[df.expiration == expiration]
        return df
    if source == "YahooFinance":
        df = yfinance_model.get_full_option_chain(symbol)
        if expiration:
            return df[df.expiration == expiration]
        return df
    if source == "Nasdaq":
        # Nasdaq handles these slightly differently
        if expiration:
            return nasdaq_model.get_chain_given_expiration(symbol, expiration)
        return nasdaq_model.get_full_option_chain(symbol)
    logger.info("Invalid Source")
    return pd.DataFrame()


@log_start_end(log=logger)
def get_option_expirations(symbol: str, source: str = "Nasdaq") -> List:
    """Get Option Chain Expirations

    Parameters
    ----------
    symbol : str
        Symbol to get chain for
    source : str, optional
        Source to get data from, by default "Nasdaq"

    Returns
    -------
    pd.DataFrame
        Dataframe of full option chain.

    Examples
    --------
    >>> from openbb_terminal.sdk import openbb
    >>> SPX_expirations = openbb.stocks.options.expirations("SPX", source = "Tradier")
    """

    if source == "Tradier":
        return tradier_model.option_expirations(symbol)
    if source == "YahooFinance":
        return yfinance_model.option_expirations(symbol)
    if source == "Nasdaq":
        return nasdaq_model.get_expirations(symbol)

    logger.info("Invalid Source")
    return pd.DataFrame()
