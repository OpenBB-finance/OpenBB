""" Options Chains Module """
__docformat__ = "numpy"

# IMPORTATION STANDARD
import logging

# IMPORTATION THIRDPARTY
from typing import Optional

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
    symbol: str, source: str = "CBOE", date: Optional[str] = "", pydantic: bool = True
) -> object:
    """Loads all options chains from a specific source, fields returned to each attribute will vary.

    Parameters
    ----------
    symbol : str
        The underlying asset's symbol.
    source: str
        The source of the data. Choices are "CBOE", "YahooFinance", "Tradier", "Intrinio", "Nasdaq", or "TMX".
    date: str
        The date for the EOD option chain.  Format: YYYY-MM-DD.
        This parameter is only available for "TMX" or "Intrinio".
    pydantic: bool
        Whether to return the object as a Pydantic Model or a Pandas object.  Default is True.

    Returns
    -------
    Pydantic

        chains: dict
            All options chains data from a specific source.
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
        SYMBOLS: dict
            The symbol directory to the selected source, when available.
        underlying_name: str
            The name of the underlying asset.
        underlying_price: dict
            A Pandas Series containing the underlying asset's price and performance.

    Examples
    --------
    Loads SPY data from CBOE and display the longest dates expiration chain.

    >>> from openbb_terminal.sdk import openbb
    >>> import pandas as pd
    >>> data = openbb.stocks.options.load_options_chains("SPY")
    >>> chains = pd.DataFrame(data.chains)
    >>> chains[chains["expiration"] == data.expirations[-1]]

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
        return load_nasdaq(symbol)
    if source == "YahooFinance":
        return load_yfinance(symbol)
    if source == "Tradier":
        return load_tradier(symbol)
    if source == "TMX":
        if date != "":
            return load_tmx(symbol, date)
        return load_tmx(symbol)
    if source == "Intrinio":
        if date != "":
            return load_intrinio(symbol, date)
        return load_intrinio(symbol)

    return load_cboe(symbol, pydantic)
