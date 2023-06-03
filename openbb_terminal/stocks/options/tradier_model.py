"""Tradier options model"""
__docformat__ = "numpy"

import logging
from datetime import datetime
from typing import List, Optional

import pandas as pd
import requests

from openbb_terminal.core.session.current_user import get_current_user
from openbb_terminal.decorators import check_api_key, log_start_end
from openbb_terminal.helper_funcs import request
from openbb_terminal.rich_config import console, optional_rich_track
from openbb_terminal.stocks.options.op_helpers import Options, PydanticOptions

logger = logging.getLogger(__name__)

option_columns = [
    "symbol",
    "bid",
    "ask",
    "strike",
    "bidsize",
    "asksize",
    "volume",
    "open_interest",
    "option_type",
]
greek_columns = ["delta", "gamma", "theta", "vega", "ask_iv", "bid_iv", "mid_iv"]
df_columns = option_columns + greek_columns

default_columns = [
    "mid_iv",
    "vega",
    "delta",
    "gamma",
    "theta",
    "volume",
    "open_interest",
    "bid",
    "ask",
]

sorted_chain_columns = [
    "symbol",
    "option_type",
    "expiration",
    "strike",
    "bid",
    "ask",
    "open_interest",
    "volume",
    "mid_iv",
    "delta",
    "gamma",
    "theta",
    "vega",
]


@check_api_key(["API_TRADIER_TOKEN"])
def lookup_company(symbol: str):
    response = request(
        "https://sandbox.tradier.com/v1/markets/lookup",
        params={"q": f"{symbol}"},
        headers={
            "Authorization": f"Bearer {get_current_user().credentials.API_TRADIER_TOKEN }",  # type: ignore[attr-defined]
            "Accept": "application/json",
        },
    )
    return response.json()


@log_start_end(log=logger)
@check_api_key(["API_TRADIER_TOKEN"])
def get_historical_options(
    symbol: str,
    expiry: str,
    strike: float = 0,
    put: bool = False,
    chain_id: Optional[str] = None,
) -> pd.DataFrame:
    """
    Gets historical option pricing.  This inputs either ticker, expiration, strike or the OCC chain ID and processes
    the request to tradier for historical premiums.

    Parameters
    ----------
    symbol: str
        Stock ticker symbol
    expiry: str
        Option expiration date
    strike: int
        Option strike price
    put: bool
        Is this a put option?
    chain_id: Optional[str]
        OCC chain ID

    Returns
    -------
    df_hist: pd.DataFrame
        Dataframe of historical option prices
    """
    if not chain_id:
        op_type = ["call", "put"][put]
        chain = get_option_chain(symbol, expiry)
        chain = chain[chain["option_type"] == op_type]

        try:
            symbol = chain[(chain.strike == strike)]["symbol"].values[0]
        except IndexError:
            error = f"Strike: {strike}, Option type: {op_type} not found"
            logging.exception(error)
            console.print(f"{error}\n")
            return pd.DataFrame()
    else:
        symbol = chain_id

    try:
        response = request(
            "https://sandbox.tradier.com/v1/markets/history",
            params={"symbol": {symbol}, "interval": "daily"},
            headers={
                "Authorization": f"Bearer {get_current_user().credentials.API_TRADIER_TOKEN}",  # type: ignore[attr-defined]
                "Accept": "application/json",
            },
        )
    except requests.exceptions.ReadTimeout:
        return pd.DataFrame()

    if response.status_code != 200:
        console.print("Error with request")
        return pd.DataFrame()

    data = response.json()["history"]
    if not data:
        console.print("No historical data available")
        return pd.DataFrame()

    df_hist = pd.DataFrame(data["day"])
    df_hist = df_hist.set_index("date")
    df_hist.index = pd.DatetimeIndex(df_hist.index)
    return df_hist


# pylint: disable=no-else-return

option_cols = [
    "strike",
    "bid",
    "ask",
    "volume",
    "open_interest",
    "mid_iv",
]

option_col_map = {"open_interest": "openinterest", "mid_iv": "iv"}


@log_start_end(log=logger)
@check_api_key(["API_TRADIER_TOKEN"])
def get_full_option_chain(symbol: str, quiet: bool = False) -> pd.DataFrame:
    """Get available expiration dates for given ticker

    Parameters
    ----------
    symbol: str
        Ticker symbol to get expirations for
    quiet: bool
        Suppress output of progress bar

    Returns
    -------
    pd.DataFrame
        Dataframe of all option chains
    """

    expirations = option_expirations(symbol)
    options_dfs: pd.DataFrame = []

    for expiry in optional_rich_track(
        expirations, suppress_output=quiet, desc="Getting Option Chain"
    ):
        chain = get_option_chain(symbol, expiry)
        options_dfs.append(chain)
    chain = pd.concat(options_dfs)
    chain = chain[sorted_chain_columns].rename(
        columns={
            "mid_iv": "impliedVolatility",
            "open_interest": "openInterest",
            "option_type": "optionType",
            "symbol": "optionSymbol",
        }
    )
    chain["openInterest"] = chain["openInterest"].astype(int)
    chain["volume"] = chain["volume"].astype(int)
    chain = chain.set_index(["expiration", "strike", "optionType"]).sort_index()

    return chain.reset_index()


