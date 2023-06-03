"""Nasdaq Model"""
__docformat__ = "numpy"

import logging
from datetime import datetime, timedelta
from typing import List

import numpy as np
import pandas as pd
import pandas_datareader

from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import request
from openbb_terminal.rich_config import console
from openbb_terminal.stocks.options.op_helpers import Options, PydanticOptions

logger = logging.getLogger(__name__)
# pylint: disable=unsupported-assignment-operation
# mypy: disable-error-code=no-redef

call_cols = [
    "c_Last",
    "c_Bid",
    "c_Ask",
    "c_Volume",
    "c_Openinterest",
    "strike",
    "expiration",
]
put_cols = [
    "p_Last",
    "p_Bid",
    "p_Ask",
    "p_Volume",
    "p_Openinterest",
    "strike",
    "expiration",
]
cols = ["lastPrice", "bid", "ask", "volume", "openInterest", "strike", "expiration"]

sorted_chain_columns = [
    "optionType",
    "expiration",
    "strike",
    "lastPrice",
    "bid",
    "ask",
    "openInterest",
    "volume",
]


def get_dte_from_expiration(date: str) -> float:
    """
    Converts a date to total days until the option would expire.
    This assumes that the date is in the form %B %d, %Y such as January 11, 2023
    This calculates time from 'now' to 4 PM the date of expiration
    This is particularly a helper for nasdaq results.

    Parameters
    ----------
    date: str
        Date in format %B %d, %Y

    Returns
    -------
    float
        Days to expiration as a decimal
    """
    # Get the date as a datetime and add 16 hours (4PM)
    expiration_time = datetime.strptime(date, "%B %d, %Y") + timedelta(hours=16)
    # Find total seconds from now
    time_to_now = (expiration_time - datetime.now()).total_seconds()
    # Convert to days
    time_to_now /= 60 * 60 * 24
    return time_to_now


@log_start_end(log=logger)
def get_full_option_chain(symbol: str) -> pd.DataFrame:
    """Get the full option chain for symbol over all expirations

    Parameters
    ----------
    symbol: str
        Symbol to get options for.  Can be a stock, etf or index.

    Returns
    -------
    pd.DataFrame
        Dataframe of option chain
    """
    # Nasdaq requires an asset code, so instead of making user supply one, just loop through all
    for asset in ["stocks", "index", "etf"]:
        url = (
            f"https://api.nasdaq.com/api/quote/{symbol}/option-chain?assetclass={asset}&"
            "fromdate=2010-09-09&todate=2030-09-09&excode=oprac&callput=callput&money=all&type=all"
        )
        # I have had issues with nasdaq requests, and this user agent seems to work in US and EU
        response_json = request(
            url,
            headers={
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"
                " AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.6 Safari/605.1.15"
            },
        ).json()

        if response_json["status"]["rCode"] == 200:
            return process_response(response_json)

    console.print(f"[red]{symbol} Option Chain not found.[/red]\n")
    return pd.DataFrame()


def process_response(response_json):
    df = pd.DataFrame(response_json["data"]["table"]["rows"]).drop(
        columns=["c_colour", "p_colour", "drillDownURL"]
    )
    df["expirygroup"] = df["expirygroup"].replace("", np.nan).fillna(method="ffill")
    df["expiration"] = pd.to_datetime(
        df["expirygroup"], format="%B %d, %Y"
    ).dt.strftime("%Y-%m-%d")
    # Make numeric
    columns_w_types = {
        "c_Last": float,
        "c_Change": float,
        "c_Bid": float,
        "c_Ask": float,
        "c_Volume": int,
        "c_Openinterest": int,
        "strike": float,
        "p_Last": float,
        "p_Change": float,
        "p_Bid": float,
        "p_Ask": float,
        "p_Volume": int,
        "p_Openinterest": int,
    }

    for key, _ in columns_w_types.items():
        df[key] = df[key].replace(",", "", regex=True)

    df = df.fillna(np.nan).dropna(axis=0).replace("--", 0).astype(columns_w_types)
    df["DTE"] = df["expirygroup"].apply(lambda t: get_dte_from_expiration(t))
    df = df[df.DTE > 0]
    df = df.drop(columns=["DTE"])

    # Process into consistent format
    calls = df[call_cols].copy()
    puts = df[put_cols].copy()

    calls.columns = cols
    puts.columns = cols
    calls["optionType"] = "call"
    puts["optionType"] = "put"

    chain = (
        pd.concat([calls, puts], axis=0)
        .sort_values(by=["expiration", "strike"])
        .reset_index(drop=True)
    )

    return chain[sorted_chain_columns]


