"""Options Functions For OpenBB SDK"""

import logging
import re
from datetime import datetime, timedelta
from typing import Optional, Union

import numpy as np
import pandas as pd

from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import get_rf
from openbb_terminal.rich_config import console
from openbb_terminal.stocks.options import (
    chartexchange_model,
    intrinio_model,
    nasdaq_model,
    tradier_model,
    yfinance_model,
)
from openbb_terminal.stocks.options.op_helpers import Option

logger = logging.getLogger(__name__)

# pylint:disable=C0302


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
        Source to get data from, by default "Nasdaq". Can be YahooFinance, Tradier, Nasdaq, or Intrinio
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

    source = re.sub(r"\s+", "", source.lower())
    df = pd.DataFrame()
    if source == "tradier":
        df = tradier_model.get_full_option_chain(symbol)

    elif source == "nasdaq":
        df = nasdaq_model.get_full_option_chain(symbol)

    elif source == "yahoofinance":
        df = yfinance_model.get_full_option_chain(symbol)

    elif source == "intrinio":
        df = intrinio_model.get_full_option_chain(symbol)

    if not isinstance(df, pd.DataFrame) or df.empty:
        logger.info("Invalid Source or Symbol")
        console.print("Invalid Source or Symbol")
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
        Source to get data, by default "Nasdaq". Can be Nasdaq, Tradier, or YahooFinance

    Returns
    -------
    float
        float of current price

    Examples
    --------
    >>> from openbb_terminal.sdk import openbb
    >>> aapl_price = openbb.stocks.options.price("AAPL", source="Nasdaq")
    """

    source = re.sub(r"\s+", "", source.lower())
    output = None
    if source == "tradier":
        output = tradier_model.get_last_price(symbol)
    if source == "nasdaq":
        output = nasdaq_model.get_last_price(symbol)
    if source == "yahoofinance":
        output = yfinance_model.get_last_price(symbol)

    if not output:
        logger.info("Invalid Source or Symbol")
        console.print("Invalid Source or Symbol")
        return 0.0

    return output


@log_start_end(log=logger)
def get_option_expirations(symbol: str, source: str = "Nasdaq") -> list:
    """Get Option Chain Expirations

    Parameters
    ----------
    symbol : str
        Symbol to get chain for
    source : str, optional
        Source to get data from, by default "Nasdaq". Can be Intrinio, Tradier, Nasdaq, or YahooFinance

    Returns
    -------
    pd.DataFrame
        Dataframe of full option chain.

    Examples
    --------
    >>> from openbb_terminal.sdk import openbb
    >>> SPX_expirations = openbb.stocks.options.expirations("SPX", source = "Tradier")
    """
    source = re.sub(r"\s+", "", source.lower())
    output = []
    if source == "tradier":
        output = tradier_model.option_expirations(symbol)
    if source == "yahoofinance":
        output = yfinance_model.option_expirations(symbol)
    if source == "nasdaq":
        output = nasdaq_model.option_expirations(symbol)
    if source == "intrinio":
        output = intrinio_model.get_expiration_dates(symbol)

    if not output:
        logger.info("Invalid Source or Symbol")
        console.print("Invalid Source or Symbol")
        return []

    return output


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
        Source to get data from, by default "ChartExchange". Can be ChartExchange, Intrinio, or Tradier

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

    source = re.sub(r"\s+", "", source.lower())
    output = pd.DataFrame()
    if source == "chartexchange":
        output = chartexchange_model.get_option_history(symbol, exp, call, strike)
    if source == "tradier":
        output = tradier_model.get_historical_options(symbol, exp, strike, not call)
    if source == "intrinio":
        occ_symbol = f"{symbol}{''.join(exp[2:].split('-'))}{'C' if call else 'P'}{str(int(1000*strike)).zfill(8)}"
        output = intrinio_model.get_historical_options(occ_symbol)

    if not isinstance(output, pd.DataFrame) or output.empty:
        logger.info("No data found for symbol, check symbol and expiration date")
        console.print("No data found for symbol, check symbol and expiration date")
        return pd.DataFrame()

    return output


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
        is_call = row["optionType"] == "call"
        try:
            opt = Option(
                current_price, row["strike"], risk_free, div_cont, dif, vol, is_call
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
        except ValueError:
            tmp = [np.nan] * 9
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
