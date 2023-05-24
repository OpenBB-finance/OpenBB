""" Options Chains Module """
__docformat__ = "numpy"

# IMPORTATION STANDARD
import logging

# IMPORTATION THIRDPARTY
from typing import Callable

import numpy as np
import pandas as pd

# IMPORTATION INTERNAL
from openbb_terminal.decorators import log_start_end
from openbb_terminal.stocks.options.cboe_model import load_options as load_cboe
from openbb_terminal.stocks.options.intrinio_model import load_options as load_intrinio
from openbb_terminal.stocks.options.nasdaq_model import load_options as load_nasdaq
from openbb_terminal.stocks.options.tmx_model import load_options as load_tmx
from openbb_terminal.stocks.options.tradier_model import load_options as load_tradier
from openbb_terminal.stocks.options.yfinance_model import load_options as load_yfinance

logger = logging.getLogger(__name__)

SOURCES = ["CBOE", "YahooFinance", "Tradier", "Intrinio", "Nasdaq", "TMX"]


@log_start_end(log=logger)
def load_options_chains(
    symbol: str,
    source: str = "CBOE",
    date: str = "",
    pydantic: bool = False,
) -> object:
    """Loads all options chains from a specific source, fields returned to each attribute will vary.

    Parameters
    ----------
    symbol : str
        The underlying asset's symbol.
    source: str
        The source of the data. Choices are "CBOE", "YahooFinance", "Tradier", "Intrinio", "Nasdaq", or "TMX".
    date: Optional[str]
        The date for the EOD option chain.  Format: YYYY-MM-DD.
        This parameter is only available for "TMX" or "Intrinio".
    pydantic: bool
        Whether to return the object as a Pydantic Model or a subscriptable Pandas object.  Default is False.

    Returns
    -------
    object: Options

        chains: dict
            All options chains data from a specific source.  Returns as a Pandas DataFrame if pydantic is False.
        expirations: list[str]
            List of all unique expiration dates.
        hasGreeks: bool
            True if the source returns greeks with the chains data.
        hasIV: bool
            True if the source returns implied volatility with the chains data.
        last_price: float
            The last price (or the price at the EOD for the date.of the EOD option chain).
        source: str
            The source that was entered in the input.
        strikes: list[float]
            List of all unique strike prices.
        symbol: str
            The symbol that was entered in the input.
        SYMBOLS: pd.DataFrame
            The symbol directory to the selected source, when available.  Only returned when pydantic is False.
        underlying_name: str
            The name of the underlying asset.
        underlying_price: dict
            The underlying asset's price and performance.  Returns as a Pandas Series if pydantic is False.

    Examples
    --------
    Loads SPY data from CBOE, returns as a Pydantic Model, and displays the longest-dated expiration chain.

    >>> from openbb_terminal.sdk import openbb
    >>> import pandas as pd
    >>> data = openbb.stocks.options.load_options_chains("SPY", pydantic = True)
    >>> chains = pd.DataFrame(data.chains)
    >>> chains[chains["expiration"] == data.expirations[-1]]

    Loads QQQ data from Tradier as a Pydantic Model.

    >>> from openbb_terminal.sdk import openbb
    >>> data = openbb.stocks.options.load_options_chains("QQQ", source = "Tradier", pydantic = True)

    Loads VIX data from YahooFinance as a Pandas object.

    >>> from openbb_terminal.sdk import openbb
    >>> data = openbb.stocks.options.load_options_chains("^VIX", source = "YahooFinance")

    Loads XIU data from TMX and displays the 25 highest open interest options.

    >>> from openbb_terminal.sdk  import openbb
    >>> data = openbb.stocks.options.load_options_chains("XIU", "TMX")
    >>> data.chains.sort_values("openInterest", ascending=False).head(25)

    Loads the EOD chains data for XIU.TO from March 15, 2020, sorted by number of transactions.

    >>> from openbb_terminal.sdk  import openbb
    >>> data = openbb.stocks.options.load_options_chains("XIU.TO", "TMX", "2020-03-15")
    >>> data.chains.sort_values("transactions", ascending=False).head(25)
    """

    if source not in SOURCES:
        print("Invalid choice. Choose from: ", list(SOURCES), sep=None)
        return None

    if source == "Nasdaq":
        return load_nasdaq(symbol, pydantic)
    if source == "YahooFinance":
        return load_yfinance(symbol, pydantic)
    if source == "Tradier":
        return load_tradier(symbol, pydantic)
    if source == "TMX":
        if date != "":
            return load_tmx(symbol, date, pydantic)
        return load_tmx(symbol, pydantic=pydantic)
    if source == "Intrinio":
        if date != "":
            return load_intrinio(symbol, date, pydantic)
        return load_intrinio(symbol, pydantic=pydantic)

    return load_cboe(symbol, pydantic)


