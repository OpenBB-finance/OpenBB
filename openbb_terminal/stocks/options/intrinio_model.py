"""Intrinio model"""
__docformat__ = "numpy"
import logging
from datetime import datetime, timedelta
from typing import List, Optional

import intrinio_sdk as intrinio
import numpy as np
import pandas as pd

from openbb_terminal.core.session.current_user import get_current_user
from openbb_terminal.decorators import check_api_key, log_start_end
from openbb_terminal.rich_config import console, optional_rich_track

logger = logging.getLogger(__name__)
intrinio.ApiClient().set_api_key(get_current_user().credentials.API_INTRINIO_KEY)
api = intrinio.OptionsApi()
security = intrinio.SecurityApi()

eod_columns_to_drop = [
    "open_ask",
    "open_bid",
    "ask_high",
    "ask_low",
    "bid_high",
    "bid_low",
    "mark",
]
columns_to_drop = [
    "id",
    "ticker",
    "date",
    "close_bid",
    "close_ask",
    "volume_bid",
    "volume_ask",
    "trades",
    "open_interest_change",
    "next_day_open_interest",
    "implied_volatility_change",
]


def calculate_dte(chain_df: pd.DataFrame) -> pd.DataFrame:
    """Adds a column calculating the difference between expiration and the date data is from

    Parameters
    ----------
    chain_df : pd.DataFrame
        Dataframe of intrinio options.  Must have date and expiration columns

    Returns
    -------
    pd.DataFrame
        Dataframe with dte column added
    """
    if "date" not in chain_df.columns:
        console.print("date column not in dataframe")
        return pd.DataFrame()
    if "expiration" not in chain_df.columns:
        console.print("expiration column not in dataframe")
        return pd.DataFrame()
    chain_df["dte"] = chain_df.apply(
        lambda row: (
            datetime.strptime(row["expiration"], "%Y-%m-%d")
            - datetime.strptime(row["date"], "%Y-%m-%d")
        ).days,
        axis=1,
    )
    return chain_df


@log_start_end(log=logger)
@check_api_key(["API_INTRINIO_KEY"])
def get_expiration_dates(
    symbol: str,
    start: str = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d"),
    end: str = "2100-12-30",
) -> List[str]:
    """Get all expirations from a start date until a specified end date.  Defaults to 100 years out to get all possible.

    Parameters
    ----------
    symbol : str
        Intrinio symbol to get expirations for
    start : str
        Start date for expirations, by default T-1 so that current day is included
    end : str, optional
        End date for intrinio endpoint, by default "2100-12-30"

    Returns
    -------
    List[str]
        List of expiration dates
    """
    return api.get_options_expirations(symbol, after=start, before=end).to_dict()[
        "expirations"
    ]


@log_start_end(log=logger)
@check_api_key(["API_INTRINIO_KEY"])
def get_option_chain(
    symbol: str,
    expiration: str,
) -> pd.DataFrame:
    """Get option chain at a given expiration

    Parameters
    ----------
    symbol : str
        Ticker to get option chain for
    expiration : str
        Expiration to get chain for

    Returns
    -------
    pd.DataFrame
        Dataframe of option chain
    """
    response = api.get_options_chain(
        symbol,
        expiration,
    ).chain_dict
    chain = pd.DataFrame()
    if not response:
        return pd.DataFrame()
    for opt in response:
        chain = pd.concat([chain, pd.json_normalize(opt)])
    chain.columns = [
        col.replace("option.", "").replace("price.", "") for col in chain.columns
    ]
    chain = chain.drop(columns=columns_to_drop).reset_index(drop=True)
    # Fill nan values with 0
    chain = chain.fillna(0).rename(
        columns={
            "type": "optionType",
            "open_interest": "openInterest",
            "implied_volatility": "impliedVolatility",
        }
    )
    return chain


@log_start_end(log=logger)
@check_api_key(["API_INTRINIO_KEY"])
def get_full_option_chain(symbol: str, quiet: bool = False) -> pd.DataFrame:
    """Get option chain across all expirations

    Parameters
    ----------
    symbol : str
        Symbol to get option chain for
    quiet: bool
        Flag to suppress progress bar

    Returns
    -------
    pd.DataFrame
        DataFrame of option chain
    """
    expirations = get_expiration_dates(symbol)
    chain = pd.DataFrame()
    for exp in optional_rich_track(
        expirations, suppress_output=quiet, desc="Getting option chain"
    ):
        chain = pd.concat([chain, get_option_chain(symbol, exp)])
    return chain.sort_values(by=["expiration", "strike"]).reset_index(drop=True)


