# mypy: disable-error-code=attr-defined

"""Yfinance options model"""
__docformat__ = "numpy"

import logging
from datetime import datetime
from typing import Any, Dict, List, Tuple

import pandas as pd
import yfinance as yf

from openbb_terminal.decorators import log_start_end
from openbb_terminal.rich_config import console, optional_rich_track
from openbb_terminal.stocks.options.op_helpers import Options, PydanticOptions

logger = logging.getLogger(__name__)

sorted_chain_columns = [
    "contractSymbol",
    "optionType",
    "expiration",
    "strike",
    "lastPrice",
    "bid",
    "ask",
    "openInterest",
    "volume",
    "impliedVolatility",
]


def get_full_option_chain(symbol: str, quiet: bool = False) -> pd.DataFrame:
    """Get all options for given ticker [Source: Yahoo Finance]

    Parameters
    ----------
    symbol: str
        Stock ticker symbol
    quiet: bool
        Flag to suppress progress bar

    Returns
    -------
    pd.Dataframe
        Option chain
    """
    ticker = yf.Ticker(symbol)
    dates = ticker.options

    options = pd.DataFrame()

    for _date in optional_rich_track(
        dates, suppress_output=quiet, desc="Getting Option Chain"
    ):
        calls = ticker.option_chain(_date).calls
        calls["optionType"] = "call"
        calls["expiration"] = _date
        calls = calls[sorted_chain_columns]
        puts = ticker.option_chain(_date).puts
        puts["optionType"] = "put"
        puts["expiration"] = _date
        puts = puts[sorted_chain_columns]

        temp = pd.merge(calls, puts, how="outer", on="strike")
        temp["expiration"] = _date
        options = (
            pd.concat([options, pd.concat([calls, puts])], axis=0)
            .fillna(0)
            .reset_index(drop=True)
        )
    return options


@log_start_end(log=logger)
def get_option_chain(symbol: str, expiry: str):
    """Gets option chain from yf for given ticker and expiration

    Parameters
    ----------
    symbol: str
        Ticker symbol to get options for
    expiry: str
        Date to get options for. YYYY-MM-DD

    Returns
    -------
    chains: yf.ticker.OptionsChains
        OptionsChains chain
    """

    yf_ticker = yf.Ticker(symbol)
    try:
        chain = yf_ticker.option_chain(expiry)
    except Exception:
        console.print(f"[red]Error: Expiration {expiry} cannot be found.[/red]")
        chain = pd.DataFrame()

    return chain


@log_start_end(log=logger)
def option_expirations(symbol: str):
    """Get available expiration dates for given ticker

    Parameters
    ----------
    symbol: str
        Ticker symbol to get expirations for

    Returns
    -------
    dates: List[str]
        List of of available expirations
    """
    yf_ticker = yf.Ticker(symbol)
    dates = list(yf_ticker.options)
    if not dates:
        console.print("No expiration dates found for ticker.")
    return dates


@log_start_end(log=logger)
def get_dividend(symbol: str) -> pd.Series:
    """Gets option chain from yf for given ticker and expiration

    Parameters
    ----------
    symbol: str
        Ticker symbol to get options for

    Returns
    -------
    chains: yf.ticker.Dividends
        Dividends
    """
    yf_ticker = yf.Ticker(symbol)
    dividend = yf_ticker.dividends
    return dividend


@log_start_end(log=logger)
def get_x_values(current_price: float, options: List[Dict[str, int]]) -> List[float]:
    """Generates different price values that need to be tested"""
    x_list = list(range(101))
    mini = current_price
    maxi = current_price
    if len(options) == 0:
        mini *= 0.5
        maxi *= 1.5
    elif len(options) > 0:
        biggest = max(options, key=lambda x: x["strike"])
        smallest = min(options, key=lambda x: x["strike"])
        maxi = max(maxi, biggest["strike"]) * 1.2
        mini = min(mini, smallest["strike"]) * 0.8
    num_range = maxi - mini
    return [(x / 100) * num_range + mini for x in x_list]