@log_start_end(log=logger)
def option_expirations(symbol: str) -> List[str]:
    """Get available expirations

    Parameters
    ----------
    symbol : str
        Ticker symbol to get expirations for

    Returns
    -------
    List[str]
        List of expiration dates
    """
    df = get_full_option_chain(symbol)

    if df.empty:
        return []

    # get everything that is not an empty string
    return [exp for exp in list(df.expiration.unique()) if exp]


@log_start_end(log=logger)
def get_last_price(symbol: str) -> float:
    """Get the last price from nasdaq

    Parameters
    ----------
    symbol: str
        Symbol to get quote for

    Returns
    -------
    float
        Last price
    """
    for asset in ["stocks", "index", "etf"]:
        url = f"https://api.nasdaq.com/api/quote/{symbol}/info?assetclass={asset}"
        response_json = request(
            url,
            headers={
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"
                " AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.6 Safari/605.1.15"
            },
        ).json()
        if response_json["status"]["rCode"] == 200:
            return float(
                response_json["data"]["primaryData"]["lastSalePrice"]
                .strip("$")
                .replace(",", "")
            )
    console.print(f"[red]Last price for {symbol} not found[/red]\n")
    return np.nan


@log_start_end(log=logger)
def get_underlying_price(symbol: str) -> pd.Series:
    """Get the last price from nasdaq

    Parameters
    ----------
    symbol: str
        Symbol to get quote for

    Returns
    -------
    float
        Last price
    """
    df = pd.Series(dtype=object)
    for asset in ["stocks", "index", "etf"]:
        url = f"https://api.nasdaq.com/api/quote/{symbol}/info?assetclass={asset}"
        response_json = request(
            url,
            headers={
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"
                " AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.6 Safari/605.1.15"
            },
        ).json()
        if response_json["status"]["rCode"] == 200:
            data = response_json["data"]
            data = pd.Series(data)
            df["companyName"] = data["companyName"]
            df["lastPrice"] = float(
                data["primaryData"]["lastSalePrice"].strip("$").replace(",", "")
            )
            df["change"] = float(data["primaryData"]["netChange"])
            df["changePercent"] = float(
                data["primaryData"]["percentageChange"].replace("%", "")
            )
            df["volume"] = data["primaryData"]["volume"].replace(",", "")
            df["date"] = pd.to_datetime(
                data["primaryData"]["lastTradeTimestamp"], yearfirst=True
            ).strftime("%Y-%m-%d")
            return df.rename(symbol)

    console.print(f"[red]Last price for {symbol} not found[/red]\n")
    return pd.Series()


# Ugh this doesn't get the full chain
# TODO: apply CRR binomial tree to backtrack IV for greeks
@log_start_end(log=logger)
def get_option_greeks(symbol: str, expiration: str) -> pd.DataFrame:
    """Get option greeks from nasdaq

    Parameters
    ----------
    symbol: str
        Symbol to get
    expiration: str
        Option expiration

    Returns
    -------
    pd.DataFrame
        Dataframe with option greeks
    """
    for asset in ["stocks", "index", "etf"]:
        url_greeks = f"https://api.nasdaq.com/api/quote/{symbol}/option-chain/greeks?assetclass={asset}&date={expiration}"
        response_json = request(
            url_greeks,
            headers={
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"
                " AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.6 Safari/605.1.15"
            },
        ).json()
        if response_json["status"]["rCode"] == 200:
            greeks = pd.DataFrame(response_json["data"]["table"]["rows"])
            greeks = greeks.drop(columns="url")
            return greeks

    console.print(f"[red]Greeks not found for {symbol} on {expiration}[/red].")
    return pd.DataFrame()