@log_start_end(log=logger)
@check_api_key(["API_TRADIER_TOKEN"])
def option_expirations(symbol: str) -> List[str]:
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
    r = request(
        "https://sandbox.tradier.com/v1/markets/options/expirations",
        params={"symbol": symbol, "includeAllRoots": "true", "strikes": "false"},
        headers={
            "Authorization": f"Bearer {get_current_user().credentials.API_TRADIER_TOKEN}",  # type: ignore[attr-defined]
            "Accept": "application/json",
        },
    )
    if r.status_code == 200:
        try:
            dates = r.json()["expirations"]["date"]
            return dates
        except TypeError:
            logging.exception("Error in tradier JSON response.  Check loaded ticker.")
            console.print("Error in tradier JSON response.  Check loaded ticker.\n")
            return []
    else:
        console.print("Tradier request failed.  Check token. \n")
        return []


@log_start_end(log=logger)
@check_api_key(["API_TRADIER_TOKEN"])
def get_option_chain(symbol: str, expiry: str) -> pd.DataFrame:
    """Display option chains [Source: Tradier]"

    Parameters
    ----------
    symbol : str
        Ticker to get options for
    expiry : str
        Expiration date in the form of "YYYY-MM-DD"

    Returns
    -------
    chains: pd.DataFrame
        Dataframe with options for the given Symbol and Expiration date
    """
    params = {"symbol": symbol, "expiration": expiry, "greeks": "true"}

    headers = {
        "Authorization": f"Bearer {get_current_user().credentials.API_TRADIER_TOKEN}",  # type: ignore[attr-defined]
        "Accept": "application/json",
    }

    response = request(
        "https://sandbox.tradier.com/v1/markets/options/chains",
        params=params,
        headers=headers,
    )
    if response.status_code != 200:
        console.print("Error in request. Check API_TRADIER_TOKEN\n")
        return pd.DataFrame()

    chains = process_chains(response)
    chains["expiration"] = expiry
    return chains


@log_start_end(log=logger)
def process_chains(response: requests.models.Response) -> pd.DataFrame:
    """Function to take in the request and return a DataFrame

    Parameters
    ----------
    response: requests.models.Response
        This is the response from tradier api.

    Returns
    -------
    opt_chain: pd.DataFrame
        Dataframe with all available options
    """
    json_response = response.json()
    options = json_response["options"]["option"]

    opt_chain = pd.DataFrame(columns=df_columns)
    for idx, option in enumerate(options):
        # initialize empty dictionary
        d = {col: "" for col in df_columns}
        # populate main dictionary values
        for col in option_columns:
            if col in option:
                d[col] = option[col]

        # populate greek dictionary values
        if option["greeks"]:
            for col in greek_columns:
                if col in option["greeks"]:
                    d[col] = option["greeks"][col]

        opt_chain.loc[idx, :] = d

    return opt_chain


@log_start_end(log=logger)
@check_api_key(["API_TRADIER_TOKEN"])
def get_last_price(symbol: str):
    """Makes api request for last price

    Parameters
    ----------
    symbol: str
        Ticker symbol

    Returns
    -------
    float:
        Last price
    """
    r = request(
        "https://sandbox.tradier.com/v1/markets/quotes",
        params={"symbols": symbol, "includeAllRoots": "true", "strikes": "false"},
        headers={
            "Authorization": f"Bearer {get_current_user().credentials.API_TRADIER_TOKEN}",  # type: ignore[attr-defined]
            "Accept": "application/json",
        },
    )
    if r.status_code == 200:
        last = r.json()["quotes"]["quote"]["last"]
        if last is None:
            return 0
        return float(last)
    else:
        console.print("Error getting last price")
        return None


