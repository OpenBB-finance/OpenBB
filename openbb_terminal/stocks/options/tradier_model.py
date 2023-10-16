# mypy: disable-error-code=attr-defined

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
                "Authorization": f"Bearer {get_current_user().credentials.API_TRADIER_TOKEN}",
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
    underlying_price = pd.Series(dtype=object)
    underlying_price = pd.Series(r.json()["quotes"]["quote"])
    underlying_price = underlying_price.rename(
        index={
            "description": "name",
            "change_percentage": "changePercent",
            "average_volume": "avgVolume",
            "last_volume": "volume",
            "trade_date": "lastTradeTimestamp",
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
    underlying_price[  # pylint: disable=unsupported-assignment-operation
        "lastTradeTimestamp"
    ] = (
        pd.to_datetime(underlying_price["lastTradeTimestamp"], unit="ms").tz_localize(
            "EST"
        )
    ).strftime(
        "%Y-%m-%d"
    )
    underlying_price["bidDate"] = (  # pylint: disable=unsupported-assignment-operation
        pd.to_datetime(underlying_price["bidDate"], unit="ms").tz_localize("EST")
    ).strftime("%Y-%m-%d")
    underlying_price["askDate"] = (  # pylint: disable=unsupported-assignment-operation
        pd.to_datetime(underlying_price["askDate"], unit="ms").tz_localize("EST")
    ).strftime("%Y-%m-%d")

    return underlying_price


def get_chains(symbol: str) -> Options:
    """OptionsChains data object for Tradier.

    Parameters
    ----------
    symbol : str
        The ticker symbol to load.

    Returns
    -------
    object: OptionsChains
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
            Returns implied volatility.
        hasGreeks: bool
            Returns greeks data.
        symbol: str
            The symbol entered by the user.
        source: str
            The source of the data, "Tradier".
        SYMBOLS: pd.DataFrame
            Tradier symbol directory.

    Examples
    --------
    >>> from openbb_terminal.stocks.options import tradier_model
    >>> data = tradier_model.load_options("AAPL")
    >>> chains = tradier_model.chains
    """

    OptionsChains = Options()
    OptionsChains.source = "Tradier"

    try:
        OptionsChains.SYMBOLS = pd.DataFrame(
            lookup_company("")["securities"]["security"]
        )
    except requests.exceptions.JSONDecodeError:
        return OptionsChains

    OptionsChains.symbol = symbol.upper()

    if OptionsChains.symbol not in list(OptionsChains.SYMBOLS["symbol"]):
        console.print(f"{OptionsChains.symbol} is not support by Tradier.")
        return OptionsChains

    OptionsChains.underlying_price = get_underlying_price(OptionsChains.symbol)
    OptionsChains.underlying_name = OptionsChains.underlying_price["name"]
    OptionsChains.last_price = OptionsChains.underlying_price["last"]

    chains = get_full_option_chain(OptionsChains.symbol)

    if not chains.empty:
        OptionsChains.expirations = chains["expiration"].unique().tolist()
        OptionsChains.strikes = chains["strike"].sort_values().unique().tolist()

    now = datetime.now()
    temp = pd.DatetimeIndex(chains.expiration)
    temp_ = (temp - now).days + 1
    chains["dte"] = temp_

    OptionsChains.chains = chains

    OptionsChains.hasIV = "impliedVolatility" in OptionsChains.chains.columns
    OptionsChains.hasGreeks = "gamma" in OptionsChains.chains.columns

    return OptionsChains


def load_options(symbol: str, pydantic: bool = False) -> Options:
    """OptionsChains data object for Tradier.

    Parameters
    ----------
    symbol: str
        The ticker symbol to load.
    pydantic: bool
        Whether to return the object as a Pydantic Model or a subscriptable Pandas Object.  Default is False.

    Returns
    -------
    object: Options
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
            Returns greeks data.
        symbol: str
            The symbol entered by the user.
        source: str
            The source of the data, "Tradier".
        SYMBOLS: pd.DataFrame
            Tradier symbol directory. Returns as a dictionary if pydantic is True.

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

    options = get_chains(symbol)

    if options.last_price is None:
        options.last_price = 0
        console.print("No last price for " + options.symbol)

    if not pydantic:
        return options

    if not options.chains.empty:
        OptionsChainsPydantic = PydanticOptions(
            chains=options.chains.to_dict(),
            expirations=options.expirations,
            strikes=options.strikes,
            last_price=options.last_price,
            underlying_name=options.underlying_name,
            underlying_price=options.underlying_price.to_dict(),
            hasIV=options.hasIV,
            hasGreeks=options.hasGreeks,
            symbol=options.symbol,
            source=options.source,
            SYMBOLS=options.SYMBOLS.to_dict(),
        )
        return OptionsChainsPydantic

    return Options()