class Chains(Options):
    """OptionsChains data object for Nasdaq."""

    def __init__(self) -> None:
        self.SYMBOLS: pd.DataFrame = (
            pandas_datareader.nasdaq_trader.get_nasdaq_symbols()
        )
        self.source: str = "Nasdaq"

    def get_chains(self, symbol: str) -> object:
        """Load options data for Nasdaq.  Parameters and attributes are the same as `load_options()`."""

        self.source = "Nasdaq"
        self.symbol = symbol.upper()
        self.chains = pd.DataFrame()
        self.underlying_name = ""
        self.underlying_price = pd.Series(dtype=object)
        self.last_price = 0
        self.expirations = []
        self.strikes = []

        if self.symbol not in self.SYMBOLS.index and self.symbol != "NDX":
            print(self.symbol, "was not found in the Nasdaq directory")
            return self

        try:
            self.chains = get_full_option_chain(self.symbol)
            now = datetime.now()
            temp = pd.DatetimeIndex(self.chains.expiration)
            temp_ = (temp - now).days + 1
            self.chains["dte"] = temp_
        except Exception:
            return self
        if not self.chains.empty:
            self.expirations = option_expirations(self.symbol)
            self.strikes = (
                pd.Series(self.chains["strike"]).sort_values().unique().tolist()
            )
            self.underlying_price = get_underlying_price(self.symbol)
            self.last_price = self.underlying_price["lastPrice"]
            self.underlying_name = self.underlying_price["companyName"]

        self.hasIV = "impliedVolatility" in self.chains.columns
        self.hasGreeks = "gamma" in self.chains.columns

        return self

    def get_available_greeks(self, expiration: str = "") -> pd.DataFrame:
        """Get available greeks for a specific expiration.
        This function will return data for strike prices near the money only.

        Parameters
        ----------
        expiration: str
            The expiration date to return the data.  Default is the first available date. (YYYY-MM-DD)

        Returns
        -------
        pd.DataFrame
            Dataframe with option greeks and strike prices.

        Examples
        --------
        Near-the-Money Greeks for the closest expiration date.

        >>> greeks = self.get_available_greeks()

        Get the last expiration date.

        >>> greeks = self.get_available_greeks(self.expirations[-1])
        """

        if expiration == "":
            expiration = self.expirations[0]

        if expiration not in self.expirations:
            print(
                f"{expiration}",
                " is not a valid expiration.  Choose from, ",
                self.expirations,
                sep="",
            )
            return self

        greeks = get_option_greeks(self.symbol, expiration)

        return greeks


def load_options(symbol: str, pydantic: bool = False) -> object:
    """Options data object for Nasdaq.

    Parameters
    ----------
    symbol: str
        The ticker symbol to load.
    pydantic: bool
        Whether to return the object as a Pydantic Model or a subscriptable Pandas Object.  Default is False.

    Returns
    -------
    object: Options

        symbol: str
            The symbol entered by the user.
        source: str
            The source of the data, "Nasdaq".
        chains: dict
            The complete options chain for the ticker.  Returns as a Pandas DataFrame if pydantic is False.
        expirations: list[str]
            List of unique expiration dates. (YYYY-MM-DD)
        strikes: list[float]
            List of unique strike prices.
        last_price: float
            The last price of the underlying asset.
        underlying_name: str
            The name of the underlying asset.
        underlying_price: dict
            The price of the underlying asset.  Returns as a Pandas Series if pydantic is False.
        hasIV: bool
            Does not return implied volatility.
        hasGreeks: bool
            Does not return greeks data.

    Examples
    --------
    Get current options chains for AAPL.
    >>> from openbb_terminal.stocks.options.nasdaq_model import load_options
    >>> data = load_options("AAPL")
    >>> chains = data.chains

    Return the object as a Pydantic Model.
    >>> from openbb_terminal.stocks.options.nasdaq_model import load_options
    >>> data = load_options("AAPL", pydantic=True)
    """

    options = Chains()
    options.get_chains(symbol)

    if not pydantic:
        return options

    if not options.chains.empty:
        if options.last_price is None:
            options.last_price = 0
            print("No last price for " + options.symbol)
        options_chains = PydanticOptions(
            source=options.source,
            symbol=options.symbol,
            underlying_name=options.underlying_name,
            last_price=options.last_price,
            expirations=options.expirations,
            strikes=options.strikes,
            hasIV=options.hasIV,
            hasGreeks=options.hasGreeks,
            underlying_price=options.underlying_price.to_dict(),
            chains=options.chains.to_dict(),
        )
        return options_chains
    return None