@check_api_key(["API_TRADIER_TOKEN"])
def get_underlying_price(symbol: str) -> pd.Series:
    """Gets the current price and performance of the underlying asset.

    Parameters
    ----------
    symbol: str
        Ticker symbol

    Returns
    -------
    pd.Series:
        Series of current price and performance of the underlying asset.
    """
    r = request(
        "https://sandbox.tradier.com/v1/markets/quotes",
        params={"symbols": symbol, "includeAllRoots": "true", "strikes": "false"},
        headers={
            "Authorization": f"Bearer {get_current_user().credentials.API_TRADIER_TOKEN}",  # type: ignore[attr-defined]
            "Accept": "application/json",
        },
    )
    if r.status_code != 200:
        console.print("Error getting last price")
        return pd.DataFrame()
    underlying_price = pd.Series(r.json()["quotes"]["quote"])
    underlying_price = underlying_price.rename(
        {
            "description": "name",
            "change_percentage": "changePercent",
            "average_volume": "avgVolume",
            "last_volume": "volume",
            "trade_date": "lastTradeDate",
            "prevclose": "previousClose",
            "week_52_high": "fiftyTwoWeekHigh",
            "week_52_low": "fiftyTwoWeekLow",
            "bidsize": "bidSize",
            "bidexch": "bidExchange",
            "bid_date": "bidDate",
            "asksize": "askSize",
            "askexch": "askExchange",
            "ask_date": "askDate",
            "root_symbols": "rootSymbols",
        }
    )
    underlying_price = pd.DataFrame(underlying_price)
    underlying_price["lastTradeDate"] = (
        pd.to_datetime(underlying_price["lastTradeDate"], unit="ms").tz_localize("EST")
    ).strftime("%Y-%m-%d")
    underlying_price["bidDate"] = (
        pd.to_datetime(underlying_price["bidDate"], unit="ms").tz_localize("EST")
    ).strftime("%Y-%m-%d")
    underlying_price["askDate"] = (
        pd.to_datetime(underlying_price["askDate"], unit="ms").tz_localize("EST")
    ).strftime("%Y-%m-%d")

    return underlying_price


class Chains(Options):
    """OptionsChains data object for Tradier."""

    def __init__(self) -> None:
        self.SYMBOLS = pd.DataFrame(lookup_company("")["securities"]["security"])
        self.source: str = "Tradier"

    def get_chains(self, symbol: str) -> object:
        """Options data object for Tradier.

        Parameters
        ----------
        symbol : str
            The ticker symbol to load.
        date: Optional[str]
            The date for EOD chains data.

        Returns
        -------
        SYMBOLS: pd.DataFrame
            The symbol directory for Tradier.
        symbol: str
            The symbol entered by the user.
        source: str
            The source of the data, "Tradier".
        chains: pd.DataFrame
            The complete options chain for the ticker.
        expirations: list[str]
            List of unique expiration dates. (YYYY-MM-DD)
        strikes: list[float]
            List of unique strike prices.
        last_price: float
            The last price of the underlying asset.
        underlying_name: str
            The name of the underlying asset.
        underlying_price: pd.Series
            The price and recent performance of the underlying asset.
        hasIV: bool
            Implied volatility is returned.
        hasGreeks: bool
            Greeks data is returned.
        """

        self.source = "Tradier"
        self.symbol = symbol.upper()
        self.chains = pd.DataFrame()
        self.underlying_name = ""
        self.underlying_price = pd.Series(dtype=object)
        self.last_price = 0
        self.expirations = []
        self.strikes = []
        self.chains = pd.DataFrame()

        if self.symbol not in list(self.SYMBOLS["symbol"]):
            print(f"{self.symbol} is not support by Tradier.")
            return self
        self.underlying_price = get_underlying_price(self.symbol)
        self.underlying_name = self.underlying_price["name"]
        self.last_price = self.underlying_price["close"]
        self.chains = get_full_option_chain(self.symbol)
        if not self.chains.empty:
            self.expirations = self.chains["expiration"].unique().tolist()
            self.strikes = self.chains["strike"].sort_values().unique().tolist()

        now = datetime.now()
        temp = pd.DatetimeIndex(self.chains.expiration)
        temp_ = (temp - now).days + 1
        self.chains["dte"] = temp_

        self.hasIV = "impliedVolatility" in self.chains.columns
        self.hasGreeks = "gamma" in self.chains.columns
        return self


def load_options(symbol: str, pydantic: bool = False) -> object:
    """Options data object for CBOE.

    Parameters
    ----------
    symbol: str
        The ticker symbol to load.
    pydantic: bool
        Whether to return the object as a Pydantic Model or a subscriptable Pandas Object.  Default is False.

    Returns
    -------
    object: Options

        SYMBOLS: pd.DataFrame
            The Tradier symbol directory.  Only returned if pydantic is False.
        symbol: str
            The symbol entered by the user.
        source: str
            The source of the data, "Tradier".
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
            The price and recent performance of the underlying asset.  Returns as a Pandas Series if pydantic is False.
        hasIV: bool
            Returns implied volatility.
        hasGreeks: bool
            Returns greeks data.

    Examples
    --------
    Get current options chains for AAPL.
    >>> from openbb_terminal.stocks.options.tradier_model import load_options
    >>> data = load_options("AAPL")
    >>> chains = data.chains

    Return the object as a Pydantic Model.
    >>> from openbb_terminal.stocks.options.tradier_model import load_options
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
            chains=options.chains.copy().to_dict(),
        )
        return options_chains
    return None