@log_start_end(log=logger)
@check_api_key(["API_INTRINIO_KEY"])
def get_eod_chain_at_expiry_given_date(
    symbol: str, expiration: str, date: str, fillnans: bool = True
):
    """Get the eod chain for a given expiration at a given close day

    Parameters
    ----------
    symbol : str
        Symbol to get option chain for
    expiration : str
        Expiration day of option chain
    date : str
        Date to get option chain for
    fillnans : bool, optional
        Flag to fill nan values with 0, by default True

    Returns
    -------
    pd.DataFrame
        Dataframe of option chain
    """
    chain = pd.DataFrame()
    response = api.get_options_chain_eod(symbol, expiration, date=date).chain_dict
    if not response:
        return pd.DataFrame()
    for opt in response:
        chain = pd.concat([chain, pd.json_normalize(opt)])
    chain.columns = [
        col.replace("option.", "").replace("prices.", "") for col in chain.columns
    ]
    chain = chain.drop(columns=eod_columns_to_drop).reset_index(drop=True)
    if fillnans:
        # Replace None with 0
        chain = chain.fillna(0)
    return chain


@log_start_end(log=logger)
@check_api_key(["API_INTRINIO_KEY"])
def get_full_chain_eod(symbol: str, date: str, quiet: bool = False) -> pd.DataFrame:
    """Get full EOD option date across all expirations

    Parameters
    ----------
    symbol : str
        Symbol to get option chain for
    date : str
        Date to get EOD chain for
    quiet:bool
        Flag to suppress progress bar

    Returns
    -------
    pd.DataFrame
        Dataframe of options across all expirations at a given close

    Example
    -------
    To get the EOD chain for AAPL on Dec 23, 2022, we do the following

    >>> from openbb_terminal.sdk import openbb
    >>> eod_chain = openbb.stocks.options.eodchain("AAPL", date="2022-12-23")

    """
    expirations = get_expiration_dates(symbol)
    # Since we can't have expirations in the past, lets do something fun:
    # Note that there is an issue with using >= in that when the date = expiration, the dte will be 0, so iv*dte = 0*0
    expirations = list(filter(lambda x: x > date, expirations))

    full_chain = pd.DataFrame()

    for exp in optional_rich_track(
        expirations, suppress_output=quiet, desc="Getting Option Chain"
    ):
        temp = get_eod_chain_at_expiry_given_date(symbol, exp, date)
        if not temp.empty:
            full_chain = pd.concat([full_chain, temp])
    if full_chain.empty:
        return pd.DataFrame()
    full_chain = (
        full_chain.sort_values(by=["expiration", "strike"])
        .reset_index(drop=True)
        .rename(
            columns={
                "type": "optionType",
                "open_interest": "openInterest",
                "implied_volatility": "impliedVolatility",
            }
        )
    )
    if full_chain.empty:
        logger.info("No options found for %s on %s", symbol, date)
        return pd.DataFrame()
    return calculate_dte(full_chain)


@log_start_end(log=logger)
@check_api_key(["API_INTRINIO_KEY"])
def get_close_at_date(symbol: str, date: str) -> float:
    """Get adjusted close price at a given date

    Parameters
    ----------
    symbol : str
        Symbol to get price for
    date : str
        Date of close price

    Returns
    -------
    float
        close price
    """
    # Catch error if the price or ticker does not exist
    try:
        return (
            intrinio.SecurityApi()
            .get_security_historical_data(
                symbol,
                "adj_close_price",
                start_date=date,
                end_date=date,
                frequency="daily",
            )
            .to_dict()["historical_data"][0]["value"]
        )
    except Exception as e:
        logger.error(
            "Error getting close price for %s on %s, error: %s", symbol, date, e
        )
        return np.nan


@log_start_end(log=logger)
@check_api_key(["API_INTRINIO_KEY"])
def get_last_price(symbol: str) -> float:
    """Get the last price of a ticker

    Parameters
    ----------
    symbol : str
        Ticker to get last price for

    Returns
    -------
    float
        Last price of ticker
    """
    return (
        intrinio.SecurityApi().get_security_realtime_price(symbol, source="").last_price
    )


@log_start_end(log=logger)
@check_api_key(["API_INTRINIO_KEY"])
def get_historical_options(symbol: str) -> pd.DataFrame:
    """Get historical pricing option chain for a given symbol

    Parameters
    ----------
    symbol : str
        Symbol to get historical option chain for.  Should be an OCC chain label

    Returns
    -------
    pd.DataFrame
        Dataframe of historical option chain
    """
    historical = pd.DataFrame(api.get_options_prices_eod(symbol).to_dict()["prices"])
    historical = historical[
        [
            "date",
            "close",
            "volume",
            "open",
            "open_interest",
            "high",
            "low",
            "implied_volatility",
            "delta",
            "gamma",
            "theta",
            "vega",
        ]
    ]
    historical["date"] = pd.DatetimeIndex(historical.date)
    # Just in case
    historical = (
        historical.set_index("date")
        .rename(
            columns={
                "open_interest": "openInterest",
                "implied_volatility": "impliedVolatility",
            }
        )
        .fillna(0)
    )
    return historical


