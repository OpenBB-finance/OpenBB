"""Forex SDK Helpers."""
__docformat__ = "numpy"

import pandas as pd
import yfinance as yf

from openbb_terminal.forex import av_model


def quote(symbol: str, source: str = "YahooFinance") -> pd.DataFrame:
    """Get forex quote.

    Parameters
    ----------
    symbol : str
        Forex symbol to get quote for.
    source : str, optional
        Source to get quote from, by default "YahooFinance"

    Returns
    -------
    pd.DataFrame
        DataFrame of quote data.

    Examples
    --------
    >>> from openbb_terminal.sdk import openbb
    >>> EUR_USD_quote = openbb.forex.quote("EURUSD")

    This also supports AlphaVantage and will handle different conventions
    >>> EUR_USD= openbb.forex.quote("EUR/USD", source="AlphaVantage")
    """
    symbol = symbol.replace("/", "").replace("-", "")
    to_symbol = symbol[:3]
    from_symbol = symbol[3:]
    if source == "YahooFinance":
        data = yf.download(f"{symbol}=X", period="1d", interval="1m", progress=False)
        return pd.DataFrame.from_dict(
            {
                "Last Refreshed": data.index[-1].strftime("%Y-%m-%d %H:%M:%S %Z"),
                "Quote": data.Close[-1],
            },
            orient="index",
        )
    if source == "AlphaVantage":
        to_symbol = symbol[:3]
        from_symbol = symbol[3:]
        data = av_model.get_quote(to_symbol, from_symbol)
        return pd.DataFrame.from_dict(data)

    return pd.DataFrame()
