"""Options Functions For OpenBB SDK"""

import logging
from typing import Optional, Union

import numpy as np
import pandas as pd
from scipy.optimize import minimize

from openbb_terminal.decorators import log_start_end
from openbb_terminal.stocks.options import (
    chartexchange_model,
    intrinio_model,
    nasdaq_model,
    op_helpers,
    tradier_model,
    yfinance_model,
)

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def get_full_option_chain(
    symbol: str, source: str = "Nasdaq", expiration: Union[str, None] = None
) -> pd.DataFrame:
    """Get Option Chain For A Stock.  No greek data is returned

    Parameters
    ----------
    symbol : str
        Symbol to get chain for
    source : str, optional
        Source to get data from, by default "Nasdaq".  Can be YahooFinance, Tradier, Nasdaq, or Intrinio
    expiration : Union[str, None], optional
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
    if source == "Intrinio":
        if expiration:
            return intrinio_model.get_option_chain(symbol, expiration)
        return (
            intrinio_model.get_full_option_chain(symbol)
            .sort_values(by=["expiration", "strike"])
            .reset_index(drop=True)
        )
    logger.info("Invalid Source")
    return pd.DataFrame()


@log_start_end(log=logger)
def get_option_expirations(symbol: str, source: str = "Nasdaq") -> list:
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
    if source == "Intrinio":
        return intrinio_model.get_expiration_dates(symbol)
    logger.info("Invalid Source")
    return pd.DataFrame()


@log_start_end(log=logger)
def hist(
    symbol: str,
    exp: str,
    strike: Union[int, Union[float, str]],
    call: bool = True,
    source="ChartExchange",
) -> pd.DataFrame:
    """Get historical option pricing.

    Parameters
    ----------
    symbol : str
        Symbol to get data for
    exp : str
        Expiration date
    strike : Union[int ,Union[float,str]]
        Strike price
    call : bool, optional
        Flag to indicate a call, by default True
    source : str, optional
        Source to get data from.  Can be ChartExchange or Tradier, by default "ChartExchange"

    Returns
    -------
    pd.DataFrame
        DataFrame of historical option pricing

    Examples
    --------
    >>> from openbb_terminal.sdk import openbb
    >>> aapl_150_call = openbb.stocks.options.hist("AAPL", "2022-11-18", 150, call=True, source="ChartExchange")

    Because this generates a dataframe, we can easily plot the close price for a SPY put:
    (Note that Tradier requires an API key)
    >>> openbb.stocks.options.hist("SPY", "2022-11-18", 400, call=False, source="Tradier").plot(y="close)
    """
    if source.lower() == "chartexchange":
        return chartexchange_model.get_option_history(symbol, exp, call, strike)
    if source.lower() == "tradier":
        return tradier_model.get_historical_options(symbol, exp, strike, not call)
    return pd.DataFrame()


def get_delta_neutral(symbol: str, date: str, x0: Optional[float] = None) -> float:
    """Get delta neutral price for symbol at a given close date

    Parameters
    ----------
    symbol : str
        Symbol to get delta neutral price for
    date : str
        Date to get delta neutral price for
    x0 : float, optional
        Optional initial guess for solver, defaults to close price of that day

    Returns
    -------
    float
        Delta neutral price
    """
    # Need an initial guess for the solver
    x0_guess = x0 if x0 else intrinio_model.get_close_at_date(symbol, date)
    chains = intrinio_model.get_full_chain_eod(symbol, date)

    return minimize(
        op_helpers.get_abs_market_delta,
        x0=x0_guess,
        args=(chains),
        bounds=[(0.01, np.inf)],
        method="l-bfgs-b",
    ).x[0]