def get_all_ticker_symbols() -> list[str]:
    """Gets a list of all options tickers supported by Intrinio.

    Returns
    -------
    list: str
        List of all ticker symbols supported.
    """

    return api.get_all_options_tickers().tickers


def get_ticker_info(symbol: str) -> pd.Series:
    """Gets basic meta data for the ticker.

    Parameters
    ----------
    symbol: str
        The ticker symbol to lookup.

    Returns
    -------
    pd.Series
        Pandas Series object with meta data for the symbol.
    """

    info = security.get_security_by_id(symbol).to_dict()

    return pd.Series(info)


def get_underlying_price(symbol: str) -> pd.Series:
    """Gets the real time bid/ask and last price for the symbol.

    Parameters
    ----------
    symbol: str
        The ticker symbol to lookup.

    Returns
    -------
    pd.Series
        Pandas Series object with real time bid/ask and last price for the symbol.

    """
    underlying_price = security.get_security_realtime_price(symbol).to_dict()

    return pd.Series(underlying_price)


class Options:
    """Options data object for Intrinio

    Attributes
    ----------
    SYMBOLS: list[str]
        List of all ticker symbols supported by Intrinio.
    symbol: str
        The symbol entered by the user.
    source: str
        The source of the data, "Intrinio".
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
        True if greeks data is returned.
    """

    def __init__(self) -> None:
        self.SYMBOLS: list = get_all_ticker_symbols()
        self.symbol: str = ""
        self.source: str = "Intrinio"
        self.chains = pd.DataFrame()
        self.expirations: list = []
        self.strikes: list = []
        self.last_price: float = 0
        self.underlying_name: str = ""
        self.underlying_price = pd.Series(dtype=object)
        self.hasIV: bool
        self.hasGreeks: bool

    def get_quotes(self, symbol: str) -> object:
        self.symbol = symbol.upper()
        self.underlying_name = get_ticker_info(self.symbol)["name"]
        self.underlying_price = get_underlying_price(self.symbol)
        self.last_price = self.underlying_price["last_price"]
        self.chains = get_full_option_chain(self.symbol, quiet=True)
        self.chains.rename(columns={"code": "optionSymbol"}, inplace=True)
        self.expirations = []
        self.strikes = []
        if not self.chains.empty:
            self.expirations = self.chains["expiration"].unique().tolist()
            self.strikes = self.chains["strike"].sort_values().unique().tolist()
        self.hasIV = "impliedVolatility" in self.chains.columns
        self.hasGreeks = "gamma" in self.chains.columns
        return self

    def get_eod_chains(self, symbol: str, date: str) -> object:
        self.symbol = symbol.upper()
        if self.symbol not in self.SYMBOLS:
            print(f"{self.symbol}", "is not supported by Intrinio.")
            return self
        underlying = security.get_security_stock_prices(
            self.symbol, start_date=date, end_date=date, frequency="daily"
        ).to_dict()
        self.underlying_name = underlying["security"]["name"]
        self.underlying_price = pd.Series(underlying["stock_prices"][0])
        self.last_price = self.underlying_price["adj_close"]
        self.chains = get_full_chain_eod(self.symbol, date)
        self.expirations = []
        self.strikes = []
        if not self.chains.empty:
            self.expirations = self.chains["expiration"].unique().tolist()
            self.strikes = self.chains["strike"].sort_values().unique().tolist()
        self.hasIV = "impliedVolatility" in self.chains.columns
        self.hasGreeks = "gamma" in self.chains.columns

        return self


@check_api_key(["API_INTRINIO_KEY"])
def load_options(symbol: str, date: str = "") -> object:
    """Options data object for Intrinio.

    Parameters
    ----------
    symbol : str
        The ticker symbol to load.
    date: Optional[str]
        The date for EOD chains data.

    Returns
    -------
    SYMBOLS: list[str]
        List of all ticker symbols supported by Intrinio.
    symbol: str
        The symbol entered by the user.
    source: str
        The source of the data, "Intrinio".
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
        True if greeks data is returned.
    """

    ticker = Options()

    if symbol.upper() not in ticker.SYMBOLS:
        print(f"{symbol}", "is not supported by Intrinio.")
        return ticker

    if date != "":
        ticker.get_eod_chains(symbol, date)
        return ticker

    ticker.get_quotes(symbol)
    return ticker
