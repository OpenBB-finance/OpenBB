"""Options Functions For OpenBB SDK"""

import logging
from datetime import datetime, timedelta
from typing import Optional, Union

import numpy as np
import pandas as pd
from scipy.optimize import minimize

from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import get_rf
from openbb_terminal.rich_config import console
from openbb_terminal.stocks.options import (
    chartexchange_model,
    intrinio_model,
    nasdaq_model,
    op_helpers,
    tradier_model,
    yfinance_model,
)
from openbb_terminal.stocks.options.op_helpers import Option

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

    elif source == "Nasdaq":
        df = nasdaq_model.get_full_option_chain(symbol)

    elif source == "YahooFinance":
        df = yfinance_model.get_full_option_chain(symbol)

    elif source == "Intrinio":
        df = intrinio_model.get_full_option_chain(symbol)

    else:
        logger.info("Invalid Source")
        return pd.DataFrame()

    if expiration:
        df = df[df.expiration == expiration]

    return df


def get_option_current_price(
    symbol: str,
    source: str = "Nasdaq",
):
    """Get Option current price for a stock.

    Parameters
    ----------
    symbol : str
        Symbol to get chain for
    source : str, optional
        Source to get data from, by default "Nasdaq"

    Returns
    -------
    float
        float of current price

    Examples
    --------
    >>> from openbb_terminal.sdk import openbb
    >>> aapl_price = openbb.stocks.options.price("AAPL", source="Nasdaq")
    """

    if source == "Tradier":
        last_price = tradier_model.get_last_price(symbol)
        return last_price if last_price else 0.0
    if source == "Nasdaq":
        return nasdaq_model.get_last_price(symbol)
    if source == "YahooFinance":
        return yfinance_model.get_last_price(symbol)
    logger.info("Invalid Source")
    return 0.0


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
        return nasdaq_model.option_expirations(symbol)
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
    >>> openbb.stocks.options.hist("SPY", "2022-11-18", 400, call=False, source="Tradier").plot(y="close")
    """
    if source.lower() == "chartexchange":
        return chartexchange_model.get_option_history(symbol, exp, call, strike)
    if source.lower() == "tradier":
        return tradier_model.get_historical_options(symbol, exp, strike, not call)
    if source.lower() == "intrinio":
        occ_symbol = f"{symbol}{''.join(exp[2:].split('-'))}{'C' if call else 'P'}{str(int(1000*strike)).zfill(8)}"
        return intrinio_model.get_historical_options(occ_symbol)
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
    if x0:
        x0_guess = x0
    else:
        # Check that the close price exists.  I am finding that holidays are not consistent, such as June 20, 2022
        try:
            x0_guess = intrinio_model.get_close_at_date(symbol, date)
        except Exception:
            console.print("Error getting close price for symbol, check date and symbol")
            return np.nan
    x0_guess = x0 if x0 else intrinio_model.get_close_at_date(symbol, date)
    chains = intrinio_model.get_full_chain_eod(symbol, date)
    if chains.empty:
        return np.nan
    # Lots of things can go wrong with minimizing, so lets add a general exception catch here.
    try:
        res = minimize(
            op_helpers.get_abs_market_delta,
            x0=x0_guess,
            args=(chains),
            bounds=[(0.01, np.inf)],
            method="l-bfgs-b",
        )
        return res.x[0]
    except Exception as e:
        logging.info(
            "Error getting delta neutral price for %s on %s: error:%s", symbol, date, e
        )
        return np.nan


def get_greeks(
    current_price: float,
    chain: pd.DataFrame,
    expire: str,
    div_cont: float = 0,
    rf: Optional[float] = None,
) -> pd.DataFrame:
    """
    Gets the greeks for a given option

    Parameters
    ----------
    current_price: float
        The current price of the underlying
    chain: pd.DataFrame
        The dataframe with option chains
    div_cont: float
        The dividend continuous rate
    expire: str
        The date of expiration
    rf: float
        The risk-free rate

    Returns
    -------
    pd.DataFrame
        Dataframe with calculated option greeks

    Examples
    --------
    >>> from openbb_terminal.sdk import openbb
    >>> aapl_chain = openbb.stocks.options.chains("AAPL", source="Tradier")
    >>> aapl_last_price = openbb.stocks.options.last_price("AAPL")
    >>> greeks = openbb.stocks.options.greeks(aapl_last_price, aapl_chain, aapl_chain.iloc[0, 2])
    """

    chain = chain.rename(columns={"iv": "impliedVolatility"})
    chain_columns = chain.columns.tolist()
    if not all(
        col in chain_columns for col in ["strike", "impliedVolatility", "optionType"]
    ):
        if "delta" not in chain_columns:
            console.print(
                "[red]It's not possible to calculate the greeks without the following "
                "columns: `strike`, `impliedVolatility`, `optionType`.\n[/red]"
            )
        return pd.DataFrame()

    risk_free = rf if rf is not None else get_rf()
    expire_dt = datetime.strptime(expire, "%Y-%m-%d")
    dif = (expire_dt - datetime.now() + timedelta(hours=16)).total_seconds() / (
        60 * 60 * 24
    )
    strikes = []
    for _, row in chain.iterrows():
        vol = row["impliedVolatility"]
        opt_type = 1 if row["optionType"] == "call" else -1
        opt = Option(
            current_price, row["strike"], risk_free, div_cont, dif, vol, opt_type
        )
        tmp = [
            opt.Delta(),
            opt.Gamma(),
            opt.Vega(),
            opt.Theta(),
            opt.Rho(),
            opt.Phi(),
            opt.Charm(),
            opt.Vanna(0.01),
            opt.Vomma(0.01),
        ]
        result = [row[col] for col in row.index.tolist()]
        result += tmp

        strikes.append(result)

    greek_columns = [
        "Delta",
        "Gamma",
        "Vega",
        "Theta",
        "Rho",
        "Phi",
        "Charm",
        "Vanna",
        "Vomma",
    ]
    columns = chain_columns + greek_columns

    df = pd.DataFrame(strikes, columns=columns)

    return df