def get_y_values(
    base: float,
    price: float,
    options: List[Dict[Any, Any]],
    underlying: int,
) -> float:
    """Generates y values for corresponding x values"""
    option_change = 0
    change = price - base
    for option in options:
        if option["type"] == "Call":
            abs_change = price - option["strike"] if price > option["strike"] else 0
            option_change += option["sign"] * abs_change
        elif option["type"] == "Put":
            abs_change = option["strike"] - price if price < option["strike"] else 0
            option_change += option["sign"] * abs_change
    return (change * underlying) + option_change


@log_start_end(log=logger)
def generate_data(
    current_price: float, options: List[Dict[str, int]], underlying: int
) -> Tuple[List[float], List[float], List[float]]:
    """Gets x values, and y values before and after premiums"""

    # Remove empty elements from options
    options = [o for o in options if o]

    x_vals = get_x_values(current_price, options)
    base = current_price
    total_cost = sum(x["cost"] for x in options)
    before = [get_y_values(base, x, options, underlying) for x in x_vals]
    if total_cost != 0:
        after = [
            get_y_values(base, x, options, underlying) - total_cost for x in x_vals
        ]
        return x_vals, before, after
    return x_vals, before, []


@log_start_end(log=logger)
def get_price(symbol: str) -> float:
    """Get current price for a given ticker

    Parameters
    ----------
    symbol : str
        The ticker symbol to get the price for

    Returns
    -------
    price : float
        The price of the ticker
    """
    ticker_yahoo = yf.Ticker(symbol)
    data = ticker_yahoo.history()
    last_quote = data.tail(1)["Close"].iloc[0]

    return last_quote


@log_start_end(log=logger)
def get_info(symbol: str):
    """Get info for a given ticker

    Parameters
    ----------
    symbol : str
        The ticker symbol to get the price for

    Returns
    -------
    price : float
        The info for a given ticker
    """
    tick = yf.Ticker(symbol)
    return tick.info


@log_start_end(log=logger)
def get_closing(symbol: str) -> pd.Series:
    """Get closing prices for a given ticker

    Parameters
    ----------
    symbol : str
        The ticker symbol to get the price for

    Returns
    -------
    price : List[float]
        A list of closing prices for a ticker
    """
    tick = yf.Ticker(symbol)
    return tick.history(period="1y")["Close"]


def get_dte(date_value: str) -> int:
    """Gets days to expiration from yfinance option date"""
    return (datetime.strptime(date_value, "%Y-%m-%d") - datetime.now()).days


@log_start_end(log=logger)
def get_iv_surface(symbol: str) -> pd.DataFrame:
    """Gets IV surface for calls and puts for ticker

    Parameters
    ----------
    symbol: str
        Stock ticker symbol to get

    Returns
    -------
    pd.DataFrame
        Dataframe of DTE, Strike and IV
    """

    stock = yf.Ticker(symbol)
    dates = stock.options
    vol_df = pd.DataFrame()
    columns = ["strike", "impliedVolatility", "openInterest", "lastPrice"]
    for date_value in dates:
        df = stock.option_chain(date_value).calls[columns]
        df["dte"] = get_dte(date_value)
        vol_df = pd.concat([vol_df, df], axis=0)
        df = stock.option_chain(date_value).puts[columns]
        df["dte"] = get_dte(date_value)
        vol_df = pd.concat([vol_df, df], axis=0)
    return vol_df


@log_start_end(log=logger)
def get_last_price(symbol: str) -> pd.Series:
    """Get the price and performance of the underlying asset.

    Parameters
    ----------
    symbol: str
        Symbol to get quote for

    Returns
    -------
    pd.Series
        Pandas Series with the price and performance of the underlying asset.
    """

    ticker = yf.Ticker(symbol).fast_info
    df = pd.Series(dtype=object)
    df["lastPrice"] = round(ticker["lastPrice"], 2)
    df["previousClose"] = round(ticker["previousClose"], 2)
    df["open"] = round(ticker["open"], 2)
    df["high"] = round(ticker["dayHigh"], 2)
    df["low"] = round(ticker["dayLow"], 2)
    df["yearHigh"] = round(ticker["yearHigh"], 2)
    df["yearLow"] = round(ticker["yearLow"], 2)
    df["fiftyDayMA"] = round(ticker["fiftyDayAverage"], 2)
    df["twoHundredDayMA"] = round(ticker["twoHundredDayAverage"], 2)

    return df.loc["lastPrice"]