@log_start_end(log=logger)
def calculate_stats(options: object, type: str = "expiration") -> pd.DataFrame:
    """Calculates basic statistics for the options chains, like OI and Vol/OI ratios.

    Parameters
    ----------
    options : object
        The OptionsChains data object.
        Accepts both Pydantic and Pandas object types, as defined by `load_options_chains()`.
        A Pandas DataFrame, or dictionary, with the options chains data is also accepted.
    type: str
        Whether to calculate by strike or expiration.  Default is expiration.

    Returns
    -------
    pd.DataFrame
        Pandas DataFrame with the calculated statistics.

    Examples
    --------
    >>> from openbb_terminal.stocks.options.options_chains_model import OptionsChains
    >>> data = OptionsChains().load_options_chains("SPY")
    >>> OptionsChains().calculate_stats(data)
    >>> OptionsChains().calculate_stats(data, "strike")
    >>> OptionsChains().calculate_stats(data.chains, "expiration")
    """

    types = ["expiration", "strike"]
    try:
        if type not in types:
            print("Invalid choice. Choose from: expiration, strike")
            return pd.DataFrame()

        if isinstance(options, pd.DataFrame):
            chains = options.copy()

        if isinstance(options, dict):
            chains = pd.DataFrame(options)

        elif isinstance(options, object) and not isinstance(options, pd.DataFrame):
            chains = (
                pd.DataFrame(options.chains)
                if isinstance(options.chains, dict)
                else options.chains.copy()
            )

            if options is None or chains.empty:
                print(
                    "No options chains data found in the supplied object.  Use load_options_chains()."
                )
                return pd.DataFrame()

        if "openInterest" not in chains.columns:
            print("Expected column, openInterest, not found.")
            return pd.DataFrame()

        if "volume" not in chains.columns:
            print("Expected column, volume, not found.")
            return pd.DataFrame()
    except AttributeError:
        print("Error: Invalid data type supplied.")
        return pd.DataFrame()

    stats = pd.DataFrame()
    stats["Puts OI"] = (
        chains[chains["optionType"] == "put"]
        .groupby(f"{type}")
        .sum(numeric_only=True)[["openInterest"]]
        .astype(int)
    )
    stats["Calls OI"] = (
        chains[chains["optionType"] == "call"]
        .groupby(f"{type}")
        .sum(numeric_only=True)[["openInterest"]]
        .astype(int)
    )
    stats["Total OI"] = stats["Calls OI"] + stats["Puts OI"]
    stats["OI Ratio"] = round(stats["Puts OI"] / stats["Calls OI"], 2)
    stats["Puts Volume"] = (
        chains[chains["optionType"] == "put"]
        .groupby(f"{type}")
        .sum(numeric_only=True)[["volume"]]
        .astype(int)
    )
    stats["Calls Volume"] = (
        chains[chains["optionType"] == "call"]
        .groupby(f"{type}")
        .sum(numeric_only=True)[["volume"]]
        .astype(int)
    )
    stats["Total Volume"] = stats["Calls Volume"] + stats["Puts Volume"]
    stats["Volume Ratio"] = round(stats["Puts Volume"] / stats["Calls Volume"], 2)
    stats["Vol-OI Ratio"] = round(stats["Total Volume"] / stats["Total OI"], 2)

    return stats.replace([np.nan, np.inf], "")


class OptionsChains:
    """Class for Options Chains."""

    def __init__(self) -> None:
        self.load_options_chains: Callable = load_options_chains
        self.calculate_stats: Callable = calculate_stats