@log_start_end(log=logger)
def get_underlying_price(symbol: str) -> pd.Series:
    """Get the price and performance of the underlying asset.

    Parameters
    ----------
    symbol: str
        Symbol to get quote for

    Returns
    -------
    pd.Series
        Pandas Series with the price and performance of the underlying asset.
    """

    ticker = yf.Ticker(symbol).fast_info
    df = pd.Series(dtype=object)
    df["lastPrice"] = round(ticker["lastPrice"], 2)
    df["previousClose"] = round(ticker["previousClose"], 2)
    df["open"] = round(ticker["open"], 2)
    df["high"] = round(ticker["dayHigh"], 2)
    df["low"] = round(ticker["dayLow"], 2)
    df["yearHigh"] = round(ticker["yearHigh"], 2)
    df["yearLow"] = round(ticker["yearLow"], 2)
    df["fiftyDayMA"] = round(ticker["fiftyDayAverage"], 2)
    df["twoHundredDayMA"] = round(ticker["twoHundredDayAverage"], 2)

    return df.rename(f"{symbol}")


def load_options(symbol: str, pydantic: bool = False) -> Options:
    """OptionsChains data object for YahooFinance.

    Parameters
    ----------
    symbol: str
        The ticker symbol to load.
    pydantic: bool
        Whether to return the object as a Pydantic Model or a subscriptable Pandas Object.  Default is False.

    Returns
    -------
    object: OptionsChains
        chains: pd.DataFrame
            The complete options chain for the ticker. Returns as a dictionary if pydantic is True.
        expirations: list[str]
            List of unique expiration dates. (YYYY-MM-DD)
        strikes: list[float]
            List of unique strike prices.
        last_price: float
            The last price of the underlying asset.
        underlying_name: str
            The name of the underlying asset.
        underlying_price: pd.Series
            The price and recent performance of the underlying asset. Returns as a dictionary if pydantic is True.
        hasIV: bool
            Returns implied volatility.
        hasGreeks: bool
            Does not return greeks data.
        symbol: str
            The symbol entered by the user.
        source: str
            The source of the data,  "YahooFinance".

    Examples
    --------
    Get current options chains for AAPL.
    >>> from openbb_terminal.stocks.options.yfinance_model import load_options
    >>> data = load_options("AAPL")
    >>> chains = data.chains

    Return the object as a Pydantic Model.
    >>> from openbb_terminal.stocks.options.yfinance_model import load_options
    >>> data = load_options("AAPL", pydantic=True)
    """
    OptionsChains = Options()

    OptionsChains.source = "YahooFinance"
    OptionsChains.symbol = symbol.upper()

    chains = get_full_option_chain(OptionsChains.symbol)

    if not chains.empty:
        OptionsChains.expirations = option_expirations(OptionsChains.symbol)
        OptionsChains.strikes = (
            pd.Series(chains["strike"]).sort_values().unique().tolist()
        )
        OptionsChains.underlying_price = get_underlying_price(OptionsChains.symbol)
        OptionsChains.underlying_name = OptionsChains.symbol
        OptionsChains.last_price = OptionsChains.underlying_price["lastPrice"]
        now = datetime.now()
        temp = pd.DatetimeIndex(chains.expiration)
        temp_ = (temp - now).days + 1
        chains["dte"] = temp_

    OptionsChains.chains = chains
    OptionsChains.hasIV = "impliedVolatility" in OptionsChains.chains.columns
    OptionsChains.hasGreeks = "gamma" in OptionsChains.chains.columns

    if not chains.empty and OptionsChains.last_price is None:
        OptionsChains.last_price = 0
        console.print("No last price for " + OptionsChains.symbol)

    if not pydantic:
        return OptionsChains

    OptionsChainsPydantic = PydanticOptions(
        chains=OptionsChains.chains.to_dict(),
        expirations=OptionsChains.expirations,
        strikes=OptionsChains.strikes,
        last_price=OptionsChains.last_price,
        underlying_name=OptionsChains.underlying_name,
        underlying_price=OptionsChains.underlying_price.to_dict(),
        hasIV=OptionsChains.hasIV,
        hasGreeks=OptionsChains.hasGreeks,
        symbol=OptionsChains.symbol,
        source=OptionsChains.source,
    )
    return OptionsChainsPydantic
